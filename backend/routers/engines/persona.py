"""
Persona Engine endpoints.
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

from services.persona_engine import PersonaEngine
from services.canon_enforcer import CanonEnforcer
from services.drift_monitor import DriftMonitor
from services.error_handler import ErrorHandler, PipelineStage

router = APIRouter(tags=["persona"])


class PersonaRequest(BaseModel):
    audience: str
    context: Optional[str] = None
    product: Optional[str] = None
    industry: Optional[str] = None
    model: Optional[str] = None


class BuyerPersonaRequest(BaseModel):
    role: str
    company_size: Optional[str] = None
    industry: Optional[str] = None
    budget_range: Optional[str] = None


class UserPersonaRequest(BaseModel):
    user_type: str
    use_case: Optional[str] = None
    experience_level: Optional[str] = None


class ICPPersonaRequest(BaseModel):
    product: str
    ideal_customer: str
    market: Optional[str] = None


class MultiplePersonasRequest(BaseModel):
    audiences: List[str]
    context: Optional[str] = None
    product: Optional[str] = None


class PersonaResponse(BaseModel):
    name: str
    role: str
    background: str
    goals: List[str]
    pains: List[str]
    triggers: List[str]
    buying_criteria: List[str]
    objections: List[str]
    preferred_channels: List[str]
    preferred_messaging: List[str]


@router.post("/persona", response_model=PersonaResponse)
async def generate_persona(payload: PersonaRequest):
    """Generate a user/customer persona from an audience description."""
    try:
        raw_persona = await PersonaEngine.generate_persona_async(
            audience=payload.audience,
            context=payload.context,
            product=payload.product,
            industry=payload.industry,
            model=payload.model
        )
        
        cleaned_persona = CanonEnforcer.normalize(raw_persona)
        DriftMonitor.check(cleaned_persona, payload.model or "claude-sonnet-4.5")
        
        return PersonaResponse(**cleaned_persona)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/persona/buyer", response_model=PersonaResponse)
async def generate_buyer_persona(payload: BuyerPersonaRequest):
    """Generate B2B buyer persona."""
    try:
        raw_persona = await PersonaEngine.buyer_persona_async(
            role=payload.role,
            company_size=payload.company_size,
            industry=payload.industry,
            budget_range=payload.budget_range
        )
        
        cleaned_persona = CanonEnforcer.normalize(raw_persona)
        DriftMonitor.check(cleaned_persona, "claude-sonnet-4.5")
        
        return PersonaResponse(**cleaned_persona)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/persona/user", response_model=PersonaResponse)
async def generate_user_persona(payload: UserPersonaRequest):
    """Generate end-user persona."""
    try:
        raw_persona = await PersonaEngine.user_persona_async(
            user_type=payload.user_type,
            use_case=payload.use_case,
            experience_level=payload.experience_level
        )
        
        cleaned_persona = CanonEnforcer.normalize(raw_persona)
        DriftMonitor.check(cleaned_persona, "claude-sonnet-4.5")
        
        return PersonaResponse(**cleaned_persona)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/persona/icp", response_model=PersonaResponse)
async def generate_icp_persona(payload: ICPPersonaRequest):
    """Generate Ideal Customer Profile (ICP) persona."""
    try:
        raw_persona = await PersonaEngine.icp_persona_async(
            product=payload.product,
            ideal_customer=payload.ideal_customer,
            market=payload.market
        )
        
        cleaned_persona = CanonEnforcer.normalize(raw_persona)
        DriftMonitor.check(cleaned_persona, "claude-sonnet-4.5")
        
        return PersonaResponse(**cleaned_persona)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/persona/multiple")
async def generate_multiple_personas(payload: MultiplePersonasRequest):
    """Generate multiple personas at once."""
    try:
        personas = await PersonaEngine.generate_multiple_personas_async(
            audiences=payload.audiences,
            context=payload.context,
            product=payload.product
        )
        
        cleaned_personas = [CanonEnforcer.normalize(p) for p in personas]
        
        return {"personas": cleaned_personas, "count": len(cleaned_personas)}
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.get("/persona/templates")
async def get_persona_templates():
    """Get available persona templates."""
    return PersonaEngine.get_persona_templates()
