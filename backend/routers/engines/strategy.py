"""
Strategy Engine endpoints.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

from services.router import RoutingEngine
from services.strategy_engine import StrategyEngine
from services.canon_enforcer import CanonEnforcer
from services.drift_monitor import DriftMonitor
from services.error_handler import ErrorHandler, PipelineStage

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


@router.post("/strategy", response_model=StrategyResponse)
async def generate_strategy(payload: StrategyRequest):
    """Generate an actionable strategy using the hybrid AI pipeline."""
    current_stage = None
    try:
        current_stage = PipelineStage.ROUTING
        routing_decision = RoutingEngine.route(payload.goal, payload.force_model)
        
        current_stage = PipelineStage.STRATEGY
        raw_output = await StrategyEngine.generate_async(
            model=routing_decision.model,
            goal=payload.goal,
            context=payload.context,
            tone=payload.tone
        )
        
        current_stage = PipelineStage.CANON
        cleaned_output = CanonEnforcer.normalize(raw_output)
        
        current_stage = PipelineStage.DRIFT
        DriftMonitor.check(cleaned_output, routing_decision.model)
        
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
