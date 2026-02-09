"""
Team-Scoped Pipeline Service.
Manages saved pipelines with team isolation.
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from bson import ObjectId

from database import pipelines_collection, users_collection
from models import (
    PipelineCreate,
    PipelineUpdate,
    PipelineResponse,
    PipelineInDB,
)


class PipelineError(Exception):
    """Custom exception for pipeline errors."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


async def create_pipeline(
    team_id: str,
    user_id: str,
    pipeline_data: PipelineCreate,
) -> PipelineResponse:
    """Create a new pipeline."""
    now = datetime.now(timezone.utc)
    
    pipeline_doc = {
        "team_id": team_id,
        "created_by": user_id,
        "name": pipeline_data.name,
        "description": pipeline_data.description,
        "steps": [step.model_dump() for step in pipeline_data.steps],
        "is_template": pipeline_data.is_template,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
        "last_executed_at": None,
        "execution_count": 0,
    }
    
    result = await pipelines_collection().insert_one(pipeline_doc)
    pipeline_id = str(result.inserted_id)
    
    return PipelineResponse(
        id=pipeline_id,
        team_id=team_id,
        created_by=user_id,
        name=pipeline_data.name,
        description=pipeline_data.description,
        steps=pipeline_data.steps,
        is_template=pipeline_data.is_template,
        is_active=True,
        created_at=now,
        updated_at=now,
        execution_count=0,
    )


async def get_team_pipelines(
    team_id: str,
    include_templates: bool = True,
    limit: int = 100,
    offset: int = 0,
) -> Dict[str, Any]:
    """Get all pipelines for a team."""
    filter_query = {"team_id": team_id, "is_active": True}
    
    if not include_templates:
        filter_query["is_template"] = False
    
    total = await pipelines_collection().count_documents(filter_query)
    
    cursor = pipelines_collection().find(filter_query).sort(
        "updated_at", -1
    ).skip(offset).limit(limit)
    
    pipelines = await cursor.to_list(length=limit)
    
    result = []
    for p in pipelines:
        # Get creator name
        creator_name = None
        if p.get("created_by"):
            user = await users_collection().find_one(
                {"_id": ObjectId(p["created_by"])},
                {"first_name": 1, "last_name": 1}
            )
            if user:
                creator_name = f"{user['first_name']} {user['last_name']}"
        
        result.append({
            "id": str(p["_id"]),
            "team_id": p["team_id"],
            "created_by": p["created_by"],
            "created_by_name": creator_name,
            "name": p["name"],
            "description": p.get("description"),
            "steps": p.get("steps", []),
            "is_template": p.get("is_template", False),
            "is_active": True,
            "created_at": p["created_at"].isoformat() if isinstance(p["created_at"], datetime) else p["created_at"],
            "updated_at": p["updated_at"].isoformat() if isinstance(p["updated_at"], datetime) else p["updated_at"],
            "last_executed_at": p.get("last_executed_at").isoformat() if p.get("last_executed_at") and isinstance(p["last_executed_at"], datetime) else p.get("last_executed_at"),
            "execution_count": p.get("execution_count", 0),
        })
    
    return {
        "pipelines": result,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


async def get_pipeline_by_id(
    team_id: str,
    pipeline_id: str,
) -> Optional[Dict[str, Any]]:
    """Get a specific pipeline by ID."""
    if not ObjectId.is_valid(pipeline_id):
        return None
    
    pipeline = await pipelines_collection().find_one({
        "_id": ObjectId(pipeline_id),
        "team_id": team_id,
        "is_active": True,
    })
    
    if not pipeline:
        return None
    
    # Get creator name
    creator_name = None
    if pipeline.get("created_by"):
        user = await users_collection().find_one(
            {"_id": ObjectId(pipeline["created_by"])},
            {"first_name": 1, "last_name": 1}
        )
        if user:
            creator_name = f"{user['first_name']} {user['last_name']}"
    
    return {
        "id": str(pipeline["_id"]),
        "team_id": pipeline["team_id"],
        "created_by": pipeline["created_by"],
        "created_by_name": creator_name,
        "name": pipeline["name"],
        "description": pipeline.get("description"),
        "steps": pipeline.get("steps", []),
        "is_template": pipeline.get("is_template", False),
        "is_active": True,
        "created_at": pipeline["created_at"].isoformat() if isinstance(pipeline["created_at"], datetime) else pipeline["created_at"],
        "updated_at": pipeline["updated_at"].isoformat() if isinstance(pipeline["updated_at"], datetime) else pipeline["updated_at"],
        "last_executed_at": pipeline.get("last_executed_at").isoformat() if pipeline.get("last_executed_at") and isinstance(pipeline["last_executed_at"], datetime) else pipeline.get("last_executed_at"),
        "execution_count": pipeline.get("execution_count", 0),
    }


async def update_pipeline(
    team_id: str,
    pipeline_id: str,
    user_id: str,
    pipeline_data: PipelineUpdate,
) -> Dict[str, Any]:
    """Update a pipeline."""
    if not ObjectId.is_valid(pipeline_id):
        raise PipelineError("Invalid pipeline ID", 400)
    
    # Check pipeline exists and belongs to team
    existing = await pipelines_collection().find_one({
        "_id": ObjectId(pipeline_id),
        "team_id": team_id,
        "is_active": True,
    })
    
    if not existing:
        raise PipelineError("Pipeline not found", 404)
    
    update_fields = {"updated_at": datetime.now(timezone.utc)}
    
    if pipeline_data.name is not None:
        update_fields["name"] = pipeline_data.name
    
    if pipeline_data.description is not None:
        update_fields["description"] = pipeline_data.description
    
    if pipeline_data.steps is not None:
        update_fields["steps"] = [step.model_dump() for step in pipeline_data.steps]
    
    if pipeline_data.is_template is not None:
        update_fields["is_template"] = pipeline_data.is_template
    
    await pipelines_collection().update_one(
        {"_id": ObjectId(pipeline_id)},
        {"$set": update_fields}
    )
    
    return await get_pipeline_by_id(team_id, pipeline_id)


async def delete_pipeline(
    team_id: str,
    pipeline_id: str,
) -> bool:
    """Soft delete a pipeline."""
    if not ObjectId.is_valid(pipeline_id):
        raise PipelineError("Invalid pipeline ID", 400)
    
    result = await pipelines_collection().update_one(
        {"_id": ObjectId(pipeline_id), "team_id": team_id, "is_active": True},
        {"$set": {"is_active": False, "updated_at": datetime.now(timezone.utc)}}
    )
    
    if result.matched_count == 0:
        raise PipelineError("Pipeline not found", 404)
    
    return True


async def record_pipeline_execution(
    team_id: str,
    pipeline_id: str,
):
    """Record that a pipeline was executed."""
    if not ObjectId.is_valid(pipeline_id):
        return
    
    await pipelines_collection().update_one(
        {"_id": ObjectId(pipeline_id), "team_id": team_id},
        {
            "$set": {"last_executed_at": datetime.now(timezone.utc)},
            "$inc": {"execution_count": 1}
        }
    )
