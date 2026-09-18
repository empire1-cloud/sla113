"""Last30Days integration bridge — runs research via subprocess, parses output.

Wraps the last30days-skill CLI (npx or pip) and converts results
into structured Signal objects.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional

from sources import Signal


class Last30DaysBridge:
    """Bridge to the last30days-skill research engine.

    Auto-discovers installation: pip module → source path → npx global.
    """

    def __init__(self):
        self._binary: Optional[str] = None
        self._discovered = False

    def _discover(self) -> Optional[str]:
        if self._discovered:
            return self._binary

        # Check pip module
        try:
            r = subprocess.run(
                [sys.executable, "-m", "last30days", "--version"],
                capture_output=True, text=True, timeout=10,
            )
            if r.returncode == 0:
                self._binary = f"{sys.executable} -m last30days"
                self._discovered = True
                return self._binary
        except Exception:
            pass

        # Check source path
        for src in [
            Path.home() / "last30days-skill",
            Path.home() / "projects" / "last30days-skill",
        ]:
            if (src / "last30days" / "__init__.py").exists():
                self._binary = f"PYTHONPATH={src} {sys.executable} -m last30days"
                self._discovered = True
                return self._binary

        # Check npx
        if shutil.which("npx"):
            r = subprocess.run(
                ["npx", "last30days", "--version"],
                capture_output=True, text=True, timeout=15,
            )
            if r.returncode == 0:
                self._binary = "npx last30days"
                self._discovered = True
                return self._binary

        self._discovered = True
        return None

    def is_available(self) -> bool:
        return self._discover() is not None

    def research(
        self,
        topic: str,
        days: int = 30,
        sources: Optional[str] = None,
        max_signals: int = 50,
    ) -> Dict:
        """Run Last30Days research and return structured results."""
        binary = self._discover()
        if not binary:
            return {"success": False, "error": "Last30Days not installed"}

        cmd = f"{binary} research \"{topic}\" --days {days} --max-results {max_signals}"
        if sources:
            cmd += f" --sources {sources}"

        try:
            r = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=120,
            )
            if r.returncode != 0:
                return {
                    "success": False,
                    "error": r.stderr[:1000] or f"Exit code {r.returncode}",
                    "stdout": r.stdout[:2000],
                }

            # Try to parse JSON output
            try:
                data = json.loads(r.stdout)
            except json.JSONDecodeError:
                data = {"raw_output": r.stdout[:5000]}

            # Convert to Signal objects
            signals = []
            for item in data.get("results", data.get("signals", [])):
                signals.append(Signal(
                    id=item.get("id", f"sig_{int(time.time() * 1000)}"),
                    source=item.get("source", "last30days"),
                    title=item.get("title", item.get("text", "Unknown")),
                    url=item.get("url", ""),
                    snippet=item.get("snippet", item.get("summary", ""))[:500],
                    published_at=item.get("published_at", item.get("date", "")),
                    collected_at=time.time(),
                    relevance_score=item.get("relevance", item.get("score", 1.0)),
                    sentiment=item.get("sentiment"),
                    tags=item.get("tags", []),
                ))

            return {
                "success": True,
                "topic": topic,
                "days": days,
                "signal_count": len(signals),
                "signals": signals,
                "raw_output": r.stdout[:5000],
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Research timed out (120s)"}
        except Exception as e:
            return {"success": False, "error": str(e)}


# Need sys import
import sys
