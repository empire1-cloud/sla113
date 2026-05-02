"""
Evaluator Engine endpoints.
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from services.evaluator_engine import EvaluatorEngine
from services.canon_enforcer import CanonEnforcer
from services.drift_monitor import DriftMonitor
from services.error_handler import ErrorHandler, PipelineStage

router = APIRouter(tags=["evaluator"])


class EvaluationRequest(BaseModel):
    subject: str
    content: str
    criteria: Optional[List[Dict[str, Any]]] = None
    criteria_preset: Optional[str] = None
    context: Optional[str] = None
    model: Optional[str] = None


class IdeaEvaluationRequest(BaseModel):
    idea: str
    context: Optional[str] = None


class OfferEvaluationRequest(BaseModel):
    offer: str
    target_audience: Optional[str] = None


class CompareRequest(BaseModel):
    options: List[Dict[str, str]]
    criteria_preset: Optional[str] = None


class CriterionModel(BaseModel):
    name: str
    score: int
    weight: float
    rationale: str


class EvaluationResponse(BaseModel):
    subject: str
    criteria: List[CriterionModel]
    weighted_score: float
    strengths: List[str]
    weaknesses: List[str]
    improvement_suggestions: List[str]
    go_no_go: str


class StrategyResponse(BaseModel):
    summary: str
    steps: List[str]
    risks: List[str]
    resources: List[str]
    next_action: str


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


@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_subject(payload: EvaluationRequest):
    """Evaluate any subject against criteria."""
    try:
        raw_evaluation = await EvaluatorEngine.evaluate_async(
            subject=payload.subject,
            content=payload.content,
            criteria=payload.criteria,
            criteria_preset=payload.criteria_preset,
            context=payload.context,
            model=payload.model
        )
        
        cleaned_evaluation = CanonEnforcer.normalize(raw_evaluation)
        DriftMonitor.check(cleaned_evaluation, payload.model or "claude-sonnet-4.5")
        
        return EvaluationResponse(**cleaned_evaluation)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/evaluate/idea", response_model=EvaluationResponse)
async def evaluate_idea(payload: IdeaEvaluationRequest):
    """Evaluate a business or product idea."""
    try:
        raw_evaluation = await EvaluatorEngine.evaluate_idea_async(
            idea=payload.idea,
            context=payload.context
        )
        
        cleaned_evaluation = CanonEnforcer.normalize(raw_evaluation)
        DriftMonitor.check(cleaned_evaluation, "claude-sonnet-4.5")
        
        return EvaluationResponse(**cleaned_evaluation)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/evaluate/offer", response_model=EvaluationResponse)
async def evaluate_offer(payload: OfferEvaluationRequest):
    """Evaluate a business offer or proposal."""
    try:
        raw_evaluation = await EvaluatorEngine.evaluate_offer_async(
            offer=payload.offer,
            target_audience=payload.target_audience
        )
        
        cleaned_evaluation = CanonEnforcer.normalize(raw_evaluation)
        DriftMonitor.check(cleaned_evaluation, "claude-sonnet-4.5")
        
        return EvaluationResponse(**cleaned_evaluation)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/evaluate/strategy", response_model=EvaluationResponse)
async def evaluate_strategy(strategy: StrategyResponse):
    """Evaluate a strategy output."""
    try:
        strategy_dict = strategy.model_dump()
        raw_evaluation = await EvaluatorEngine.evaluate_strategy_async(strategy_dict)
        
        cleaned_evaluation = CanonEnforcer.normalize(raw_evaluation)
        DriftMonitor.check(cleaned_evaluation, "claude-sonnet-4.5")
        
        return EvaluationResponse(**cleaned_evaluation)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/evaluate/plan", response_model=EvaluationResponse)
async def evaluate_plan(plan: PlanResponse):
    """Evaluate an execution plan."""
    try:
        plan_dict = plan.model_dump()
        raw_evaluation = await EvaluatorEngine.evaluate_plan_async(plan_dict)
        
        cleaned_evaluation = CanonEnforcer.normalize(raw_evaluation)
        DriftMonitor.check(cleaned_evaluation, "claude-sonnet-4.5")
        
        return EvaluationResponse(**cleaned_evaluation)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/evaluate/compare")
async def compare_options(payload: CompareRequest):
    """Compare multiple options and rank them."""
    try:
        comparison = await EvaluatorEngine.compare_async(
            options=payload.options,
            criteria_preset=payload.criteria_preset
        )
        
        return comparison
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.get("/evaluate/presets")
async def get_evaluation_presets():
    """Get available evaluation criteria presets."""
    return EvaluatorEngine.get_available_presets()
