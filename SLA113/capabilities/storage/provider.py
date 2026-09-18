"""Storage Pack — Universal file and object storage.

Every universe stores and retrieves data the same way:
    storage = StorageProvider(runtime)
    url = storage.store("audio/track.wav", wav_data)
    data = storage.retrieve(url)
    signed = storage.presign(url, expiry=3600)
"""

from __future__ import annotations

import hashlib
import io
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import quote

from SLA113.runtime import CapabilityRuntime
from SLA113.execution_engine.provider import ProviderDef, ProviderType


class StorageProvider:
    """Universal storage provider. Routes through the Runtime.

    Example:
        storage = StorageProvider()
        storage.register_providers(runtime)
        url = storage.store("audio/track.wav", wav_bytes)
        data = storage.retrieve(url)
    """

    CAPABILITY = "storage"

    def __init__(self, runtime: Optional[CapabilityRuntime] = None, base_path: str = "/tmp/sla113/storage"):
        self.runtime = runtime or CapabilityRuntime()
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def register_providers(self, runtime: Optional[CapabilityRuntime] = None):
        if runtime:
            self.runtime = runtime

        self.runtime.register_provider(
            ProviderDef(id="storage-local", name="Local File Storage",
                         provider_type=ProviderType.LOCAL_DSP,
                         lifecycle="active", priority=95, cost_per_call=0.0, latency_ms=10,
                         config={"capability": "storage", "base_path": str(self.base_path)}),
            self._handle_request,
        )
        self.runtime.register_provider(
            ProviderDef(id="storage-gcs", name="Google Cloud Storage",
                         provider_type=ProviderType.CLOUD_API,
                         lifecycle="development", priority=30, cost_per_call=0.0, latency_ms=200,
                         config={"capability": "storage", "bucket": "lyrica3-audio-output"}),
            self._handle_request,
        )

    def _handle_request(self, capability: str, inputs: Dict[str, Any],
                        provider: ProviderDef, creator_id: str) -> Dict[str, Any]:
        action = inputs.get("action", "")
        if action == "store":
            return self._store(inputs, provider)
        elif action == "retrieve":
            return self._retrieve(inputs, provider)
        elif action == "stream":
            return self._stream(inputs, provider)
        elif action == "presign":
            return self._presign(inputs, provider)
        elif action == "archive":
            return self._archive(inputs)
        elif action == "delete":
            return self._delete(inputs)
        elif action == "list":
            return self._list(inputs)
        elif action == "exists":
            return self._exists(inputs)
        raise ValueError(f"Unknown storage action: {action}")

    def _resolve_path(self, storage_path: str) -> Path:
        return self.base_path / storage_path.lstrip("/")

    def _store(self, inputs: Dict[str, Any], provider: ProviderDef) -> Dict[str, Any]:
        path = inputs.get("path", "")
        data = inputs.get("data", b"")
        content_type = inputs.get("content_type", "application/octet-stream")

        full_path = self._resolve_path(path)
        full_path.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(data, str):
            data = data.encode("utf-8")

        full_path.write_bytes(data)

        checksum = hashlib.sha256(data).hexdigest()[:16]

        return {
            "url": f"storage://local/{path}",
            "path": str(full_path),
            "size_bytes": len(data),
            "content_type": content_type,
            "checksum": checksum,
            "stored_at": datetime.now(timezone.utc).isoformat(),
        }

    def _retrieve(self, inputs: Dict[str, Any], provider: ProviderDef) -> Dict[str, Any]:
        path = inputs.get("path", "")
        full_path = self._resolve_path(path)

        if not full_path.exists():
            return {"found": False, "error": f"Path not found: {path}"}

        data = full_path.read_bytes()
        return {
            "found": True,
            "data": data,
            "size_bytes": len(data),
            "path": str(full_path),
        }

    def _stream(self, inputs: Dict[str, Any], provider: ProviderDef) -> Dict[str, Any]:
        path = inputs.get("path", "")
        offset = inputs.get("offset", 0)
        length = inputs.get("length", None)

        full_path = self._resolve_path(path)
        if not full_path.exists():
            return {"found": False, "error": f"Path not found: {path}"}

        with open(full_path, "rb") as f:
            f.seek(offset)
            data = f.read(length) if length else f.read()

        return {
            "found": True,
            "data": data,
            "offset": offset,
            "size_bytes": len(data),
            "total_size": full_path.stat().st_size,
        }

    def _presign(self, inputs: Dict[str, Any], provider: ProviderDef) -> Dict[str, Any]:
        path = inputs.get("path", "")
        expiry = inputs.get("expiry_seconds", 3600)

        full_path = self._resolve_path(path)
        if not full_path.exists():
            return {"found": False, "error": f"Path not found: {path}"}

        raw = f"{path}:{int(time.time()) + expiry}:sla113-storage"
        signature = hashlib.sha256(raw.encode()).hexdigest()[:12]

        return {
            "found": True,
            "url": f"storage://local/{path}?signature={signature}&expiry={int(time.time()) + expiry}",
            "expires_at": int(time.time()) + expiry,
            "signature": signature,
        }

    def _archive(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        path = inputs.get("path", "")
        full_path = self._resolve_path(path)
        if not full_path.exists():
            return {"found": False, "error": f"Path not found: {path}"}

        archive_dir = self.base_path / ".archive"
        archive_dir.mkdir(parents=True, exist_ok=True)

        archive_name = f"{datetime.now(timezone.utc).strftime('%Y%m%d')}_{full_path.name}"
        archive_path = archive_dir / archive_name

        full_path.rename(archive_path)
        return {"archived": True, "archive_path": str(archive_path), "original_path": path}

    def _delete(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        path = inputs.get("path", "")
        full_path = self._resolve_path(path)
        if not full_path.exists():
            return {"found": False, "error": f"Path not found: {path}"}
        full_path.unlink()
        return {"deleted": True, "path": path}

    def _list(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        prefix = inputs.get("prefix", "")
        dir_path = self._resolve_path(prefix)
        if not dir_path.exists() or not dir_path.is_dir():
            return {"found": False, "files": []}

        files = []
        for f in dir_path.iterdir():
            if f.is_file():
                files.append({
                    "name": f.name,
                    "path": str(f.relative_to(self.base_path)),
                    "size_bytes": f.stat().st_size,
                    "modified_at": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                })
        return {"found": True, "prefix": prefix, "files": files, "total": len(files)}

    def _exists(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        path = inputs.get("path", "")
        full_path = self._resolve_path(path)
        return {"exists": full_path.exists(), "path": path}

    # Public API — bypass runtime cache (storage is stateful)
    def store(self, path: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        result = self.runtime.request(self.CAPABILITY, {
            "action": "store", "path": path, "data": data, "content_type": content_type,
        }, use_cache=False)
        return result.get("url", "")

    def retrieve(self, url: str) -> Optional[bytes]:
        path = url.replace("storage://local/", "", 1) if url.startswith("storage://") else url
        result = self.runtime.request(self.CAPABILITY, {"action": "retrieve", "path": path}, use_cache=False)
        return result.get("data") if result.get("found") else None

    def presign(self, path: str, expiry: int = 3600) -> Optional[str]:
        result = self.runtime.request(self.CAPABILITY, {
            "action": "presign", "path": path, "expiry_seconds": expiry,
        }, use_cache=False)
        return result.get("url") if result.get("found") else None

    def exists(self, path: str) -> bool:
        result = self.runtime.request(self.CAPABILITY, {"action": "exists", "path": path}, use_cache=False)
        return result.get("exists", False)

    def list_files(self, prefix: str = "") -> list:
        result = self.runtime.request(self.CAPABILITY, {"action": "list", "prefix": prefix}, use_cache=False)
        return result.get("files", [])

    def delete(self, path: str) -> bool:
        result = self.runtime.request(self.CAPABILITY, {"action": "delete", "path": path}, use_cache=False)
        return result.get("deleted", False)
