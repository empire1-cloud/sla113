"""SLA113 API Router - Universal AI Game Studio"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime, timezone
import uuid
import logging

from database import get_database
from sla113.models import (
    GAME_TYPES,
    CreateProjectRequest,
    VisionGenerateRequest,
    LogicGenerateRequest,
    ComposeRequest,
)
from sla113.vision_engine import generate_vision_assets
from sla113.logic_engine import generate_logic
from sla113.composer_engine import compose_game_bundle

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sla113", tags=["sla113"])


def projects_collection():
    return get_database()["sla113_projects"]


# ─── Game Types ───
@router.get("/game-types")
async def list_game_types():
    """List all supported game types."""
    return {"game_types": GAME_TYPES}


# ─── Projects CRUD ───
@router.post("/projects")
async def create_project(req: CreateProjectRequest):
    """Create a new game project."""
    if req.game_type not in GAME_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported game type: {req.game_type}. Supported: {list(GAME_TYPES.keys())}")

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
    """List all game projects."""
    cursor = projects_collection().find({}, {"_id": 0})
    projects = await cursor.to_list(100)
    return {"projects": projects, "total": len(projects)}


@router.get("/projects/{project_id}")
async def get_project(project_id: str):
    """Get a game project by ID."""
    project = await projects_collection().find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a game project."""
    result = await projects_collection().delete_one({"id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"deleted": True, "project_id": project_id}


# ─── Vision Engine ───
@router.post("/vision/generate")
async def generate_vision(req: VisionGenerateRequest):
    """Generate visual assets for a game project."""
    project = await projects_collection().find_one({"id": req.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        result = await generate_vision_assets(
            project=project,
            asset_type=req.asset_type,
            style=req.style,
            count=req.count,
            custom_prompt=req.custom_prompt,
        )

        # Save generated assets to project
        await projects_collection().update_one(
            {"id": req.project_id},
            {
                "$push": {"vision_assets": result},
                "$set": {"status": "vision_generated", "updated_at": datetime.now(timezone.utc).isoformat()},
            },
        )
        return result

    except Exception as e:
        logger.error(f"Vision generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Vision generation failed: {str(e)}")


# ─── Logic Engine ───
@router.post("/logic/generate")
async def generate_game_logic(req: LogicGenerateRequest):
    """Generate game logic/math for a project."""
    project = await projects_collection().find_one({"id": req.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        result = await generate_logic(
            project=project,
            logic_type=req.logic_type,
            difficulty=req.difficulty,
            custom_requirements=req.custom_requirements,
        )

        await projects_collection().update_one(
            {"id": req.project_id},
            {
                "$push": {"logic_specs": result},
                "$set": {"status": "logic_generated", "updated_at": datetime.now(timezone.utc).isoformat()},
            },
        )
        return result

    except Exception as e:
        logger.error(f"Logic generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Logic generation failed: {str(e)}")


# ─── Composer Engine ───
@router.post("/compose")
async def compose_game(req: ComposeRequest):
    """Compose a complete game bundle from generated assets."""
    project = await projects_collection().find_one({"id": req.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        result = await compose_game_bundle(
            project=project,
            include_vision=req.include_vision,
            include_logic=req.include_logic,
            output_format=req.output_format,
        )

        await projects_collection().update_one(
            {"id": req.project_id},
            {
                "$push": {"compositions": result},
                "$set": {"status": "composed", "updated_at": datetime.now(timezone.utc).isoformat()},
            },
        )
        return result

    except Exception as e:
        logger.error(f"Composition failed: {e}")
        raise HTTPException(status_code=500, detail=f"Composition failed: {str(e)}")


# ─── Quick Stats ───
@router.get("/stats")
async def get_stats():
    """Get SLA113 platform stats."""
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
