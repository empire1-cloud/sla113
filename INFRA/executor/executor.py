"""Best-effort subprocess sandbox for forged artifacts.

WARNING: This is NOT a kernel-isolated sandbox. We have no Docker/firejail/nsjail
in this preview container, so we rely on:
  - tempdir-only writes (RLIMIT_FSIZE + cwd in a fresh /tmp/cv-exec-*)
  - RLIMIT_AS (512MB), RLIMIT_CPU (30s), RLIMIT_NPROC (32)
  - wallclock timeout via asyncio.wait_for
  - auth-gating (artifact owner only)
  - tier-based rate limiting

A motivated attacker CAN escape this. Treat executions as if the user trusts
their own forged code. Do not expose to anonymous users.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import resource
import shutil
import signal
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Awaitable, Callable, List, Optional, Tuple

# ----- Resource caps applied via preexec_fn in each child -----
MEM_BYTES = 512 * 1024 * 1024
CPU_SECONDS = 30
FSIZE_BYTES = 50 * 1024 * 1024
NPROC = 64

DEPS_INSTALL_TIMEOUT = 90  # wall-clock seconds
RUN_TIMEOUT = 30  # wall-clock seconds for the actual run

PY_ENTRY_CANDIDATES = ["main.py", "app.py", "run.py", "__main__.py"]
NODE_ENTRY_CANDIDATES = ["index.js", "app.js", "main.js", "server.js"]


def _preexec() -> None:
    """Set rlimits in the child before exec."""
    try:
        resource.setrlimit(resource.RLIMIT_AS, (MEM_BYTES, MEM_BYTES))
        resource.setrlimit(resource.RLIMIT_CPU, (CPU_SECONDS, CPU_SECONDS))
        resource.setrlimit(resource.RLIMIT_FSIZE, (FSIZE_BYTES, FSIZE_BYTES))
        resource.setrlimit(resource.RLIMIT_NPROC, (NPROC, NPROC))
    except Exception:
        # If the kernel rejects a limit, still proceed — better partial caps
        # than failing the whole run.
        pass
    # Detach from controlling tty so child signals don't hit the parent.
    os.setsid()


@dataclass
class ExecutionPlan:
    runtime: str  # "python" | "node" | "unsupported"
    entry_path: Optional[str] = None
    deps_cmd: Optional[List[str]] = None
    run_cmd: Optional[List[str]] = None
    env: dict = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)


def detect_plan(files: List[dict]) -> ExecutionPlan:
    """Pick a runtime + commands from the artifact's files. Pure function."""
    by_path = {f["path"]: f["content"] for f in files}
    paths = set(by_path.keys())

    # ---- Node ----
    if "package.json" in paths:
        try:
            pkg = json.loads(by_path["package.json"])
        except json.JSONDecodeError:
            pkg = {}
        scripts = pkg.get("scripts") or {}
        main = pkg.get("main") or "index.js"
        deps_cmd = ["npm", "install", "--no-audit", "--no-fund", "--silent"]
        if "start" in scripts:
            return ExecutionPlan(
                runtime="node",
                entry_path="package.json (npm start)",
                deps_cmd=deps_cmd,
                run_cmd=["npm", "start", "--silent"],
                notes=["Detected package.json with start script"],
            )
        if main in paths:
            return ExecutionPlan(
                runtime="node",
                entry_path=main,
                deps_cmd=deps_cmd,
                run_cmd=["node", main],
                notes=[f"Detected package.json main={main}"],
            )

    for cand in NODE_ENTRY_CANDIDATES:
        if cand in paths:
            return ExecutionPlan(
                runtime="node",
                entry_path=cand,
                deps_cmd=None,
                run_cmd=["node", cand],
                notes=[f"Found {cand}; no package.json"],
            )

    # ---- Python ----
    has_reqs = "requirements.txt" in paths
    for cand in PY_ENTRY_CANDIDATES:
        if cand in paths:
            deps_cmd: Optional[List[str]] = None
            env: dict = {}
            if has_reqs:
                deps_cmd = ["pip", "install", "--quiet", "--no-cache-dir", "--target", "_deps", "-r", "requirements.txt"]
                env = {"PYTHONPATH": "_deps"}
            return ExecutionPlan(
                runtime="python",
                entry_path=cand,
                deps_cmd=deps_cmd,
                run_cmd=["python3", cand],
                env=env,
                notes=[f"Found {cand}", *(["With requirements.txt"] if has_reqs else [])],
            )

    return ExecutionPlan(
        runtime="unsupported",
        notes=[
            "No supported entry point found.",
            "Looked for: main.py / app.py / run.py / __main__.py / index.js / app.js / package.json",
        ],
    )


def _safe_relpath(path: str) -> Optional[str]:
    """Reject paths that try to escape the workspace."""
    p = Path(path)
    if p.is_absolute():
        return None
    parts = p.parts
    if any(part == ".." for part in parts):
        return None
    return str(p)


def write_workspace(files: List[dict], root: Path) -> Tuple[int, List[str]]:
    """Write files to root, refusing path traversal. Returns (count, skipped)."""
    written = 0
    skipped: List[str] = []
    for f in files:
        rel = _safe_relpath(f.get("path", ""))
        if not rel:
            skipped.append(f.get("path", "<empty>"))
            continue
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f.get("content", ""), encoding="utf-8")
        written += 1
    return written, skipped


LogCallback = Callable[[str, str], Awaitable[None]]  # (stream, line)


async def _stream_proc(
    proc: asyncio.subprocess.Process, on_log: LogCallback
) -> None:
    async def pump(stream, label):
        if stream is None:
            return
        while True:
            line = await stream.readline()
            if not line:
                break
            text = line.decode("utf-8", errors="replace").rstrip("\n\r")
            # Truncate insanely long lines to keep Mongo docs bounded.
            if len(text) > 2000:
                text = text[:2000] + " …[truncated]"
            await on_log(label, text)

    await asyncio.gather(pump(proc.stdout, "stdout"), pump(proc.stderr, "stderr"))


async def _run_step(
    cmd: List[str],
    cwd: Path,
    on_log: LogCallback,
    timeout: int,
    env_overrides: Optional[dict] = None,
) -> int:
    """Run one subprocess; stream logs; enforce timeout."""
    base_env = os.environ.copy()
    base_env.update(env_overrides or {})
    # Strip anything sensitive from leaking into user code.
    for k in ("EMERGENT_LLM_KEY", "JWT_SECRET", "STRIPE_API_KEY", "STRIPE_SECRET_KEY", "MONGO_URL"):
        base_env.pop(k, None)

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=str(cwd),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        preexec_fn=_preexec,
        env=base_env,
    )
    try:
        await asyncio.wait_for(
            asyncio.gather(_stream_proc(proc, on_log), proc.wait()),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass
        await on_log("system", f"[timeout] killed after {timeout}s")
        await proc.wait()
        return 124  # standard timeout exit code
    return proc.returncode if proc.returncode is not None else -1


@dataclass
class ExecutionOutcome:
    runtime: str
    entry_path: Optional[str]
    deps_exit: Optional[int]
    run_exit: Optional[int]
    duration_ms: int
    final_status: str  # "ok" | "deps_failed" | "run_failed" | "timeout" | "unsupported"


async def run_artifact(
    files: List[dict],
    on_log: LogCallback,
    cancel_event: Optional[asyncio.Event] = None,
) -> ExecutionOutcome:
    """End-to-end: detect, install deps, run, capture. Public entry point."""
    plan = detect_plan(files)
    started = time.monotonic()

    if plan.runtime == "unsupported":
        for n in plan.notes:
            await on_log("system", n)
        return ExecutionOutcome(
            runtime="unsupported",
            entry_path=None,
            deps_exit=None,
            run_exit=None,
            duration_ms=int((time.monotonic() - started) * 1000),
            final_status="unsupported",
        )

    workdir = Path(tempfile.mkdtemp(prefix="cv-exec-"))
    try:
        await on_log("system", f"[workspace] {workdir}")
        count, skipped = write_workspace(files, workdir)
        await on_log("system", f"[workspace] wrote {count} files" + (f" · skipped {skipped}" if skipped else ""))
        for n in plan.notes:
            await on_log("system", f"[plan] {n}")

        deps_exit: Optional[int] = None
        if plan.deps_cmd:
            await on_log("system", f"[install] {' '.join(plan.deps_cmd)}")
            if cancel_event and cancel_event.is_set():
                return ExecutionOutcome(plan.runtime, plan.entry_path, None, None,
                                        int((time.monotonic() - started) * 1000), "canceled")
            deps_exit = await _run_step(
                plan.deps_cmd, workdir, on_log, DEPS_INSTALL_TIMEOUT, plan.env
            )
            await on_log("system", f"[install] exit={deps_exit}")
            if deps_exit != 0:
                return ExecutionOutcome(
                    runtime=plan.runtime,
                    entry_path=plan.entry_path,
                    deps_exit=deps_exit,
                    run_exit=None,
                    duration_ms=int((time.monotonic() - started) * 1000),
                    final_status="deps_failed",
                )

        if cancel_event and cancel_event.is_set():
            return ExecutionOutcome(plan.runtime, plan.entry_path, deps_exit, None,
                                    int((time.monotonic() - started) * 1000), "canceled")

        await on_log("system", f"[run] {' '.join(plan.run_cmd or [])}")
        run_exit = await _run_step(plan.run_cmd or [], workdir, on_log, RUN_TIMEOUT, plan.env)
        await on_log("system", f"[run] exit={run_exit}")
        status = (
            "timeout" if run_exit == 124
            else "ok" if run_exit == 0
            else "run_failed"
        )
        return ExecutionOutcome(
            runtime=plan.runtime,
            entry_path=plan.entry_path,
            deps_exit=deps_exit,
            run_exit=run_exit,
            duration_ms=int((time.monotonic() - started) * 1000),
            final_status=status,
        )
    finally:
        # Clean up the workspace regardless of outcome.
        try:
            shutil.rmtree(workdir, ignore_errors=True)
        except Exception:
            pass
