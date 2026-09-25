"""End-to-end Genesis pipeline: spec -> math -> verify -> assets -> compose -> package -> descriptor."""
from __future__ import annotations

import os
import re
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from .assets import build_assets
from .audio import build_audio_manifest
from .build import package
from .compliance import build_verification_artifact
from .composer import compose_web
from .deploy import build_deployment_artifact
from .logic import verify_math

STAGES = ["SPECIFIED", "CALCULATED", "VERIFIED", "GENERATED", "COMPOSED", "PACKAGED", "DESCRIBED"]
JOB_ID_RE = re.compile(r"^genesis_[0-9a-f]{32}$")


def workspace_root() -> Path:
    return Path(os.environ.get("SLA113_GENESIS_WORKDIR", Path(tempfile.gettempdir()) / "sla113_genesis"))


def job_dir(job_id: str) -> Optional[Path]:
    """Resolve a job workspace, refusing anything that is not a well-formed job id."""
    if not JOB_ID_RE.match(job_id or ""):
        return None
    path = workspace_root() / job_id
    return path if path.is_dir() else None


class GenesisPipeline:
    def run(self, spec: Any, include_audio: bool = True, include_vision: bool = True, include_build: bool = True) -> Dict[str, Any]:
        job_id = f"genesis_{uuid.uuid4().hex}"
        root = workspace_root() / job_id
        root.mkdir(parents=True, exist_ok=True)

        verification = verify_math(spec)
        assets = build_assets(spec, root) if include_vision else []
        audio = build_audio_manifest(spec, root) if include_audio else []
        manifest = {"job_id": job_id, "spec": spec.model_dump(), "assets": assets, "audio": audio, "logic": verification}
        composed = compose_web(spec, verification, assets, audio, root)
        verification_artifact = build_verification_artifact(spec, verification, manifest, root)
        built = package(spec, root) if include_build else {"status": "skipped"}

        artifacts = [verification_artifact, {"type": "playable", "path": composed["entrypoint"], "status": composed["status"]}]
        stages = STAGES[:5]
        if built.get("web_zip"):
            artifacts.append({"type": "build", "path": built["web_zip"], "status": built["status"], "sha256": built["sha256"]})
            artifacts.append(build_deployment_artifact(spec, root, built))
            stages = STAGES

        return {
            "job_id": job_id,
            "status": "complete",
            "stages_completed": stages,
            "manifest": {**manifest, "composer": composed},
            "verification": verification,
            "artifacts": artifacts,
            "build": built,
        }
