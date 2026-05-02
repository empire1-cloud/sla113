"""
Blueprint Engine endpoints.
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

from services.blueprint_engine import BlueprintEngine
from services.canon_enforcer import CanonEnforcer
from services.drift_monitor import DriftMonitor
from services.error_handler import ErrorHandler, PipelineStage

router = APIRouter(tags=["blueprint"])


class BlueprintRequest(BaseModel):
    system_description: str
    requirements: Optional[List[str]] = None
    constraints: Optional[List[str]] = None
    tech_stack: Optional[List[str]] = None
    scale: Optional[str] = None
    model: Optional[str] = None


class SaaSBlueprintRequest(BaseModel):
    product_name: str
    core_features: List[str]
    user_types: Optional[List[str]] = None


class APIBlueprintRequest(BaseModel):
    api_name: str
    endpoints: List[str]
    expected_load: Optional[str] = None


class MicroservicesBlueprintRequest(BaseModel):
    system_name: str
    domains: List[str]
    shared_concerns: Optional[List[str]] = None


class ComponentModel(BaseModel):
    name: str
    type: str
    responsibilities: List[str]
    inputs: List[str]
    outputs: List[str]
    dependencies: List[str]


class DataFlowModel(BaseModel):
    from_component: Optional[str] = None
    to: str
    data: str
    frequency: str


class BlueprintResponse(BaseModel):
    objective: str
    components: List[ComponentModel]
    data_flows: List[DataFlowModel]
    constraints: List[str]
    risks: List[str]


class StrategyResponse(BaseModel):
    summary: str
    steps: List[str]
    risks: List[str]
    resources: List[str]
    next_action: str


@router.post("/blueprint", response_model=BlueprintResponse)
async def generate_blueprint(payload: BlueprintRequest):
    """Generate a system architecture blueprint."""
    try:
        raw_blueprint = await BlueprintEngine.generate_blueprint_async(
            system_description=payload.system_description,
            requirements=payload.requirements,
            constraints=payload.constraints,
            tech_stack=payload.tech_stack,
            scale=payload.scale,
            model=payload.model
        )
        
        cleaned_blueprint = CanonEnforcer.normalize(raw_blueprint)
        DriftMonitor.check(cleaned_blueprint, payload.model or "gpt-5.2")
        
        return BlueprintResponse(**cleaned_blueprint)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/blueprint/saas", response_model=BlueprintResponse)
async def generate_saas_blueprint(payload: SaaSBlueprintRequest):
    """Generate SaaS product architecture blueprint."""
    try:
        raw_blueprint = await BlueprintEngine.saas_blueprint_async(
            product_name=payload.product_name,
            core_features=payload.core_features,
            user_types=payload.user_types
        )
        
        cleaned_blueprint = CanonEnforcer.normalize(raw_blueprint)
        DriftMonitor.check(cleaned_blueprint, "gpt-5.2")
        
        return BlueprintResponse(**cleaned_blueprint)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/blueprint/api", response_model=BlueprintResponse)
async def generate_api_blueprint(payload: APIBlueprintRequest):
    """Generate API system architecture blueprint."""
    try:
        raw_blueprint = await BlueprintEngine.api_blueprint_async(
            api_name=payload.api_name,
            endpoints=payload.endpoints,
            expected_load=payload.expected_load
        )
        
        cleaned_blueprint = CanonEnforcer.normalize(raw_blueprint)
        DriftMonitor.check(cleaned_blueprint, "gpt-5.2")
        
        return BlueprintResponse(**cleaned_blueprint)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/blueprint/microservices", response_model=BlueprintResponse)
async def generate_microservices_blueprint(payload: MicroservicesBlueprintRequest):
    """Generate microservices architecture blueprint."""
    try:
        raw_blueprint = await BlueprintEngine.microservices_blueprint_async(
            system_name=payload.system_name,
            domains=payload.domains,
            shared_concerns=payload.shared_concerns
        )
        
        cleaned_blueprint = CanonEnforcer.normalize(raw_blueprint)
        DriftMonitor.check(cleaned_blueprint, "gpt-5.2")
        
        return BlueprintResponse(**cleaned_blueprint)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/blueprint/from-strategy", response_model=BlueprintResponse)
async def blueprint_from_strategy(strategy: StrategyResponse):
    """Generate system blueprint from a strategy output."""
    try:
        strategy_dict = strategy.model_dump()
        raw_blueprint = await BlueprintEngine.blueprint_from_strategy_async(strategy_dict)
        
        cleaned_blueprint = CanonEnforcer.normalize(raw_blueprint)
        DriftMonitor.check(cleaned_blueprint, "gpt-5.2")
        
        return BlueprintResponse(**cleaned_blueprint)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.get("/blueprint/component-types")
async def get_component_types():
    """Get available component types for blueprints."""
    return BlueprintEngine.get_component_types()
