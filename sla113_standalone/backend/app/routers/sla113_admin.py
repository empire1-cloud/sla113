"""SLA113 Admin — Tenant Management (White Label Mint + Provisioning)"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
import uuid
import os
import logging

from app.core.database import get_database
from app.core.config import get_settings
from app.core.tenant_context import require_master_admin
from app.models.schemas import TenantCreate, TenantUpdate, TenantPlan, TenantStatus, BrandConfig

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/sla113", tags=["sla113-admin"])


def tenants_collection():
    return get_database()["sla113_tenants"]


def _plan_features(plan: TenantPlan) -> dict:
    return {
        TenantPlan.FREE: {"custom_domain": False, "api_access": False, "white_label": True, "analytics": False, "priority_support": False, "max_projects": 5, "max_builds_per_month": 10, "max_storage_mb": 500},
        TenantPlan.STARTER: {"custom_domain": True, "api_access": False, "white_label": True, "analytics": True, "priority_support": False, "max_projects": 15, "max_builds_per_month": 50, "max_storage_mb": 2000},
        TenantPlan.PRO: {"custom_domain": True, "api_access": True, "white_label": True, "analytics": True, "priority_support": True, "max_projects": 50, "max_builds_per_month": 200, "max_storage_mb": 10000},
        TenantPlan.ENTERPRISE: {"custom_domain": True, "api_access": True, "white_label": True, "analytics": True, "priority_support": True, "max_projects": 999, "max_builds_per_month": 9999, "max_storage_mb": 100000},
    }[plan]


@router.post("/tenants")
async def create_tenant(req: TenantCreate, _: bool = Depends(require_master_admin)):
    settings = get_settings()
    now = datetime.now(timezone.utc).isoformat()
    existing = await tenants_collection().find_one({"subdomain": req.subdomain}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=409, detail=f"Subdomain '{req.subdomain}' already exists")

    features = _plan_features(req.plan)
    tenant_url = f"https://{req.subdomain}.{settings.PLATFORM_DOMAIN}"
    tenant_id = str(uuid.uuid4())

    tenant = {
        "id": tenant_id,
        "name": req.name,
        "subdomain": req.subdomain,
        "plan": req.plan.value,
        "status": TenantStatus.PROVISIONING.value,
        "brand": req.brand.model_dump() if req.brand else BrandConfig().model_dump(),
        "features": features,
        "admin_email": req.admin_email,
        "credits": 0,
        "rtp_mode": 92,
        "tenant_url": tenant_url,
        "billing": {
            "stripe_customer_id": "",
            "stripe_subscription_id": "",
            "current_period_start": now,
            "current_period_end": "",
            "payment_method": "",
            "billing_email": req.admin_email,
        },
        "stats": {
            "total_projects": 0,
            "total_builds": 0,
            "total_deploys": 0,
            "total_storage_mb": 0,
            "api_calls_this_month": 0,
        },
        "created_at": now,
        "updated_at": now,
    }
    await tenants_collection().insert_one(tenant)
    tenant.pop("_id", None)

    await tenants_collection().update_one(
        {"id": tenant_id},
        {"$set": {"status": TenantStatus.ACTIVE.value, "updated_at": now}},
    )
    tenant["status"] = TenantStatus.ACTIVE.value

    logger.info(f"Tenant provisioned: {req.name} ({req.subdomain}) — {tenant_url}")
    return tenant


@router.get("/tenants")
async def list_tenants(_: bool = Depends(require_master_admin)):
    cursor = tenants_collection().find({}, {"_id": 0}).sort("created_at", -1)
    tenants = await cursor.to_list(200)
    return {"tenants": tenants, "total": len(tenants)}


@router.get("/tenants/{tenant_id}")
async def get_tenant(tenant_id: str, _: bool = Depends(require_master_admin)):
    tenant = await tenants_collection().find_one({"id": tenant_id}, {"_id": 0})
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@router.put("/tenants/{tenant_id}")
async def update_tenant(tenant_id: str, req: TenantUpdate, _: bool = Depends(require_master_admin)):
    update = {k: v for k, v in req.model_dump(exclude_unset=True).items() if v is not None}
    if not update:
        raise HTTPException(status_code=400, detail="No fields to update")
    update["updated_at"] = datetime.now(timezone.utc).isoformat()
    if "plan" in update:
        update["features"] = _plan_features(TenantPlan(update["plan"]))
    result = await tenants_collection().update_one({"id": tenant_id}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return await tenants_collection().find_one({"id": tenant_id}, {"_id": 0})


@router.delete("/tenants/{tenant_id}")
async def delete_tenant(tenant_id: str, _: bool = Depends(require_master_admin)):
    tenant = await tenants_collection().find_one({"id": tenant_id})
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    await tenants_collection().delete_one({"id": tenant_id})
    logger.info(f"Tenant deleted: {tenant.get('name')} ({tenant_id})")
    return {"deleted": True}


@router.put("/tenants/{tenant_id}/credits")
async def update_tenant_credits(tenant_id: str, amount: int, _: bool = Depends(require_master_admin)):
    result = await tenants_collection().update_one(
        {"id": tenant_id},
        {"$inc": {"credits": amount}, "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return await tenants_collection().find_one({"id": tenant_id}, {"_id": 0})


@router.put("/tenants/{tenant_id}/rtp")
async def update_tenant_rtp(tenant_id: str, rtp: int, _: bool = Depends(require_master_admin)):
    if rtp < 80 or rtp > 99:
        raise HTTPException(status_code=400, detail="RTP must be between 80 and 99")
    await tenants_collection().update_one(
        {"id": tenant_id}, {"$set": {"rtp_mode": rtp, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    return await tenants_collection().find_one({"id": tenant_id}, {"_id": 0})


@router.post("/tenants/{tenant_id}/provision")
async def provision_tenant(tenant_id: str, _: bool = Depends(require_master_admin)):
    tenant = await tenants_collection().find_one({"id": tenant_id})
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    settings = get_settings()
    now = datetime.now(timezone.utc).isoformat()
    subdomain = tenant["subdomain"]
    deploy_dir = f"/app/backend/static/tenants/{subdomain}"
    os.makedirs(deploy_dir, exist_ok=True)

    await tenants_collection().update_one(
        {"id": tenant_id},
        {"$set": {
            "status": TenantStatus.ACTIVE.value,
            "tenant_url": f"https://{subdomain}.{settings.PLATFORM_DOMAIN}",
            "deploy_path": deploy_dir,
            "provisioned_at": now,
            "updated_at": now,
        }}
    )
    logger.info(f"Tenant provisioned on disk: {subdomain} -> {deploy_dir}")
    return await tenants_collection().find_one({"id": tenant_id}, {"_id": 0})
