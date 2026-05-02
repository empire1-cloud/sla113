"""
Execution History API endpoints (Team-Scoped).
All history is isolated by team for multi-tenant support.
"""

from fastapi import APIRouter, Query, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

from core.dependencies import get_current_user, get_current_team
from core.engine_context import get_engine_context, EngineContext
from services.execution_logger_db import (
    log_execution,
    get_team_execution_logs,
    get_team_execution_stats,
    get_execution_log_detail,
)
from models import ExecutionLogQuery

router = APIRouter(prefix="/history", tags=["Execution History"])


class ManualLogRequest(BaseModel):
    engine: str
    endpoint: str
    method: str = "POST"
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration_ms: int = 0
    source: str = "api"
    pipeline_id: Optional[str] = None


@router.get("")
async def get_execution_history(
    engine: Optional[str] = Query(None, description="Filter by engine name"),
    status: Optional[str] = Query(None, description="Filter by status (success/error)"),
    source: Optional[str] = Query(None, description="Filter by source (direct/pipeline)"),
    pipeline_id: Optional[str] = Query(None, description="Filter by pipeline ID"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    limit: int = Query(50, ge=1, le=500, description="Number of logs to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    ctx: EngineContext = Depends(get_engine_context),
):
    """
    Get execution history for the current team.
    Results are automatically scoped to the user's current team.
    """
    query = ExecutionLogQuery(
        engine=engine,
        pipeline_id=pipeline_id,
        status=status,
        source=source,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )
    
    return await get_team_execution_logs(ctx.team_id, query)


@router.get("/stats")
async def get_execution_stats(
    ctx: EngineContext = Depends(get_engine_context),
):
    """
    Get execution statistics for the current team.
    """
    return await get_team_execution_stats(ctx.team_id)


@router.get("/{log_id}")
async def get_execution_detail(
    log_id: str,
    ctx: EngineContext = Depends(get_engine_context),
):
    """
    Get full details of a specific execution log.
    """
    result = await get_execution_log_detail(ctx.team_id, log_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Execution log not found")
    
    return result


@router.post("/log")
async def create_execution_log(
    request: ManualLogRequest,
    ctx: EngineContext = Depends(get_engine_context),
):
    """
    Manually log an execution.
    Used by frontend for logging pipeline steps and custom executions.
    """
    ctx.require_write()
    
    log_id = await log_execution(
        team_id=ctx.team_id,
        user_id=ctx.user_id,
        engine=request.engine,
        input_data=request.input_data,
        output_data=request.output_data,
        error_message=request.error,
        duration_ms=request.duration_ms,
        source=request.source,
        pipeline_id=request.pipeline_id,
        endpoint=request.endpoint,
        method=request.method,
    )
    
    return {"status": "logged", "id": log_id}


@router.delete("/clear")
async def clear_execution_history(
    ctx: EngineContext = Depends(get_engine_context),
):
    """
    Clear all execution history for the current team.
    Requires owner or admin role.
    """
    ctx.require_admin()
    
    from database import execution_logs_collection
    
    result = await execution_logs_collection().delete_many({"team_id": ctx.team_id})
    
    return {"message": f"Cleared {result.deleted_count} execution logs"}
