"""
Pricing Engine endpoints.
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

from services.pricing_engine import PricingEngine
from services.canon_enforcer import CanonEnforcer
from services.drift_monitor import DriftMonitor
from services.error_handler import ErrorHandler, PipelineStage

router = APIRouter(tags=["pricing"])


class PricingRequest(BaseModel):
    product: str
    description: Optional[str] = None
    target_market: Optional[str] = None
    competitors: Optional[List[str]] = None
    pricing_model: Optional[str] = None
    constraints: Optional[List[str]] = None
    model: Optional[str] = None


class SaaSPricingRequest(BaseModel):
    product: str
    features: List[str]
    target_arr: Optional[str] = None


class APIPricingRequest(BaseModel):
    api_name: str
    use_cases: List[str]
    competitors: Optional[List[str]] = None


class PricingTierModel(BaseModel):
    name: str
    price: str
    ideal_for: str
    limits: List[str]
    features: List[str]
    value_prop: str


class PricingResponse(BaseModel):
    offer_summary: str
    target_segments: List[str]
    pricing_model: str
    tiers: List[PricingTierModel]
    monetization_risks: List[str]
    expansion_opportunities: List[str]
    recommended_entry_tier: str


class StrategyResponse(BaseModel):
    summary: str
    steps: List[str]
    risks: List[str]
    resources: List[str]
    next_action: str


@router.post("/pricing", response_model=PricingResponse)
async def generate_pricing(payload: PricingRequest):
    """Generate pricing structure for a product or service."""
    try:
        raw_pricing = await PricingEngine.generate_pricing_async(
            product=payload.product,
            description=payload.description,
            target_market=payload.target_market,
            competitors=payload.competitors,
            pricing_model=payload.pricing_model,
            constraints=payload.constraints,
            model=payload.model
        )
        
        cleaned_pricing = CanonEnforcer.normalize(raw_pricing)
        DriftMonitor.check(cleaned_pricing, payload.model or "claude-sonnet-4.5")
        
        return PricingResponse(**cleaned_pricing)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/pricing/saas", response_model=PricingResponse)
async def generate_saas_pricing(payload: SaaSPricingRequest):
    """Generate SaaS-specific pricing structure."""
    try:
        raw_pricing = await PricingEngine.saas_pricing_async(
            product=payload.product,
            features=payload.features,
            target_arr=payload.target_arr
        )
        
        cleaned_pricing = CanonEnforcer.normalize(raw_pricing)
        DriftMonitor.check(cleaned_pricing, "claude-sonnet-4.5")
        
        return PricingResponse(**cleaned_pricing)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/pricing/api", response_model=PricingResponse)
async def generate_api_pricing(payload: APIPricingRequest):
    """Generate API-specific pricing structure."""
    try:
        raw_pricing = await PricingEngine.api_pricing_async(
            api_name=payload.api_name,
            use_cases=payload.use_cases,
            competitors=payload.competitors
        )
        
        cleaned_pricing = CanonEnforcer.normalize(raw_pricing)
        DriftMonitor.check(cleaned_pricing, "claude-sonnet-4.5")
        
        return PricingResponse(**cleaned_pricing)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/pricing/from-strategy", response_model=PricingResponse)
async def pricing_from_strategy(strategy: StrategyResponse):
    """Generate pricing from a strategy output."""
    try:
        strategy_dict = strategy.model_dump()
        raw_pricing = await PricingEngine.price_from_strategy_async(strategy_dict)
        
        cleaned_pricing = CanonEnforcer.normalize(raw_pricing)
        DriftMonitor.check(cleaned_pricing, "claude-sonnet-4.5")
        
        return PricingResponse(**cleaned_pricing)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.get("/pricing/models")
async def get_pricing_models():
    """Get available pricing model templates."""
    return PricingEngine.get_pricing_models()
