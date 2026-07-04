"""
tenant_engine.py
SLA113 Arcade — Tenant Engine
Maps tenant_id to: governance profile, regulatory profile, engine set, revenue routing.

All values derived from SLA113_BUILD_SPEC.yaml tenants section.
This engine is the single entry point for resolving a tenant's full context
before any arcade game engine is dispatched.
"""

from typing import Optional

# Tenant registry — statically defined from SLA113_BUILD_SPEC.yaml
TENANT_REGISTRY = {}

# Ensure display_name is used consistently
for tid, t in TENANT_REGISTRY.items():
    if "display_name" not in t and "identity" in t:
        t["display_name"] = t["identity"].get("tagline", tid)


# Stripe plan tier → allowed tenant types
STRIPE_PLAN_ENGINE_ACCESS = {
    "operator":   ["fishing_engine_v2", "slots_engine_v1"],
    "factory":    ["fishing_engine_v2", "slots_engine_v1", "keno_engine_v1", "payout_engine", "machine_engine"],
    "enterprise": ["fishing_engine_v2", "slots_engine_v1", "keno_engine_v1", "payout_engine",
                   "machine_engine", "tenant_engine", "canon_layer_sgv_aztec"],
}


class TenantEngine:
    ENGINE_ID = "tenant_engine"
    ENGINE_TYPE = "arcade"
    VERSION = "1.0.0"

    def resolve(self, tenant_id: str) -> dict:
        """
        Resolve full tenant context for arcade game dispatch.
        Returns tenant config or raises ValueError for unknown tenants.
        """
        tenant = TENANT_REGISTRY.get(tenant_id)
        if not tenant:
            raise ValueError(f"Unknown tenant: {tenant_id}")
        return {"tenant_id": tenant_id, **tenant}

    def check_machine_access(self, tenant_id: str, machine_type: str) -> bool:
        """Check if tenant is allowed to use a machine type."""
        tenant = TENANT_REGISTRY.get(tenant_id)
        if not tenant:
            return False
        return machine_type in tenant.get("allowed_machine_types", [])

    def check_stripe_entitlement(
        self,
        tenant_id: str,
        engine_id: str,
        subscription_plan: Optional[str] = None,
    ) -> bool:
        """
        Check if tenant's Stripe subscription plan grants access to the engine.
        subscription_plan: "operator" | "factory" | "enterprise" (from Stripe metadata)
        """
        tenant = TENANT_REGISTRY.get(tenant_id)
        if not tenant:
            return False

        # If no plan provided, use the tenant's required minimum plan
        plan = subscription_plan or tenant.get("stripe_plan_required", "operator")

        allowed_engines = STRIPE_PLAN_ENGINE_ACCESS.get(plan, [])
        return engine_id in allowed_engines

    def get_governance(self, tenant_id: str) -> dict:
        """Return governance rules for a tenant (session limits, loss limits, age gate)."""
        tenant = TENANT_REGISTRY.get(tenant_id)
        if not tenant:
            return {}
        return tenant.get("governance", {})

    def get_revenue_routing(self, tenant_id: str) -> dict:
        """Return revenue routing config for a tenant."""
        tenant = TENANT_REGISTRY.get(tenant_id)
        if not tenant:
            return {}
        return tenant.get("revenue_routing", {})

    def list_tenants(self) -> list:
        """List all registered tenants with their basic metadata."""
        return [
            {
                "tenant_id": tid,
                "display_name": t.get("display_name"),
                "regulatory_profile": t.get("regulatory_profile"),
                "region": t.get("region"),
                "allowed_machine_types": t.get("allowed_machine_types"),
                "stripe_plan_required": t.get("stripe_plan_required"),
            }
            for tid, t in TENANT_REGISTRY.items()
        ]
