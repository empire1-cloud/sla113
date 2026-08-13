"""SLA113 Master Admin Console — System-wide oversight.

Protected by MASTER_API_KEY. Exposes platform-level stats, health,
tenant activity summary, and system configuration.
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
import logging

from app.core.database import get_database
from app.core.config import get_settings
from app.core.tenant_context import require_master_admin

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin", tags=["sla113-master-admin"])


def _db():
    return get_database()


@router.get("/health")
async def admin_health():
    return {
        "status": "online",
        "service": "SLA113 White-Label Platform",
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/stats")
async def admin_stats(_: bool = Depends(require_master_admin)):
    db = _db()
    total_tenants = await db["sla113_tenants"].count_documents({})
    active_tenants = await db["sla113_tenants"].count_documents({"status": "active"})
    total_projects = await db["sla113_projects"].count_documents({})
    total_builds = await db["sla113_builds"].count_documents({})
    total_deployments = await db["sla113_deployments"].count_documents({})
    by_plan = {}
    cursor = db["sla113_tenants"].aggregate([
        {"$group": {"_id": "$plan", "count": {"$sum": 1}}}
    ])
    async for row in cursor:
        by_plan[row["_id"]] = row["count"]
    return {
        "platform": {
            "domain": get_settings().PLATFORM_DOMAIN,
            "total_tenants": total_tenants,
            "active_tenants": active_tenants,
            "tenants_by_plan": by_plan,
            "total_projects": total_projects,
            "total_builds": total_builds,
            "total_deployments": total_deployments,
        }
    }


@router.get("/tenants")
async def admin_list_tenants(_: bool = Depends(require_master_admin)):
    db = _db()
    cursor = db["sla113_tenants"].find(
        {}, {"_id": 0, "admin_password": 0}
    ).sort("created_at", -1).limit(200)
    tenants = await cursor.to_list(200)
    return {"tenants": tenants, "total": len(tenants)}


@router.get("/tenants/{tenant_id}")
async def admin_get_tenant(tenant_id: str, _: bool = Depends(require_master_admin)):
    db = _db()
    tenant = await db["sla113_tenants"].find_one(
        {"id": tenant_id}, {"_id": 0, "admin_password": 0}
    )
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    projects = await db["sla113_projects"].count_documents({"tenant_id": tenant_id})
    builds = await db["sla113_builds"].count_documents({"tenant_id": tenant_id})
    deployments = await db["sla113_deployments"].count_documents({"tenant_id": tenant_id})
    tenant["resource_counts"] = {"projects": projects, "builds": builds, "deployments": deployments}
    return tenant


@router.get("/tenants/{tenant_id}/activity")
async def admin_tenant_activity(tenant_id: str, _: bool = Depends(require_master_admin)):
    db = _db()
    tenant = await db["sla113_tenants"].find_one({"id": tenant_id})
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    builds = await db["sla113_builds"].find(
        {"tenant_id": tenant_id}, {"_id": 0}
    ).sort("created_at", -1).limit(20).to_list(20)
    deploys = await db["sla113_deployments"].find(
        {"tenant_id": tenant_id}, {"_id": 0}
    ).sort("created_at", -1).limit(10).to_list(10)
    return {
        "tenant_id": tenant_id,
        "tenant_name": tenant.get("name"),
        "recent_builds": builds,
        "recent_deployments": deploys,
    }
