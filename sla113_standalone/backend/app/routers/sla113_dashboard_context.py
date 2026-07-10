"""SLA113 Dashboard Context — Stats, Game Types, Projects CRUD"""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
import uuid
import logging

from app.core.database import get_database
from app.models.schemas_game_types import GAME_TYPES
from app.models.schemas import CreateProjectRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/sla113", tags=["sla113-dashboard"])


def projects_collection():
    return get_database()["sla113_projects"]


@router.get("/game-types")
async def list_game_types():
    return {"game_types": GAME_TYPES}


@router.get("/stats")
async def get_stats():
    total = await projects_collection().count_documents({})
    by_type = {}
    for gt in GAME_TYPES:
        count = await projects_collection().count_documents({"game_type": gt})
        if count > 0:
            by_type[gt] = count
    return {
        "total_projects": total,
        "by_game_type": by_type,
        "supported_game_types": len(GAME_TYPES),
        "engines": ["vision", "logic", "composer"],
        "version": "1.0.0",
    }


@router.post("/projects")
async def create_project(req: CreateProjectRequest):
    if req.game_type not in GAME_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported game type: {req.game_type}")
    now = datetime.now(timezone.utc).isoformat()
    project = {
        "id": str(uuid.uuid4()),
        "name": req.name,
        "game_type": req.game_type,
        "game_type_info": GAME_TYPES[req.game_type],
        "description": req.description or GAME_TYPES[req.game_type]["description"],
        "theme": req.theme or "default",
        "target_platform": req.target_platform,
        "status": "created",
        "vision_assets": [],
        "logic_specs": [],
        "compositions": [],
        "created_at": now,
        "updated_at": now,
    }
    await projects_collection().insert_one(project)
    project.pop("_id", None)
    return project


@router.get("/projects")
async def list_projects():
    cursor = projects_collection().find({}, {"_id": 0})
    projects = await cursor.to_list(100)
    return {"projects": projects, "total": len(projects)}


@router.get("/projects/{project_id}")
async def get_project(project_id: str):
    project = await projects_collection().find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    result = await projects_collection().delete_one({"id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"deleted": True, "project_id": project_id}
