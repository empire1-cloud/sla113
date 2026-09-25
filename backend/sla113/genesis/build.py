"""Package the portable web build as a zip. Native targets are detected, not faked."""
from __future__ import annotations

import hashlib
import re
import shutil
import zipfile
from pathlib import Path
from typing import Any, Dict


def package(spec: Any, root: Path) -> Dict[str, Any]:
    dist = root / "dist"
    dist.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "_", spec.name.lower()).strip("_") or "genesis_game"
    archive = dist / f"{slug}_web.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted((root / "web").rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(root))
        if (root / "verification.json").exists():
            z.write(root / "verification.json", "verification.json")
    return {
        "status": "packaged",
        "web_zip": str(archive.relative_to(root)),
        "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
        "toolchain": {"web": True, "android_gradle": shutil.which("gradle") is not None, "cocos2dx": shutil.which("cocos") is not None},
        "notes": "Only the web build is produced. APK/Cocos builds need their native toolchains and are not attempted.",
    }
