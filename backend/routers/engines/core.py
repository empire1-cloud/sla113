"""
Core and Health endpoints for the Hybrid Intelligence system.
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any

from services.hybrid_core import get_core, TaskType
from services.error_handler import ErrorHandler, PipelineStage

router = APIRouter(tags=["core"])


class CoreRequest(BaseModel):
    """Unified request for Hybrid Intelligence Core."""
    prompt: str
    task_type: Optional[str] = None
    context: Optional[str] = None
    force_model: Optional[str] = None


class CoreResponse(BaseModel):
    """Unified response from Hybrid Intelligence Core."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


@router.post("/core/execute", response_model=CoreResponse)
async def core_execute(payload: CoreRequest):
    """
    Execute via Hybrid Intelligence Core.
    
    The Core automatically:
    1. Classifies the task type
    2. Routes to optimal model
    3. Executes appropriate engine
    4. Enforces canon rules
    5. Monitors drift
    6. Handles errors
    """
    core = get_core()
    
    task_type = None
    if payload.task_type:
        try:
            task_type = TaskType(payload.task_type)
        except ValueError:
            pass
    
    result = await core.execute(
        prompt=payload.prompt,
        task_type=task_type,
        context=payload.context,
        force_model=payload.force_model
    )
    
    if result.success:
        return CoreResponse(
            success=True,
            data=result.data,
            metadata=result.metadata
        )
    else:
        return JSONResponse(
            status_code=500,
            content=result.error
        )


@router.post("/core/strategy-to-plan", response_model=CoreResponse)
async def core_strategy_to_plan(payload: CoreRequest):
    """Execute full strategy → plan pipeline via Core."""
    core = get_core()
    
    result = await core.execute_strategy_to_plan(
        goal=payload.prompt,
        context=payload.context,
        force_model=payload.force_model
    )
    
    if result.success:
        return CoreResponse(
            success=True,
            data=result.data,
            metadata=result.metadata
        )
    else:
        return JSONResponse(
            status_code=500,
            content=result.error
        )


@router.get("/core/status")
async def core_status():
    """Get Hybrid Intelligence Core system status."""
    core = get_core()
    return core.get_system_status()


@router.get("/core/log")
async def core_execution_log(limit: int = 50):
    """Get recent execution log from the Core."""
    core = get_core()
    return {
        "log": core.get_execution_log(limit),
        "total_executions": len(core.execution_log)
    }


@router.get("/health")
async def health_check():
    """Check hybrid AI pipeline health."""
    return {
        "status": "healthy",
        "pipeline": "hybrid-ai-stack",
        "models": {
            "gpt-5.2": "available",
            "claude-sonnet-4.5": "available",
            "gemini-3-flash": "available"
        },
        "engines": [
            "hybrid_intelligence_core",
            "routing_engine",
            "strategy_engine",
            "plan_builder_engine",
            "analysis_engine",
            "opportunity_mapper_engine",
            "evaluator_engine",
            "pricing_engine",
            "blueprint_engine",
            "persona_engine",
            "anime_character_engine",
            "anime_lore_engine",
            "anime_story_engine",
            "art_direction_engine",
            "pipeline_composer_engine",
            "canon_enforcer",
            "drift_monitor",
            "error_handler"
        ]
    }
