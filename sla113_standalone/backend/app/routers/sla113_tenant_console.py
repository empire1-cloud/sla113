"""SLA113 Tenant Console — Branded operator dashboard per tenant.

Every endpoint in this router is scoped to the tenant resolved from
the subdomain. Uses `get_current_tenant` dependency.
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime, timezone
import uuid
import logging

from app.core.database import get_database
from app.models.schemas_game_types import GAME_TYPES
from app.core.tenant_context import get_current_tenant
from app.models.schemas import CreateProjectRequest, CreateBuildRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/console", tags=["sla113-tenant-console"])


def _db():
    return get_database()


@router.get("/brand")
async def get_brand(tenant: dict = Depends(get_current_tenant)):
    return {
        "tenant_id": tenant["id"],
        "name": tenant["name"],
        "subdomain": tenant["subdomain"],
        "plan": tenant.get("plan", "free"),
        "brand": tenant.get("brand", {}),
        "features": tenant.get("features", {}),
        "tenant_url": tenant.get("tenant_url", ""),
    }


@router.get("/stats")
async def console_stats(tenant: dict = Depends(get_current_tenant)):
    db = _db()
    tid = tenant["id"]
    total_projects = await db["sla113_projects"].count_documents({"tenant_id": tid})
    total_builds = await db["sla113_builds"].count_documents({"tenant_id": tid})
    total_deploys = await db["sla113_deployments"].count_documents({"tenant_id": tid})
    last_build = await db["sla113_builds"].find_one(
        {"tenant_id": tid}, {"_id": 0}, sort=[("created_at", -1)]
    )
    return {
        "tenant_id": tid,
        "total_projects": total_projects,
        "total_builds": total_builds,
        "total_deployments": total_deploys,
        "supported_game_types": len(GAME_TYPES),
        "last_build_status": last_build.get("status") if last_build else None,
        "credits_remaining": tenant.get("credits", 0),
        "storage_used_mb": tenant.get("stats", {}).get("total_storage_mb", 0),
        "storage_limit_mb": tenant.get("features", {}).get("max_storage_mb", 500),
    }


@router.get("/features")
async def console_features(tenant: dict = Depends(get_current_tenant)):
    return {
        "tenant_id": tenant["id"],
        "plan": tenant.get("plan"),
        "features": tenant.get("features"),
    }


@router.put("/brand")
async def update_brand(
    brand: dict,
    tenant: dict = Depends(get_current_tenant),
):
    allowed_keys = {"primary_color", "secondary_color", "accent_color",
                    "logo_url", "favicon_url", "custom_css", "operator_name", "tagline"}
    updates = {k: v for k, v in brand.items() if k in allowed_keys}
    if not updates:
        raise HTTPException(status_code=400, detail="No valid brand fields provided")
    db = _db()
    now = datetime.now(timezone.utc).isoformat()
    set_clause = {f"brand.{k}": v for k, v in updates.items()}
    set_clause["updated_at"] = now
    await db["sla113_tenants"].update_one({"id": tenant["id"]}, {"$set": set_clause})
    return await db["sla113_tenants"].find_one({"id": tenant["id"]}, {"_id": 0})


@router.get("/game-types")
async def tenant_game_types(_: dict = Depends(get_current_tenant)):
    return {"game_types": GAME_TYPES}


# ─── Tenant-scoped Projects ───
@router.post("/projects")
async def create_project(
    req: CreateProjectRequest,
    tenant: dict = Depends(get_current_tenant),
):
    tid = tenant["id"]
    features = tenant.get("features", {})
    db = _db()
    count = await db["sla113_projects"].count_documents({"tenant_id": tid})
    max_projects = features.get("max_projects", 5)
    if count >= max_projects:
        raise HTTPException(status_code=429, detail=f"Project limit ({max_projects}) reached. Upgrade your plan.")
    now = datetime.now(timezone.utc).isoformat()
    project = {
        "id": str(uuid.uuid4()),
        "tenant_id": tid,
        "name": req.name,
        "game_type": req.game_type,
        "description": req.description or "",
        "theme": req.theme or "default",
        "target_platform": req.target_platform,
        "status": "draft",
        "created_at": now,
        "updated_at": now,
    }
    await db["sla113_projects"].insert_one(project)
    project.pop("_id", None)
    await db["sla113_tenants"].update_one(
        {"id": tid},
        {"$inc": {"stats.total_projects": 1}, "$set": {"updated_at": now}},
    )
    return project


@router.get("/projects")
async def list_projects(tenant: dict = Depends(get_current_tenant)):
    db = _db()
    cursor = db["sla113_projects"].find(
        {"tenant_id": tenant["id"]}, {"_id": 0}
    ).sort("created_at", -1)
    projects = await cursor.to_list(100)
    return {"projects": projects, "total": len(projects)}


@router.get("/projects/{project_id}")
async def get_project(project_id: str, tenant: dict = Depends(get_current_tenant)):
    db = _db()
    project = await db["sla113_projects"].find_one(
        {"id": project_id, "tenant_id": tenant["id"]}, {"_id": 0}
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/projects/{project_id}")
async def delete_project(project_id: str, tenant: dict = Depends(get_current_tenant)):
    db = _db()
    result = await db["sla113_projects"].delete_one(
        {"id": project_id, "tenant_id": tenant["id"]}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    await db["sla113_tenants"].update_one(
        {"id": tenant["id"]},
        {"$inc": {"stats.total_projects": -1}},
    )
    return {"deleted": True}


# ─── Tenant-scoped Builds ───
@router.post("/builds")
async def create_build(
    req: CreateBuildRequest,
    tenant: dict = Depends(get_current_tenant),
):
    tid = tenant["id"]
    features = tenant.get("features", {})
    db = _db()
    project = await db["sla113_projects"].find_one(
        {"id": req.project_id, "tenant_id": tid}
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found in this tenant")
    now = datetime.now(timezone.utc).isoformat()
    build = {
        "id": f"BLD-{uuid.uuid4().hex[:8].upper()}",
        "tenant_id": tid,
        "project_id": req.project_id,
        "project_name": project.get("name", "Unknown"),
        "game_type": project.get("game_type", "unknown"),
        "target": req.target,
        "optimization": req.optimization,
        "include_assets": req.include_assets,
        "include_logic": req.include_logic,
        "status": "queued",
        "progress": 0,
        "stages": [
            {"name": "Asset Compilation", "status": "pending", "progress": 0},
            {"name": "Logic Binding", "status": "pending", "progress": 0},
            {"name": "Shader Compilation", "status": "pending", "progress": 0},
            {"name": "Bundle Packaging", "status": "pending", "progress": 0},
            {"name": "Optimization Pass", "status": "pending", "progress": 0},
        ],
        "output": None,
        "size_mb": None,
        "logs": [f"[{now}] Build queued by {tenant['name']}."],
        "created_at": now,
        "updated_at": now,
    }
    await db["sla113_builds"].insert_one(build)
    build.pop("_id", None)
    await db["sla113_tenants"].update_one(
        {"id": tid},
        {"$inc": {"stats.total_builds": 1}},
    )
    return build


@router.get("/builds")
async def list_builds(tenant: dict = Depends(get_current_tenant)):
    db = _db()
    cursor = db["sla113_builds"].find(
        {"tenant_id": tenant["id"]}, {"_id": 0}
    ).sort("created_at", -1)
    builds = await cursor.to_list(100)
    return {"builds": builds, "total": len(builds)}


@router.get("/builds/{build_id}")
async def get_build(build_id: str, tenant: dict = Depends(get_current_tenant)):
    db = _db()
    build = await db["sla113_builds"].find_one(
        {"id": build_id, "tenant_id": tenant["id"]}, {"_id": 0}
    )
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")
    return build


@router.post("/builds/{build_id}/advance")
async def advance_build(build_id: str, tenant: dict = Depends(get_current_tenant)):
    db = _db()
    build = await db["sla113_builds"].find_one(
        {"id": build_id, "tenant_id": tenant["id"]}, {"_id": 0}
    )
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")
    if build["status"] == "completed":
        return build
    now = datetime.now(timezone.utc).isoformat()
    advanced = False
    for stage in build.get("stages", []):
        if stage["status"] == "pending":
            stage["status"] = "processing"
            stage["progress"] = 50
            advanced = True
            break
        elif stage["status"] == "processing":
            stage["status"] = "completed"
            stage["progress"] = 100
            advanced = True
            break
    if not advanced:
        new_status = "completed"
        new_progress = 100
        log_msg = f"[{now}] Build completed successfully."
    else:
        completed = sum(1 for s in build["stages"] if s["status"] == "completed")
        total = len(build["stages"])
        new_progress = int((completed / total) * 100)
        new_status = "building" if new_progress < 100 else "completed"
        log_msg = f"[{now}] Build progress: {new_progress}%"
    await db["sla113_builds"].update_one(
        {"id": build_id},
        {"$set": {"stages": build["stages"], "status": new_status, "progress": new_progress, "updated_at": now},
         "$push": {"logs": log_msg}},
    )
    result = await db["sla113_builds"].find_one({"id": build_id}, {"_id": 0})
    if new_status == "completed":
        await db["sla113_tenants"].update_one(
            {"id": tenant["id"]},
            {"$set": {"updated_at": now}},
        )
    return result
