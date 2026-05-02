"""
Execution History API endpoints.
"""
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import time

from services.execution_logger import get_logger, ExecutionLog

router = APIRouter(tags=["history"])


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


@router.get("/history")
async def get_execution_history(
    engine: Optional[str] = Query(None, description="Filter by engine name"),
    status: Optional[str] = Query(None, description="Filter by status (success/error)"),
    source: Optional[str] = Query(None, description="Filter by source (api/pipeline)"),
    search: Optional[str] = Query(None, description="Search in engine, input, endpoint"),
    limit: int = Query(100, ge=1, le=500, description="Number of logs to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """Get execution history with optional filters."""
    logger = get_logger()
    return logger.get_logs(
        engine=engine,
        status=status,
        source=source,
        search=search,
        limit=limit,
        offset=offset
    )


@router.get("/history/stats")
async def get_execution_stats():
    """Get execution statistics."""
    logger = get_logger()
    return logger.get_stats()


@router.post("/history/log")
async def log_execution(request: ManualLogRequest):
    """Manually log an execution (used by frontend for pipeline logging)."""
    logger = get_logger()
    log_entry = logger.log(
        engine=request.engine,
        endpoint=request.endpoint,
        method=request.method,
        input_data=request.input_data,
        output_data=request.output_data,
        error=request.error,
        duration_ms=request.duration_ms,
        source=request.source,
        pipeline_id=request.pipeline_id
    )
    return {"status": "logged", "id": log_entry.id}


@router.delete("/history/clear")
async def clear_history():
    """Clear all execution history."""
    logger = get_logger()
    count = logger.clear_logs()
    return {"status": "cleared", "count": count}


@router.get("/history/export")
async def export_history(
    format: str = Query("json", description="Export format (json)")
):
    """Export execution history."""
    logger = get_logger()
    result = logger.get_logs(limit=10000)
    return result
