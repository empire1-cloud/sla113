"""Inspectable math-verification artifact. Engineering evidence, not certification."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict


def build_verification_artifact(spec: Any, verification: Dict[str, Any], manifest: Dict[str, Any], root: Path) -> Dict[str, Any]:
    payload = {
        "engine": "SLA113 Genesis Engine",
        "artifact_type": "math_verification",
        "regulatory_status": "engineering verification only — not a regulatory certification",
        "spec": spec.model_dump(),
        "verification": verification,
        "manifest_digest": hashlib.sha256(json.dumps(manifest, sort_keys=True, default=str).encode()).hexdigest(),
    }
    path = root / "verification.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return {"type": "verification", "path": "verification.json", "status": verification["verification_status"],
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
