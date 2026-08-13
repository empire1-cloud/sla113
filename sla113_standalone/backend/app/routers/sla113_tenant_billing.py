"""SLA113 Tenant Billing — Tiered plan management per tenant.

Integrates with Stripe for subscription management. Falls back to
mock billing when STRIPE_SECRET_KEY is not configured (dev mode).
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
import logging
import os

from app.core.database import get_database
from app.core.config import get_settings
from app.core.tenant_context import get_current_tenant
from app.models.schemas import TenantPlan

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/billing", tags=["sla113-tenant-billing"])

PLAN_PRICING = {
    TenantPlan.FREE: {"monthly": 0, "name": "Free", "projects": 5, "builds": 10},
    TenantPlan.STARTER: {"monthly": 99, "name": "Starter", "projects": 15, "builds": 50},
    TenantPlan.PRO: {"monthly": 299, "name": "Pro", "projects": 50, "builds": 200},
    TenantPlan.ENTERPRISE: {"monthly": 999, "name": "Enterprise", "projects": 999, "builds": 9999},
}


def _db():
    return get_database()


@router.get("/plans")
async def list_plans():
    return {"plans": {k.value: v for k, v in PLAN_PRICING.items()}}


@router.get("/subscription")
async def get_subscription(tenant: dict = Depends(get_current_tenant)):
    return {
        "tenant_id": tenant["id"],
        "tenant_name": tenant["name"],
        "plan": tenant.get("plan", "free"),
        "status": tenant.get("status"),
        "billing": tenant.get("billing", {}),
        "features": tenant.get("features", {}),
    }


@router.post("/change-plan")
async def change_plan(
    plan: str,
    tenant: dict = Depends(get_current_tenant),
):
    try:
        new_plan = TenantPlan(plan)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid plan: {plan}")
    tid = tenant["id"]
    settings = get_settings()
    db = _db()
    now = datetime.now(timezone.utc).isoformat()

    if settings.STRIPE_SECRET_KEY:
        try:
            import stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            customer_id = tenant.get("billing", {}).get("stripe_customer_id", "")
            if customer_id:
                subscription_data = {
                    "customer": customer_id,
                    "items": [{"price": f"sla113_{plan}"}],
                }
                sub_id = tenant.get("billing", {}).get("stripe_subscription_id", "")
                if sub_id:
                    stripe.Subscription.modify(sub_id, items=[{"price": f"sla113_{plan}"}])
                else:
                    sub = stripe.Subscription.create(**subscription_data)
                    sub_id = sub.id
                await db["sla113_tenants"].update_one(
                    {"id": tid},
                    {"$set": {
                        "billing.stripe_subscription_id": sub_id,
                        "plan": plan,
                        "updated_at": now,
                    }}
                )
            else:
                raise HTTPException(status_code=400, detail="No Stripe customer record. Contact support.")
        except Exception as e:
            logger.error(f"Stripe plan change failed: {e}")
            raise HTTPException(status_code=500, detail=f"Payment processing error: {e}")
    else:
        from app.models.schemas import TenantFeatureFlags
        features_map = {
            "free": {"custom_domain": False, "api_access": False, "white_label": True, "analytics": False, "priority_support": False, "max_projects": 5, "max_builds_per_month": 10, "max_storage_mb": 500},
            "starter": {"custom_domain": True, "api_access": False, "white_label": True, "analytics": True, "priority_support": False, "max_projects": 15, "max_builds_per_month": 50, "max_storage_mb": 2000},
            "pro": {"custom_domain": True, "api_access": True, "white_label": True, "analytics": True, "priority_support": True, "max_projects": 50, "max_builds_per_month": 200, "max_storage_mb": 10000},
            "enterprise": {"custom_domain": True, "api_access": True, "white_label": True, "analytics": True, "priority_support": True, "max_projects": 999, "max_builds_per_month": 9999, "max_storage_mb": 100000},
        }
        await db["sla113_tenants"].update_one(
            {"id": tid},
            {"$set": {
                "plan": plan,
                "features": features_map.get(plan, features_map["free"]),
                "updated_at": now,
            }}
        )
        logger.info(f"Mock plan change: {tenant['name']} -> {plan}")

    updated = await db["sla113_tenants"].find_one({"id": tid}, {"_id": 0})
    is_mock = not settings.STRIPE_SECRET_KEY
    return {
        "tenant_id": tid, "plan": plan,
        "message": f"Plan changed to {plan}",
        "mock": is_mock,
        "mock_note": "Stripe not configured — plan updated in DB only, no payment processed." if is_mock else None,
        "tenant": updated,
    }


@router.post("/billing-portal")
async def billing_portal(tenant: dict = Depends(get_current_tenant)):
    settings = get_settings()
    if not settings.STRIPE_SECRET_KEY:
        return {
            "url": None,
            "message": "Billing portal not available. Set STRIPE_SECRET_KEY to enable.",
            "mock": True,
        }
    try:
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        customer_id = tenant.get("billing", {}).get("stripe_customer_id", "")
        if not customer_id:
            customer = stripe.Customer.create(
                email=tenant.get("admin_email", ""),
                metadata={"tenant_id": tenant["id"], "tenant_name": tenant["name"]},
            )
            customer_id = customer.id
            await _db()["sla113_tenants"].update_one(
                {"id": tenant["id"]},
                {"$set": {"billing.stripe_customer_id": customer_id}},
            )
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=f"https://{tenant['subdomain']}.{settings.PLATFORM_DOMAIN}/console/billing",
        )
        return {"url": session.url}
    except Exception as e:
        logger.error(f"Billing portal error: {e}")
        raise HTTPException(status_code=500, detail=f"Billing portal error: {e}")


@router.get("/usage")
async def get_usage(tenant: dict = Depends(get_current_tenant)):
    tid = tenant["id"]
    db = _db()
    now = datetime.now(timezone.utc)
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    builds_this_month = await db["sla113_builds"].count_documents({
        "tenant_id": tid,
        "created_at": {"$gte": current_month_start},
    })
    total_storage = tenant.get("stats", {}).get("total_storage_mb", 0)
    features = tenant.get("features", {})
    return {
        "tenant_id": tid,
        "period_start": current_month_start,
        "builds_this_month": builds_this_month,
        "build_limit": features.get("max_builds_per_month", 10),
        "storage_used_mb": total_storage,
        "storage_limit_mb": features.get("max_storage_mb", 500),
        "projects_current": await db["sla113_projects"].count_documents({"tenant_id": tid}),
        "project_limit": features.get("max_projects", 5),
    }
