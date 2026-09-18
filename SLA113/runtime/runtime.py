"""CapabilityRuntime — the central runtime that hosts all capability packs.

Responsibilities:
  - Register and manage providers
  - Route capability requests to providers
  - Health check all providers
  - Cache results
  - Collect metrics
  - Manage pack lifecycle
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from SLA113.execution_engine.logging import cache_hit as log_cache_hit
from SLA113.execution_engine.logging import cache_miss as log_cache_miss
from SLA113.execution_engine.logging import provider_select as log_provider_select
from SLA113.execution_engine.logging import request as log_request
from SLA113.execution_engine.provider import (
    ProviderDef,
    ProviderHealth,
    ProviderRouter,
)

from .loader import RuntimeLoader


@dataclass
class RuntimeMetrics:
    provider_id: str
    call_count: int = 0
    total_latency_ms: int = 0
    error_count: int = 0
    total_cost: float = 0.0
    cache_hits: int = 0

    @property
    def avg_latency_ms(self) -> float:
        return self.total_latency_ms / max(self.call_count, 1)

    @property
    def error_rate(self) -> float:
        return self.error_count / max(self.call_count, 1)


class RuntimeCache:
    """Simple TTL-based result cache."""

    def __init__(self, default_ttl: int = 300):
        self._cache: Dict[str, tuple] = {}
        self.default_ttl = default_ttl

    def _key(self, provider_id: str, inputs: tuple) -> str:
        import hashlib
        raw = f"{provider_id}:{repr(inputs)}"
        return hashlib.sha256(raw.encode()).hexdigest()[:32]

    def get(self, provider_id: str, inputs: tuple) -> Optional[Any]:
        key = self._key(provider_id, inputs)
        entry = self._cache.get(key)
        if entry:
            value, expiry = entry
            if time.time() < expiry:
                return value
            del self._cache[key]
        return None

    def set(self, provider_id: str, inputs: tuple, value: Any, ttl: Optional[int] = None):
        key = self._key(provider_id, inputs)
        expiry = time.time() + (ttl or self.default_ttl)
        self._cache[key] = (value, expiry)

    def invalidate(self, provider_id: Optional[str] = None):
        if provider_id:
            self._cache = {
                k: v for k, v in self._cache.items()
                if not k.startswith(f"{provider_id}:")
            }
        else:
            self._cache.clear()


class CapabilityRuntime:
    """Central runtime that hosts all capability packs and routes requests."""

    def __init__(self):
        self.router = ProviderRouter()
        self.loader = RuntimeLoader()
        self.cache = RuntimeCache()
        self.metrics: Dict[str, RuntimeMetrics] = {}
        self._initialized = False

    def initialize(self):
        """Discover, load, and register all capability packs."""
        packs = self.loader.load_all()
        self.loader.register_all(self.router)
        self._initialized = True

    def is_initialized(self) -> bool:
        return self._initialized

    def register_provider(self, provider: ProviderDef, handler: Callable):
        self.router.register(provider, handler)

    def resolve(self, capability: str, preference: Optional[str] = None) -> Optional[ProviderDef]:
        return self.router.select(capability, preference)

    def request(
        self,
        capability: str,
        inputs: Dict[str, Any],
        preference: Optional[str] = None,
        creator_id: str = "system",
        use_cache: bool = True,
    ) -> Any:
        """Execute a capability request through the best available provider.

        Flow:
          1. Select provider (capability → preference → router)
          2. Check cache
          3. Execute with fallback chain
          4. Cache result
          5. Record metrics
        """
        provider = self.router.select(capability, preference)
        if not provider:
            fallbacks = self.router.select_with_fallback(capability)
            if not fallbacks:
                raise RuntimeError(f"No available provider for capability '{capability}'")
            provider = fallbacks[0]

        log_provider_select(capability, provider.id, preference)

        handler = self.router.get_handler(provider.id)
        if not handler:
            raise RuntimeError(f"No handler registered for provider '{provider.id}'")

        cache_key_inputs = tuple(sorted(inputs.items()))
        if use_cache:
            cached = self.cache.get(provider.id, cache_key_inputs)
            if cached is not None:
                self._record_metric(provider.id, cache_hit=True)
                log_cache_hit(provider.id, capability)
                return cached

        log_cache_miss(provider.id, capability)
        start = time.time()
        try:
            result = handler(capability, inputs, provider, creator_id)
            elapsed = int((time.time() - start) * 1000)
            self._record_metric(
                provider.id,
                latency_ms=elapsed,
                cost=provider.cost_per_call,
            )
            log_request(capability, provider.id, "success", elapsed)
            if use_cache:
                self.cache.set(provider.id, cache_key_inputs, result)
            return result
        except Exception as e:
            elapsed = int((time.time() - start) * 1000)
            self._record_metric(
                provider.id,
                latency_ms=elapsed,
                error=True,
            )
            log_request(capability, provider.id, "error", elapsed, str(e))

            fallbacks = self.router.select_with_fallback(capability)
            for fb in fallbacks:
                if fb.id == provider.id:
                    continue
                fb_handler = self.router.get_handler(fb.id)
                if not fb_handler:
                    continue
                try:
                    result = fb_handler(capability, inputs, fb, creator_id)
                    self._record_metric(fb.id, latency_ms=elapsed)
                    log_request(capability, fb.id, "fallback_success", elapsed)
                    return result
                except Exception:
                    continue

            raise RuntimeError(
                f"All providers failed for capability '{capability}'."
                f" Last error: {e}"
            )

    def health(self) -> Dict[str, ProviderHealth]:
        return self.router.health_summary()

    def _record_metric(
        self,
        provider_id: str,
        latency_ms: int = 0,
        cost: float = 0.0,
        error: bool = False,
        cache_hit: bool = False,
    ):
        if provider_id not in self.metrics:
            self.metrics[provider_id] = RuntimeMetrics(provider_id=provider_id)
        m = self.metrics[provider_id]
        m.call_count += 1
        m.total_latency_ms += latency_ms
        m.total_cost += cost
        if error:
            m.error_count += 1
        if cache_hit:
            m.cache_hits += 1

    def get_metrics_report(self) -> Dict[str, dict]:
        return {
            pid: {
                "call_count": m.call_count,
                "avg_latency_ms": round(m.avg_latency_ms, 1),
                "error_rate": round(m.error_rate, 3),
                "total_cost": round(m.total_cost, 4),
                "cache_hits": m.cache_hits,
            }
            for pid, m in self.metrics.items()
        }
