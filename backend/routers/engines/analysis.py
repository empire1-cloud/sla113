"""
Analysis Engine endpoints.
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

from services.analysis_engine import AnalysisEngine
from services.canon_enforcer import CanonEnforcer
from services.drift_monitor import DriftMonitor
from services.error_handler import ErrorHandler, PipelineStage

router = APIRouter(tags=["analysis"])


class AnalysisRequest(BaseModel):
    subject: str
    context: Optional[str] = None
    focus_area: Optional[str] = None
    model: Optional[str] = None


class AnalysisResponse(BaseModel):
    overview: str
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threats: List[str]
    key_insights: List[str]
    recommended_focus: str


class CompetitiveAnalysisRequest(BaseModel):
    product: str
    competitors: List[str]
    market: Optional[str] = None


class StrategyResponse(BaseModel):
    summary: str
    steps: List[str]
    risks: List[str]
    resources: List[str]
    next_action: str


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_subject(payload: AnalysisRequest):
    """Perform deep structured analysis on any subject."""
    try:
        raw_analysis = await AnalysisEngine.analyze_async(
            subject=payload.subject,
            context=payload.context,
            focus_area=payload.focus_area,
            model=payload.model
        )
        
        cleaned_analysis = CanonEnforcer.normalize(raw_analysis)
        DriftMonitor.check(cleaned_analysis, payload.model or "claude-sonnet-4.5")
        
        return AnalysisResponse(**cleaned_analysis)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/analyze/competitive", response_model=AnalysisResponse)
async def competitive_analysis(payload: CompetitiveAnalysisRequest):
    """Perform competitive analysis."""
    try:
        raw_analysis = await AnalysisEngine.competitive_analysis_async(
            product=payload.product,
            competitors=payload.competitors,
            market=payload.market
        )
        
        cleaned_analysis = CanonEnforcer.normalize(raw_analysis)
        DriftMonitor.check(cleaned_analysis, "claude-sonnet-4.5")
        
        return AnalysisResponse(**cleaned_analysis)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/analyze/strategy", response_model=AnalysisResponse)
async def analyze_strategy_output(strategy: StrategyResponse):
    """Analyze a strategy output for feasibility and blind spots."""
    try:
        strategy_dict = strategy.model_dump()
        raw_analysis = await AnalysisEngine.analyze_strategy_async(strategy_dict)
        
        cleaned_analysis = CanonEnforcer.normalize(raw_analysis)
        DriftMonitor.check(cleaned_analysis, "claude-sonnet-4.5")
        
        return AnalysisResponse(**cleaned_analysis)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )
