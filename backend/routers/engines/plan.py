"""
Plan Builder Engine endpoints.
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

from services.router import RoutingEngine
from services.strategy_engine import StrategyEngine
from services.plan_builder import PlanBuilderEngine
from services.canon_enforcer import CanonEnforcer
from services.drift_monitor import DriftMonitor
from services.error_handler import ErrorHandler, PipelineStage

router = APIRouter(tags=["plan"])


class TaskModel(BaseModel):
    task: str
    steps: List[str]
    owner: str
    dependencies: List[str]


class PhaseModel(BaseModel):
    name: str
    duration: str
    tasks: List[TaskModel]


class PlanRequest(BaseModel):
    goal: str
    strategy: Optional[dict] = None
    context: Optional[str] = None
    model: Optional[str] = None


class PlanResponse(BaseModel):
    objective: str
    phases: List[PhaseModel]
    milestones: List[str]
    critical_path: List[str]
    first_24_hours: List[str]


class StrategyRequest(BaseModel):
    goal: str
    context: Optional[str] = None
    tone: Optional[str] = "direct"
    force_model: Optional[str] = None


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
        routing_decision = RoutingEngine.route(payload.goal, payload.force_model)
        raw_strategy = await StrategyEngine.generate_async(
            model=routing_decision.model,
            goal=payload.goal,
            context=payload.context,
            tone=payload.tone
        )
        cleaned_strategy = CanonEnforcer.normalize(raw_strategy)
        
        plan = await PlanBuilderEngine.convert_strategy_to_plan_async(cleaned_strategy)
        cleaned_plan = CanonEnforcer.normalize(plan)
        
        DriftMonitor.check(cleaned_plan, routing_decision.model)
        
        return PlanResponse(**cleaned_plan)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )
