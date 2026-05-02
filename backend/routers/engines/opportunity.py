"""
Opportunity Mapper Engine endpoints.
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

from services.opportunity_mapper import OpportunityMapperEngine
from services.canon_enforcer import CanonEnforcer
from services.drift_monitor import DriftMonitor
from services.error_handler import ErrorHandler, PipelineStage

router = APIRouter(tags=["opportunity"])


class OpportunityRequest(BaseModel):
    situation: str
    context: Optional[str] = None
    constraints: Optional[List[str]] = None
    goals: Optional[List[str]] = None
    model: Optional[str] = None


class MarketOpportunityRequest(BaseModel):
    market: str
    current_position: Optional[str] = None
    competitors: Optional[List[str]] = None
    budget: Optional[str] = None


class QuickWinsRequest(BaseModel):
    situation: str
    timeframe: Optional[str] = "30 days"


class OpportunityItem(BaseModel):
    name: str
    description: str
    impact: str
    effort: str
    time_to_value: str
    dependencies: List[str]
    risks: List[str]


class OpportunityResponse(BaseModel):
    context_summary: str
    opportunities: List[OpportunityItem]
    top_3_opportunities: List[str]
    recommended_next_move: str


class StrategyResponse(BaseModel):
    summary: str
    steps: List[str]
    risks: List[str]
    resources: List[str]
    next_action: str


@router.post("/opportunities", response_model=OpportunityResponse)
async def map_opportunities(payload: OpportunityRequest):
    """Map highest-leverage opportunities for a situation."""
    try:
        raw_opportunities = await OpportunityMapperEngine.map_opportunities_async(
            situation=payload.situation,
            context=payload.context,
            constraints=payload.constraints,
            goals=payload.goals,
            model=payload.model
        )
        
        cleaned_opportunities = CanonEnforcer.normalize(raw_opportunities)
        DriftMonitor.check(cleaned_opportunities, payload.model or "claude-sonnet-4.5")
        
        return OpportunityResponse(**cleaned_opportunities)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/opportunities/market", response_model=OpportunityResponse)
async def map_market_opportunities(payload: MarketOpportunityRequest):
    """Map market-specific opportunities."""
    try:
        raw_opportunities = await OpportunityMapperEngine.map_market_opportunities_async(
            market=payload.market,
            current_position=payload.current_position,
            competitors=payload.competitors,
            budget=payload.budget
        )
        
        cleaned_opportunities = CanonEnforcer.normalize(raw_opportunities)
        DriftMonitor.check(cleaned_opportunities, "claude-sonnet-4.5")
        
        return OpportunityResponse(**cleaned_opportunities)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/opportunities/quick-wins", response_model=OpportunityResponse)
async def find_quick_wins(payload: QuickWinsRequest):
    """Identify quick-win opportunities only."""
    try:
        raw_opportunities = await OpportunityMapperEngine.quick_wins_async(
            situation=payload.situation,
            timeframe=payload.timeframe
        )
        
        cleaned_opportunities = CanonEnforcer.normalize(raw_opportunities)
        DriftMonitor.check(cleaned_opportunities, "claude-sonnet-4.5")
        
        return OpportunityResponse(**cleaned_opportunities)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/opportunities/from-strategy", response_model=OpportunityResponse)
async def opportunities_from_strategy(strategy: StrategyResponse):
    """Extract opportunities from a strategy output."""
    try:
        strategy_dict = strategy.model_dump()
        raw_opportunities = await OpportunityMapperEngine.map_from_strategy_async(strategy_dict)
        
        cleaned_opportunities = CanonEnforcer.normalize(raw_opportunities)
        DriftMonitor.check(cleaned_opportunities, "claude-sonnet-4.5")
        
        return OpportunityResponse(**cleaned_opportunities)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )
