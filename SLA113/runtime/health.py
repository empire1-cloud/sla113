"""Health monitoring for all registered providers."""

from __future__ import annotations

from typing import Dict, List, Optional

from SLA113.execution_engine.provider import ProviderHealth, ProviderRouter


class HealthMonitor:
    """Periodic health checker for all providers."""

    def __init__(self, router: ProviderRouter, interval_seconds: int = 60):
        self.router = router
        self.interval = interval_seconds

    def check_all(self) -> Dict[str, ProviderHealth]:
        return self.router.health_summary()

    def check_capability(self, capability: str) -> List[ProviderHealth]:
        results = []
        for pid, provider in self.router.all_providers().items():
            if provider.config.get("capability") == capability:
                results.append(self.router.check_health(pid))
        return results

    def summary(self) -> Dict[str, int]:
        health = self.check_all()
        return {
            "total": len(health),
            "healthy": sum(1 for h in health.values() if h.healthy),
            "unhealthy": sum(1 for h in health.values() if not h.healthy),
        }
