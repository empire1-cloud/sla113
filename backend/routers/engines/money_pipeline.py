"""
Universal Money Pipeline Engine endpoints.
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

from services.money_pipeline_engine import MoneyPipelineEngine
from services.canon_enforcer import CanonEnforcer
from services.drift_monitor import DriftMonitor
from services.error_handler import ErrorHandler, PipelineStage

router = APIRouter(tags=["money-pipeline"])


class MoneyPipelineRequest(BaseModel):
    idea: str
    context: Optional[str] = None
    industry: Optional[str] = None
    target_revenue: Optional[str] = None
    constraints: Optional[List[str]] = None
    model: Optional[str] = None


class SaaSPipelineRequest(BaseModel):
    product: str
    target_users: str
    target_arr: Optional[str] = None


class ServicePipelineRequest(BaseModel):
    service: str
    target_clients: str
    delivery_model: Optional[str] = None


class EcommercePipelineRequest(BaseModel):
    product: str
    target_market: str
    price_range: Optional[str] = None


class APIPipelineRequest(BaseModel):
    api_concept: str
    use_cases: List[str]
    target_developers: Optional[str] = None


class PricingTierModel(BaseModel):
    name: str
    price: str
    features: List[str]


class MarketAnalysisModel(BaseModel):
    target_segments: List[str]
    pain_points: List[str]
    demand_drivers: List[str]
    competitive_landscape: List[str]
    positioning_opportunity: str


class OpportunityMapModel(BaseModel):
    primary_opportunities: List[str]
    secondary_opportunities: List[str]
    high_leverage_moves: List[str]


class PricingModelModel(BaseModel):
    tiers: List[PricingTierModel]
    value_metrics: List[str]
    monetization_strategy: str


class BusinessModelModel(BaseModel):
    core_offer: str
    delivery_model: str
    retention_model: str
    expansion_model: str


class ProductBlueprintModel(BaseModel):
    core_features: List[str]
    differentiators: List[str]
    technical_requirements: List[str]
    dependencies: List[str]


class ExecutionPlanModel(BaseModel):
    phase_1: List[str]
    phase_2: List[str]
    phase_3: List[str]
    critical_path: List[str]


class ForecastModel(BaseModel):
    revenue_projection: str
    growth_drivers: List[str]
    risks: List[str]
    mitigations: List[str]


class MarketingFunnelModel(BaseModel):
    top_of_funnel: List[str]
    middle_of_funnel: List[str]
    bottom_of_funnel: List[str]


class LaunchStrategyModel(BaseModel):
    pre_launch: List[str]
    launch: List[str]
    post_launch: List[str]


class MoneyPipelineResponse(BaseModel):
    market_analysis: MarketAnalysisModel
    opportunity_map: OpportunityMapModel
    pricing_model: PricingModelModel
    business_model: BusinessModelModel
    product_blueprint: ProductBlueprintModel
    execution_plan: ExecutionPlanModel
    forecast: ForecastModel
    marketing_funnel: MarketingFunnelModel
    launch_strategy: LaunchStrategyModel


@router.post("/money-pipeline", response_model=MoneyPipelineResponse)
async def generate_money_pipeline(payload: MoneyPipelineRequest):
    """Transform any idea into a complete, monetizable, execution-ready system."""
    try:
        raw_pipeline = await MoneyPipelineEngine.generate_pipeline_async(
            idea=payload.idea,
            context=payload.context,
            industry=payload.industry,
            target_revenue=payload.target_revenue,
            constraints=payload.constraints,
            model=payload.model
        )
        
        cleaned_pipeline = CanonEnforcer.normalize(raw_pipeline)
        DriftMonitor.check(cleaned_pipeline, payload.model or "claude-sonnet-4.5")
        
        return MoneyPipelineResponse(**cleaned_pipeline)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/money-pipeline/quick")
async def quick_monetize(idea: str, model: Optional[str] = None):
    """Quick monetization analysis with minimal parameters."""
    try:
        raw_pipeline = await MoneyPipelineEngine.quick_monetize_async(
            idea=idea,
            model=model
        )
        
        cleaned_pipeline = CanonEnforcer.normalize(raw_pipeline)
        
        return cleaned_pipeline
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/money-pipeline/saas", response_model=MoneyPipelineResponse)
async def saas_money_pipeline(payload: SaaSPipelineRequest):
    """Generate SaaS-specific money pipeline."""
    try:
        raw_pipeline = await MoneyPipelineEngine.saas_pipeline_async(
            product=payload.product,
            target_users=payload.target_users,
            target_arr=payload.target_arr
        )
        
        cleaned_pipeline = CanonEnforcer.normalize(raw_pipeline)
        DriftMonitor.check(cleaned_pipeline, "claude-sonnet-4.5")
        
        return MoneyPipelineResponse(**cleaned_pipeline)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/money-pipeline/service", response_model=MoneyPipelineResponse)
async def service_money_pipeline(payload: ServicePipelineRequest):
    """Generate service business money pipeline."""
    try:
        raw_pipeline = await MoneyPipelineEngine.service_pipeline_async(
            service=payload.service,
            target_clients=payload.target_clients,
            delivery_model=payload.delivery_model
        )
        
        cleaned_pipeline = CanonEnforcer.normalize(raw_pipeline)
        DriftMonitor.check(cleaned_pipeline, "claude-sonnet-4.5")
        
        return MoneyPipelineResponse(**cleaned_pipeline)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/money-pipeline/ecommerce", response_model=MoneyPipelineResponse)
async def ecommerce_money_pipeline(payload: EcommercePipelineRequest):
    """Generate e-commerce money pipeline."""
    try:
        raw_pipeline = await MoneyPipelineEngine.ecommerce_pipeline_async(
            product=payload.product,
            target_market=payload.target_market,
            price_range=payload.price_range
        )
        
        cleaned_pipeline = CanonEnforcer.normalize(raw_pipeline)
        DriftMonitor.check(cleaned_pipeline, "claude-sonnet-4.5")
        
        return MoneyPipelineResponse(**cleaned_pipeline)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/money-pipeline/api", response_model=MoneyPipelineResponse)
async def api_money_pipeline(payload: APIPipelineRequest):
    """Generate API product money pipeline."""
    try:
        raw_pipeline = await MoneyPipelineEngine.api_pipeline_async(
            api_concept=payload.api_concept,
            use_cases=payload.use_cases,
            target_developers=payload.target_developers
        )
        
        cleaned_pipeline = CanonEnforcer.normalize(raw_pipeline)
        DriftMonitor.check(cleaned_pipeline, "claude-sonnet-4.5")
        
        return MoneyPipelineResponse(**cleaned_pipeline)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )
