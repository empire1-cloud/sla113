from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio

from services.router import RoutingEngine, RoutingDecision
from services.strategy_engine import StrategyEngine
from services.canon_enforcer import CanonEnforcer
from services.drift_monitor import DriftMonitor
from services.error_handler import ErrorHandler, PipelineStage
from services.plan_builder import PlanBuilderEngine
from services.analysis_engine import AnalysisEngine
from services.opportunity_mapper import OpportunityMapperEngine
from services.evaluator_engine import EvaluatorEngine
from services.pricing_engine import PricingEngine
from services.blueprint_engine import BlueprintEngine
from services.persona_engine import PersonaEngine
from services.anime_character_engine import AnimeCharacterEngine
from services.hybrid_core import get_core, TaskType

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

class PlanRequest(BaseModel):
    goal: str
    strategy: Optional[dict] = None
    context: Optional[str] = None
    model: Optional[str] = None

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

class EvaluationRequest(BaseModel):
    subject: str
    content: str
    criteria: Optional[List[Dict[str, Any]]] = None
    criteria_preset: Optional[str] = None  # strategy, idea, plan, offer
    context: Optional[str] = None
    model: Optional[str] = None

class IdeaEvaluationRequest(BaseModel):
    idea: str
    context: Optional[str] = None

class OfferEvaluationRequest(BaseModel):
    offer: str
    target_audience: Optional[str] = None

class CompareRequest(BaseModel):
    options: List[Dict[str, str]]  # [{"name": "...", "content": "..."}]
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

class AnimeCharacterRequest(BaseModel):
    concept: str
    role: Optional[str] = None
    genre: Optional[str] = None
    abilities_type: Optional[str] = None
    context: Optional[str] = None
    model: Optional[str] = None

class ProtagonistRequest(BaseModel):
    concept: str
    genre: Optional[str] = None
    abilities_type: Optional[str] = None

class AntagonistRequest(BaseModel):
    concept: str
    genre: Optional[str] = None
    protagonist: Optional[str] = None

class CastRequest(BaseModel):
    story_concept: str
    genre: Optional[str] = None
    cast_size: Optional[int] = 5

class CharacterRelationshipsModel(BaseModel):
    allies: List[str]
    rivals: List[str]
    enemies: List[str]

class AnimeCharacterResponse(BaseModel):
    name: str
    role: str
    appearance: str
    personality: List[str]
    abilities: List[str]
    motivations: List[str]
    backstory: str
    relationships: CharacterRelationshipsModel
    arc: str

@router.post("/strategy", response_model=StrategyResponse)
async def generate_strategy(payload: StrategyRequest):
    """Generate an actionable strategy using the hybrid AI pipeline."""
    current_stage = None
    try:
        # 1. ROUTING ENGINE
        current_stage = PipelineStage.ROUTING
        routing_decision = RoutingEngine.route(payload.goal, payload.force_model)
        
        # 2. STRATEGY ENGINE
        current_stage = PipelineStage.STRATEGY
        raw_output = await StrategyEngine.generate_async(
            model=routing_decision.model,
            goal=payload.goal,
            context=payload.context,
            tone=payload.tone
        )
        
        # 3. CANON ENFORCER
        current_stage = PipelineStage.CANON
        cleaned_output = CanonEnforcer.normalize(raw_output)
        
        # 4. DRIFT MONITOR
        current_stage = PipelineStage.DRIFT
        DriftMonitor.check(cleaned_output, routing_decision.model)
        
        # 5. RETURN FINAL JSON
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
        "engines": [
            "hybrid_intelligence_core",
            "routing_engine",
            "strategy_engine",
            "plan_builder_engine",
            "analysis_engine",
            "opportunity_mapper_engine",
            "evaluator_engine",
            "pricing_engine",
            "blueprint_engine",
            "persona_engine",
            "anime_character_engine",
            "canon_enforcer",
            "drift_monitor",
            "error_handler"
        ]
    }

# ============================================
# ANALYSIS ENGINE ENDPOINTS
# ============================================

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
        
        # Apply canon enforcement
        cleaned_analysis = CanonEnforcer.normalize(raw_analysis)
        
        # Monitor drift
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

# ============================================
# OPPORTUNITY MAPPER ENGINE ENDPOINTS
# ============================================

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
        
        # Apply canon enforcement
        cleaned_opportunities = CanonEnforcer.normalize(raw_opportunities)
        
        # Monitor drift
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

# ============================================
# EVALUATOR ENGINE ENDPOINTS
# ============================================

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

# ============================================
# PRICING ENGINE ENDPOINTS
# ============================================

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

# ============================================
# BLUEPRINT ENGINE ENDPOINTS
# ============================================

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

# ============================================
# PERSONA ENGINE ENDPOINTS
# ============================================

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

# ============================================
# ANIME CHARACTER ENGINE ENDPOINTS
# ============================================

@router.post("/anime/character", response_model=AnimeCharacterResponse)
async def generate_anime_character(payload: AnimeCharacterRequest):
    """Generate an original anime character."""
    try:
        raw_character = await AnimeCharacterEngine.generate_character_async(
            concept=payload.concept,
            role=payload.role,
            genre=payload.genre,
            abilities_type=payload.abilities_type,
            context=payload.context,
            model=payload.model
        )
        
        cleaned_character = CanonEnforcer.normalize(raw_character)
        DriftMonitor.check(cleaned_character, payload.model or "claude-sonnet-4.5")
        
        return AnimeCharacterResponse(**cleaned_character)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )

@router.post("/anime/protagonist", response_model=AnimeCharacterResponse)
async def generate_protagonist(payload: ProtagonistRequest):
    """Generate an anime protagonist character."""
    try:
        raw_character = await AnimeCharacterEngine.generate_protagonist_async(
            concept=payload.concept,
            genre=payload.genre,
            abilities_type=payload.abilities_type
        )
        
        cleaned_character = CanonEnforcer.normalize(raw_character)
        DriftMonitor.check(cleaned_character, "claude-sonnet-4.5")
        
        return AnimeCharacterResponse(**cleaned_character)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )

@router.post("/anime/antagonist", response_model=AnimeCharacterResponse)
async def generate_antagonist(payload: AntagonistRequest):
    """Generate an anime antagonist/villain character."""
    try:
        raw_character = await AnimeCharacterEngine.generate_antagonist_async(
            concept=payload.concept,
            genre=payload.genre,
            protagonist=payload.protagonist
        )
        
        cleaned_character = CanonEnforcer.normalize(raw_character)
        DriftMonitor.check(cleaned_character, "claude-sonnet-4.5")
        
        return AnimeCharacterResponse(**cleaned_character)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )

@router.post("/anime/cast")
async def generate_cast(payload: CastRequest):
    """Generate a full cast of anime characters for a story."""
    try:
        characters = await AnimeCharacterEngine.generate_cast_async(
            story_concept=payload.story_concept,
            genre=payload.genre,
            cast_size=payload.cast_size or 5
        )
        
        cleaned_characters = [CanonEnforcer.normalize(c) for c in characters]
        
        return {"cast": cleaned_characters, "count": len(cleaned_characters)}
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )

@router.get("/anime/archetypes")
async def get_character_archetypes():
    """Get available character archetypes."""
    return AnimeCharacterEngine.get_archetypes()

@router.get("/anime/genres")
async def get_anime_genres():
    """Get available anime genres."""
    return AnimeCharacterEngine.get_genres()

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
        
        # Apply canon enforcement
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
        # 1. Generate strategy
        routing_decision = RoutingEngine.route(payload.goal, payload.force_model)
        raw_strategy = await StrategyEngine.generate_async(
            model=routing_decision.model,
            goal=payload.goal,
            context=payload.context,
            tone=payload.tone
        )
        cleaned_strategy = CanonEnforcer.normalize(raw_strategy)
        
        # 2. Convert to plan
        plan = await PlanBuilderEngine.convert_strategy_to_plan_async(cleaned_strategy)
        cleaned_plan = CanonEnforcer.normalize(plan)
        
        # 3. Monitor drift
        DriftMonitor.check(cleaned_plan, routing_decision.model)
        
        return PlanResponse(**cleaned_plan)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )

# ============================================
# HYBRID INTELLIGENCE CORE ENDPOINTS
# ============================================

class CoreRequest(BaseModel):
    """Unified request for Hybrid Intelligence Core."""
    prompt: str
    task_type: Optional[str] = None  # strategy, plan, analysis, code, quick
    context: Optional[str] = None
    force_model: Optional[str] = None

class CoreResponse(BaseModel):
    """Unified response from Hybrid Intelligence Core."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@router.post("/core/execute", response_model=CoreResponse)
async def core_execute(payload: CoreRequest):
    """
    Execute via Hybrid Intelligence Core.
    
    The Core automatically:
    1. Classifies the task type
    2. Routes to optimal model
    3. Executes appropriate engine
    4. Enforces canon rules
    5. Monitors drift
    6. Handles errors
    """
    core = get_core()
    
    # Parse task type if provided
    task_type = None
    if payload.task_type:
        try:
            task_type = TaskType(payload.task_type)
        except ValueError:
            pass
    
    result = await core.execute(
        prompt=payload.prompt,
        task_type=task_type,
        context=payload.context,
        force_model=payload.force_model
    )
    
    if result.success:
        return CoreResponse(
            success=True,
            data=result.data,
            metadata=result.metadata
        )
    else:
        return JSONResponse(
            status_code=500,
            content=result.error
        )

@router.post("/core/strategy-to-plan", response_model=CoreResponse)
async def core_strategy_to_plan(payload: CoreRequest):
    """Execute full strategy → plan pipeline via Core."""
    core = get_core()
    
    result = await core.execute_strategy_to_plan(
        goal=payload.prompt,
        context=payload.context,
        force_model=payload.force_model
    )
    
    if result.success:
        return CoreResponse(
            success=True,
            data=result.data,
            metadata=result.metadata
        )
    else:
        return JSONResponse(
            status_code=500,
            content=result.error
        )

@router.get("/core/status")
async def core_status():
    """Get Hybrid Intelligence Core system status."""
    core = get_core()
    return core.get_system_status()

@router.get("/core/log")
async def core_execution_log(limit: int = 50):
    """Get recent execution log from the Core."""
    core = get_core()
    return {
        "log": core.get_execution_log(limit),
        "total_executions": len(core.execution_log)
    }

