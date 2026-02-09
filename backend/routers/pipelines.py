"""
Pipeline Management API (Team-Scoped).
CRUD operations for saved pipelines with team isolation.
"""

from fastapi import APIRouter, Query, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from core.engine_context import get_engine_context, EngineContext
from services.pipeline_service import (
    create_pipeline,
    get_team_pipelines,
    get_pipeline_by_id,
    update_pipeline,
    delete_pipeline,
    PipelineError,
)
from models import PipelineCreate, PipelineUpdate, PipelineStep

router = APIRouter(prefix="/pipelines", tags=["Pipelines"])


@router.post("")
async def create_new_pipeline(
    pipeline_data: PipelineCreate,
    ctx: EngineContext = Depends(get_engine_context),
):
    """
    Create a new pipeline.
    Requires member role or higher.
    """
    ctx.require_write()
    
    return await create_pipeline(
        team_id=ctx.team_id,
        user_id=ctx.user_id,
        pipeline_data=pipeline_data,
    )


@router.get("")
async def list_pipelines(
    include_templates: bool = Query(True, description="Include template pipelines"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    ctx: EngineContext = Depends(get_engine_context),
):
    """
    Get all pipelines for the current team.
    """
    return await get_team_pipelines(
        team_id=ctx.team_id,
        include_templates=include_templates,
        limit=limit,
        offset=offset,
    )


@router.get("/{pipeline_id}")
async def get_pipeline(
    pipeline_id: str,
    ctx: EngineContext = Depends(get_engine_context),
):
    """
    Get a specific pipeline by ID.
    """
    result = await get_pipeline_by_id(ctx.team_id, pipeline_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    return result


@router.put("/{pipeline_id}")
async def update_existing_pipeline(
    pipeline_id: str,
    pipeline_data: PipelineUpdate,
    ctx: EngineContext = Depends(get_engine_context),
):
    """
    Update a pipeline.
    Requires member role or higher.
    """
    ctx.require_write()
    
    try:
        return await update_pipeline(
            team_id=ctx.team_id,
            pipeline_id=pipeline_id,
            user_id=ctx.user_id,
            pipeline_data=pipeline_data,
        )
    except PipelineError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{pipeline_id}")
async def delete_existing_pipeline(
    pipeline_id: str,
    ctx: EngineContext = Depends(get_engine_context),
):
    """
    Delete a pipeline (soft delete).
    Requires member role or higher.
    """
    ctx.require_write()
    
    try:
        await delete_pipeline(ctx.team_id, pipeline_id)
        return {"message": "Pipeline deleted"}
    except PipelineError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
