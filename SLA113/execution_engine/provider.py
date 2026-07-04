"""Provider abstraction layer.

The execution chain:
  Workflow → Capability → Service → Provider

A Provider is a concrete implementation — Vertex AI, Local GPU, OpenAI, etc.
A Service is a logical capability with configuration and fallback order.
The Provider Router selects the best available provider at runtime.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


class ProviderType:
    CLOUD_API = "cloud_api"
    LOCAL_MODEL = "local_model"
    LOCAL_DSP = "local_dsp"
    MCP = "mcp"
    CACHED = "cached"
    FALLBACK = "fallback"


@dataclass
class ProviderDef:
    """A concrete implementation that can fulfill a service request."""
    id: str
    name: str
    provider_type: str
    lifecycle: str
    priority: int
    cost_per_call: float = 0.0
    latency_ms: int = 0
    config: Dict[str, Any] = field(default_factory=dict)
    health_check: Optional[Callable[[], bool]] = None


@dataclass
class ProviderHealth:
    provider_id: str
    healthy: bool
    latency_ms: int
    error: Optional[str] = None


class ProviderRouter:
    """Routes capability requests to the best available provider.

    Selection strategy:
      1. Filter by capability match
      2. Filter by lifecycle == 'active'
      3. Filter healthy providers only
      4. Sort by priority (highest first)
      5. Within same priority, prefer lower latency
      6. Return the best match
    """

    def __init__(self):
        self._providers: Dict[str, ProviderDef] = {}
        self._handlers: Dict[str, Callable] = {}
        self._capability_map: Dict[str, List[str]] = {}
        self._health_cache: Dict[str, ProviderHealth] = {}

    def register(self, provider: ProviderDef, handler: Callable):
        self._providers[provider.id] = provider
        self._handlers[provider.id] = handler
        cap = provider.config.get("capability", "unknown")
        if cap not in self._capability_map:
            self._capability_map[cap] = []
        self._capability_map[cap].append(provider.id)

    def register_handler(self, provider_id: str, handler: Callable):
        if provider_id in self._providers:
            self._handlers[provider_id] = handler

    def get_handler(self, provider_id: str) -> Optional[Callable]:
        return self._handlers.get(provider_id)

    def get_provider(self, provider_id: str) -> Optional[ProviderDef]:
        return self._providers.get(provider_id)

    def select(self, capability: str, preference: Optional[str] = None) -> Optional[ProviderDef]:
        if preference and preference in self._providers:
            p = self._providers[preference]
            if p.lifecycle == "active" and self._is_healthy(p.id):
                return p

        candidates = []
        for pid in self._capability_map.get(capability, []):
            p = self._providers.get(pid)
            if p and p.lifecycle == "active" and self._is_healthy(pid):
                candidates.append(p)

        candidates.sort(key=lambda p: (-p.priority, p.latency_ms, p.cost_per_call))
        return candidates[0] if candidates else None

    def select_with_fallback(self, capability: str) -> List[ProviderDef]:
        """Returns all viable providers in priority order for fallback chaining."""
        candidates = []
        for pid in self._capability_map.get(capability, []):
            p = self._providers.get(pid)
            if p and p.lifecycle == "active":
                health = self.check_health(pid)
                candidates.append((p, health.healthy if health else False))

        candidates.sort(key=lambda x: (-x[0].priority, x[0].latency_ms, x[0].cost_per_call))
        return [c[0] for c in candidates]

    def check_health(self, provider_id: str) -> ProviderHealth:
        import time
        p = self._providers.get(provider_id)
        if not p:
            return ProviderHealth(provider_id=provider_id, healthy=False, latency_ms=0, error="Unknown provider")

        if provider_id in self._health_cache:
            cached = self._health_cache[provider_id]
            if time.time() - getattr(cached, "_cached_at", 0) < 30:
                return cached

        start = time.time()
        try:
            if p.health_check:
                healthy = p.health_check()
            else:
                handler = self._handlers.get(provider_id)
                healthy = handler is not None
            elapsed = int((time.time() - start) * 1000)
            result = ProviderHealth(provider_id=provider_id, healthy=healthy, latency_ms=elapsed)
        except Exception as e:
            elapsed = int((time.time() - start) * 1000)
            result = ProviderHealth(provider_id=provider_id, healthy=False, latency_ms=elapsed, error=str(e))

        result._cached_at = time.time()
        self._health_cache[provider_id] = result
        return result

    def _is_healthy(self, provider_id: str) -> bool:
        health = self.check_health(provider_id)
        return health.healthy

    def all_providers(self) -> Dict[str, ProviderDef]:
        return dict(self._providers)

    def health_summary(self) -> Dict[str, ProviderHealth]:
        return {pid: self.check_health(pid) for pid in self._providers}
