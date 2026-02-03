from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio

from services.router import RoutingEngine, RoutingDecision
from services.strategy_engine import StrategyEngine
from services.canon_enforcer import CanonEnforcer
from services.drift_monitor import DriftMonitor
from services.error_handler import ErrorHandler, PipelineStage
from services.plan_builder import PlanBuilderEngine
from services.analysis_engine import AnalysisEngine
from services.hybrid_core import get_core, TaskType

router = APIRouter(tags=["strategy"])

class StrategyRequest(BaseModel):
    goal: str
    context: Optional[str] = None
    tone: Optional[str] = "direct"
    force_model: Optional[str] = None

class StrategyResponse(BaseModel):
    summary: str
    steps: List[str]
    risks: List[str]
    resources: List[str]
    next_action: str

class RoutingResponse(BaseModel):
    model: str
    reason: str

class DriftReportResponse(BaseModel):
    status: str
    model: str
    sample_count: int
    metrics: Optional[dict] = None
    deviations: Optional[dict] = None
    max_deviation: Optional[float] = None
    message: Optional[str] = None

class PlanRequest(BaseModel):
    goal: str
    strategy: Optional[dict] = None
    context: Optional[str] = None
    model: Optional[str] = None

class TaskModel(BaseModel):
    task: str
    steps: List[str]
    owner: str
    dependencies: List[str]

class PhaseModel(BaseModel):
    name: str
    duration: str
    tasks: List[TaskModel]

class PlanResponse(BaseModel):
    objective: str
    phases: List[PhaseModel]
    milestones: List[str]
    critical_path: List[str]
    first_24_hours: List[str]

@router.post("/strategy", response_model=StrategyResponse)
async def generate_strategy(payload: StrategyRequest):
    """Generate an actionable strategy using the hybrid AI pipeline."""
    current_stage = None
    try:
        # 1. ROUTING ENGINE
        current_stage = PipelineStage.ROUTING
        routing_decision = RoutingEngine.route(payload.goal, payload.force_model)
        
        # 2. STRATEGY ENGINE
        current_stage = PipelineStage.STRATEGY
        raw_output = await StrategyEngine.generate_async(
            model=routing_decision.model,
            goal=payload.goal,
            context=payload.context,
            tone=payload.tone
        )
        
        # 3. CANON ENFORCER
        current_stage = PipelineStage.CANON
        cleaned_output = CanonEnforcer.normalize(raw_output)
        
        # 4. DRIFT MONITOR
        current_stage = PipelineStage.DRIFT
        DriftMonitor.check(cleaned_output, routing_decision.model)
        
        # 5. RETURN FINAL JSON
        return StrategyResponse(**cleaned_output)
    
    except Exception as e:
        error_response = ErrorHandler.handle(e, current_stage)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )

@router.post("/route", response_model=RoutingResponse)
async def route_request(payload: StrategyRequest):
    """Get routing decision without generating strategy."""
    try:
        decision = RoutingEngine.route(payload.goal, payload.force_model)
        return RoutingResponse(model=decision.model, reason=decision.reason)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/drift-report")
async def get_drift_report(model: str = "all"):
    """Get drift analysis report for specified model."""
    return DriftMonitor.get_drift_report(model)

@router.get("/drift-report/{model}")
async def get_model_drift_report(model: str):
    """Get drift analysis report for a specific model."""
    valid_models = ["gpt-5.2", "claude-sonnet-4.5", "gemini-3-flash", "all"]
    if model not in valid_models:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid model. Choose from: {', '.join(valid_models)}"
        )
    return DriftMonitor.get_drift_report(model)

@router.post("/drift-reset")
async def reset_drift_metrics(model: Optional[str] = None):
    """Reset drift monitoring metrics."""
    DriftMonitor.reset(model)
    return {"status": "success", "message": f"Metrics reset for {'all models' if not model else model}"}

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
        "stages": [
            "routing_engine",
            "strategy_engine",
            "plan_builder_engine",
            "canon_enforcer",
            "drift_monitor",
            "error_handler"
        ]
    }

@router.post("/plan", response_model=PlanResponse)
async def build_execution_plan(payload: PlanRequest):
    """Convert a goal or strategy into an actionable execution plan."""
    try:
        plan = await PlanBuilderEngine.build_plan_async(
            goal=payload.goal,
            strategy=payload.strategy,
            context=payload.context,
            model=payload.model
        )
        
        # Apply canon enforcement
        cleaned_plan = CanonEnforcer.normalize(plan)
        
        return PlanResponse(**cleaned_plan)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )

@router.post("/strategy-to-plan", response_model=PlanResponse)
async def convert_strategy_to_plan(payload: StrategyRequest):
    """Generate strategy and immediately convert to execution plan."""
    try:
        # 1. Generate strategy
        routing_decision = RoutingEngine.route(payload.goal, payload.force_model)
        raw_strategy = await StrategyEngine.generate_async(
            model=routing_decision.model,
            goal=payload.goal,
            context=payload.context,
            tone=payload.tone
        )
        cleaned_strategy = CanonEnforcer.normalize(raw_strategy)
        
        # 2. Convert to plan
        plan = await PlanBuilderEngine.convert_strategy_to_plan_async(cleaned_strategy)
        cleaned_plan = CanonEnforcer.normalize(plan)
        
        # 3. Monitor drift
        DriftMonitor.check(cleaned_plan, routing_decision.model)
        
        return PlanResponse(**cleaned_plan)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )

# ============================================
# HYBRID INTELLIGENCE CORE ENDPOINTS
# ============================================

class CoreRequest(BaseModel):
    """Unified request for Hybrid Intelligence Core."""
    prompt: str
    task_type: Optional[str] = None  # strategy, plan, analysis, code, quick
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
    
    # Parse task type if provided
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

