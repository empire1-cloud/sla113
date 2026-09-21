"""Deployment descriptor. Describes a static-CDN deploy; does not perform one."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict


def build_deployment_artifact(spec: Any, root: Path, build: Dict[str, Any]) -> Dict[str, Any]:
    descriptor = {
        "engine": "SLA113 Genesis Engine", "game": spec.name, "platform": spec.target_platform,
        "artifact": build.get("web_zip"), "artifact_sha256": build.get("sha256"),
        "deployment_mode": "static-cdn", "entrypoint": "web/index.html", "cache_policy": "immutable-assets",
        "health_path": "/index.html", "credentials_required": True,
        "deployed": False, "status": "descriptor_ready",
    }
    path = root / "deployment.json"
    path.write_text(json.dumps(descriptor, indent=2), encoding="utf-8")
    return {"type": "deployment_descriptor", "path": "deployment.json", "status": descriptor["status"],
            "deployed": False, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
