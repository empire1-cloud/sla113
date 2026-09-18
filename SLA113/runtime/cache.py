"""Cache layer for capability runtime results."""

from __future__ import annotations

import time
from typing import Any, Dict, Optional


class CapabilityCache:
    """TTL-based cache for capability execution results.

    Supports per-provider and global invalidation,
    and configurable TTL per capability type.
    """

    def __init__(self, default_ttl: int = 300):
        self._store: Dict[str, tuple] = {}
        self._ttl_overrides: Dict[str, int] = {}
        self.default_ttl = default_ttl

    def set_ttl(self, capability: str, ttl_seconds: int):
        self._ttl_overrides[capability] = ttl_seconds

    def _key(self, provider_id: str, inputs: tuple) -> str:
        import hashlib
        raw = f"{provider_id}:{repr(inputs)}"
        return hashlib.sha256(raw.encode()).hexdigest()[:32]

    def _ttl(self, capability: str) -> int:
        return self._ttl_overrides.get(capability, self.default_ttl)

    def get(self, provider_id: str, inputs: tuple) -> Optional[Any]:
        key = self._key(provider_id, inputs)
        entry = self._store.get(key)
        if entry:
            value, expiry = entry
            if time.time() < expiry:
                return value
            del self._store[key]
        return None

    def set(self, provider_id: str, inputs: tuple, value: Any, ttl: Optional[int] = None):
        key = self._key(provider_id, inputs)
        expiry = time.time() + (ttl or self.default_ttl)
        self._store[key] = (value, expiry)

    def invalidate(self, provider_id: Optional[str] = None):
        if provider_id:
            self._store = {
                k: v for k, v in self._store.items()
                if not k.startswith(f"{provider_id}:")
            }
        else:
            self._store.clear()

    def size(self) -> int:
        return len(self._store)

    def clear_expired(self) -> int:
        now = time.time()
        expired = [k for k, v in self._store.items() if v[1] < now]
        for k in expired:
            del self._store[k]
        return len(expired)
