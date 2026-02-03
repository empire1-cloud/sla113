from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import asyncio

from services.router import RoutingEngine, RoutingDecision
from services.strategy_engine import StrategyEngine
from services.canon_enforcer import CanonEnforcer
from services.drift_monitor import DriftMonitor

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

@router.post("/strategy", response_model=StrategyResponse)
async def generate_strategy(payload: StrategyRequest):
    """Generate an actionable strategy using the hybrid AI pipeline."""
    try:
        # 1. ROUTING ENGINE
        routing_decision = RoutingEngine.route(payload.goal, payload.force_model)
        
        # 2. STRATEGY ENGINE
        raw_output = await StrategyEngine.generate_async(
            model=routing_decision.model,
            goal=payload.goal,
            context=payload.context,
            tone=payload.tone
        )
        
        # 3. CANON ENFORCER
        cleaned_output = CanonEnforcer.normalize(raw_output)
        
        # 4. DRIFT MONITOR
        DriftMonitor.check(cleaned_output, routing_decision.model)
        
        # 5. RETURN FINAL JSON
        return StrategyResponse(**cleaned_output)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
            "canon_enforcer",
            "drift_monitor"
        ]
    }
