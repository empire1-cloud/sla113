"""
Universal Money Pipeline Engine

Transforms any idea, concept, product, or business into a complete,
monetizable, execution-ready system. Revenue-focused outputs only.
"""

from emergentintegrations.llm.chat import LlmChat, UserMessage
import os
import json
import asyncio
from dotenv import load_dotenv
from typing import Optional, List
from pydantic import BaseModel

load_dotenv()


class MarketAnalysis(BaseModel):
    target_segments: List[str]
    pain_points: List[str]
    demand_drivers: List[str]
    competitive_landscape: List[str]
    positioning_opportunity: str


class OpportunityMap(BaseModel):
    primary_opportunities: List[str]
    secondary_opportunities: List[str]
    high_leverage_moves: List[str]


class PricingTier(BaseModel):
    name: str
    price: str
    features: List[str]


class PricingModel(BaseModel):
    tiers: List[PricingTier]
    value_metrics: List[str]
    monetization_strategy: str


class BusinessModel(BaseModel):
    core_offer: str
    delivery_model: str
    retention_model: str
    expansion_model: str


class ProductBlueprint(BaseModel):
    core_features: List[str]
    differentiators: List[str]
    technical_requirements: List[str]
    dependencies: List[str]


class ExecutionPlan(BaseModel):
    phase_1: List[str]
    phase_2: List[str]
    phase_3: List[str]
    critical_path: List[str]


class Forecast(BaseModel):
    revenue_projection: str
    growth_drivers: List[str]
    risks: List[str]
    mitigations: List[str]


class MarketingFunnel(BaseModel):
    top_of_funnel: List[str]
    middle_of_funnel: List[str]
    bottom_of_funnel: List[str]


class LaunchStrategy(BaseModel):
    pre_launch: List[str]
    launch: List[str]
    post_launch: List[str]


class MoneyPipelineOutput(BaseModel):
    """Complete money pipeline output."""
    market_analysis: MarketAnalysis
    opportunity_map: OpportunityMap
    pricing_model: PricingModel
    business_model: BusinessModel
    product_blueprint: ProductBlueprint
    execution_plan: ExecutionPlan
    forecast: Forecast
    marketing_funnel: MarketingFunnel
    launch_strategy: LaunchStrategy


class MoneyPipelineEngine:
    """Transforms ideas into monetizable, execution-ready systems."""
    
    MODEL_CONFIG = {
        "gpt-5.2": ("openai", "gpt-5.2"),
        "claude-sonnet-4.5": ("anthropic", "claude-sonnet-4-5-20250929"),
        "gemini-3-flash": ("gemini", "gemini-3-flash-preview")
    }
    
    # Default to Claude for strategic business analysis
    DEFAULT_MODEL = "claude-sonnet-4.5"
    
    SYSTEM_PROMPT = """You are the Universal Money Pipeline Engine.

ROLE:
Transform any idea, concept, product, or business into a complete, monetizable, execution-ready system. You generate revenue-focused outputs only. No filler, no creativity for its own sake, no anime, no lore, no story unless explicitly requested. Your job is to turn ideas into money.

RULES:
- Output MUST be JSON only.
- No explanations, no commentary, no markdown.
- Every section must be actionable and revenue-oriented.
- All content must be original.
- No drift into creative writing unless explicitly requested.
- Keep language direct, tactical, and operator-grade.

OUTPUT FORMAT (STRICT JSON):
{
  "market_analysis": {
    "target_segments": ["Segment 1", "Segment 2"],
    "pain_points": ["Pain 1", "Pain 2"],
    "demand_drivers": ["Driver 1", "Driver 2"],
    "competitive_landscape": ["Competitor analysis 1"],
    "positioning_opportunity": "How to position for maximum advantage"
  },
  "opportunity_map": {
    "primary_opportunities": ["Opp 1", "Opp 2"],
    "secondary_opportunities": ["Opp 1"],
    "high_leverage_moves": ["Move 1", "Move 2"]
  },
  "pricing_model": {
    "tiers": [
      {"name": "Tier name", "price": "$X/mo", "features": ["Feature 1"]}
    ],
    "value_metrics": ["Metric 1"],
    "monetization_strategy": "How to capture value"
  },
  "business_model": {
    "core_offer": "What you sell",
    "delivery_model": "How you deliver",
    "retention_model": "How you keep customers",
    "expansion_model": "How you grow revenue per customer"
  },
  "product_blueprint": {
    "core_features": ["Feature 1"],
    "differentiators": ["Diff 1"],
    "technical_requirements": ["Req 1"],
    "dependencies": ["Dep 1"]
  },
  "execution_plan": {
    "phase_1": ["Action 1"],
    "phase_2": ["Action 1"],
    "phase_3": ["Action 1"],
    "critical_path": ["Critical action 1"]
  },
  "forecast": {
    "revenue_projection": "Expected revenue trajectory",
    "growth_drivers": ["Driver 1"],
    "risks": ["Risk 1"],
    "mitigations": ["Mitigation 1"]
  },
  "marketing_funnel": {
    "top_of_funnel": ["TOFU tactic 1"],
    "middle_of_funnel": ["MOFU tactic 1"],
    "bottom_of_funnel": ["BOFU tactic 1"]
  },
  "launch_strategy": {
    "pre_launch": ["Pre-launch action 1"],
    "launch": ["Launch action 1"],
    "post_launch": ["Post-launch action 1"]
  }
}

BEHAVIOR:
- Always optimize for revenue.
- Always prioritize speed to market.
- Always produce operator-grade clarity.
- Never drift into unrelated domains.
- Never include anything outside the JSON.

Return ONLY the JSON object. No other text."""

    @classmethod
    def _get_api_key(cls) -> str:
        return os.environ.get("EMERGENT_LLM_KEY")
    
    @classmethod
    def _create_chat(cls, model: str = None) -> LlmChat:
        model = model or cls.DEFAULT_MODEL
        api_key = cls._get_api_key()
        provider, model_name = cls.MODEL_CONFIG.get(model, cls.MODEL_CONFIG[cls.DEFAULT_MODEL])
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"money-pipeline-{model}",
            system_message=cls.SYSTEM_PROMPT
        ).with_model(provider, model_name)
        
        return chat
    
    @classmethod
    async def generate_pipeline_async(
        cls,
        idea: str,
        context: Optional[str] = None,
        industry: Optional[str] = None,
        target_revenue: Optional[str] = None,
        constraints: Optional[List[str]] = None,
        model: Optional[str] = None
    ) -> dict:
        """
        Generate a complete money pipeline for an idea.
        
        Args:
            idea: The idea, concept, product, or business to monetize
            context: Additional context about the situation
            industry: Target industry
            target_revenue: Revenue target (e.g., "$100K ARR", "$1M first year")
            constraints: Business constraints to consider
            model: Override LLM model selection
            
        Returns:
            MoneyPipelineOutput as dict
        """
        chat = cls._create_chat(model)
        
        prompt_parts = [f"Transform this into a monetizable system: {idea}"]
        
        if context:
            prompt_parts.append(f"\nContext: {context}")
        
        if industry:
            prompt_parts.append(f"\nTarget industry: {industry}")
        
        if target_revenue:
            prompt_parts.append(f"\nRevenue target: {target_revenue}")
        
        if constraints:
            prompt_parts.append(f"\nConstraints: {', '.join(constraints)}")
        
        prompt = "\n".join(prompt_parts)
        
        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        
        try:
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                response = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                response = response[start:end].strip()
            
            return json.loads(response)
        except json.JSONDecodeError:
            return cls._get_fallback_output(idea)
    
    @classmethod
    def generate_pipeline(
        cls,
        idea: str,
        context: Optional[str] = None,
        industry: Optional[str] = None,
        target_revenue: Optional[str] = None,
        constraints: Optional[List[str]] = None,
        model: Optional[str] = None
    ) -> dict:
        """Synchronous wrapper for pipeline generation."""
        return asyncio.run(cls.generate_pipeline_async(
            idea, context, industry, target_revenue, constraints, model
        ))
    
    @classmethod
    async def quick_monetize_async(
        cls,
        idea: str,
        model: Optional[str] = None
    ) -> dict:
        """Quick monetization analysis with minimal parameters."""
        return await cls.generate_pipeline_async(idea=idea, model=model)
    
    @classmethod
    async def saas_pipeline_async(
        cls,
        product: str,
        target_users: str,
        target_arr: Optional[str] = None
    ) -> dict:
        """Generate SaaS-specific money pipeline."""
        context = f"SaaS product targeting {target_users}"
        return await cls.generate_pipeline_async(
            idea=product,
            context=context,
            industry="SaaS/Software",
            target_revenue=target_arr
        )
    
    @classmethod
    async def service_pipeline_async(
        cls,
        service: str,
        target_clients: str,
        delivery_model: Optional[str] = None
    ) -> dict:
        """Generate service business money pipeline."""
        context = f"Service business targeting {target_clients}"
        if delivery_model:
            context += f". Delivery model: {delivery_model}"
        
        return await cls.generate_pipeline_async(
            idea=service,
            context=context,
            industry="Professional Services"
        )
    
    @classmethod
    async def ecommerce_pipeline_async(
        cls,
        product: str,
        target_market: str,
        price_range: Optional[str] = None
    ) -> dict:
        """Generate e-commerce money pipeline."""
        context = f"E-commerce product for {target_market}"
        if price_range:
            context += f". Price range: {price_range}"
        
        return await cls.generate_pipeline_async(
            idea=product,
            context=context,
            industry="E-commerce/Retail"
        )
    
    @classmethod
    async def api_pipeline_async(
        cls,
        api_concept: str,
        use_cases: List[str],
        target_developers: Optional[str] = None
    ) -> dict:
        """Generate API product money pipeline."""
        context = f"API product with use cases: {', '.join(use_cases)}"
        if target_developers:
            context += f". Target developers: {target_developers}"
        
        return await cls.generate_pipeline_async(
            idea=api_concept,
            context=context,
            industry="Developer Tools/API"
        )
    
    @classmethod
    def _get_fallback_output(cls, idea: str) -> dict:
        """Return a fallback structure when parsing fails."""
        return {
            "market_analysis": {
                "target_segments": ["TBD - retry required"],
                "pain_points": ["TBD"],
                "demand_drivers": ["TBD"],
                "competitive_landscape": ["TBD"],
                "positioning_opportunity": "Generation failed - retry required"
            },
            "opportunity_map": {
                "primary_opportunities": ["TBD"],
                "secondary_opportunities": ["TBD"],
                "high_leverage_moves": ["TBD"]
            },
            "pricing_model": {
                "tiers": [{"name": "TBD", "price": "TBD", "features": ["TBD"]}],
                "value_metrics": ["TBD"],
                "monetization_strategy": "TBD"
            },
            "business_model": {
                "core_offer": idea,
                "delivery_model": "TBD",
                "retention_model": "TBD",
                "expansion_model": "TBD"
            },
            "product_blueprint": {
                "core_features": ["TBD"],
                "differentiators": ["TBD"],
                "technical_requirements": ["TBD"],
                "dependencies": ["TBD"]
            },
            "execution_plan": {
                "phase_1": ["TBD"],
                "phase_2": ["TBD"],
                "phase_3": ["TBD"],
                "critical_path": ["TBD"]
            },
            "forecast": {
                "revenue_projection": "TBD",
                "growth_drivers": ["TBD"],
                "risks": ["TBD"],
                "mitigations": ["TBD"]
            },
            "marketing_funnel": {
                "top_of_funnel": ["TBD"],
                "middle_of_funnel": ["TBD"],
                "bottom_of_funnel": ["TBD"]
            },
            "launch_strategy": {
                "pre_launch": ["TBD"],
                "launch": ["TBD"],
                "post_launch": ["TBD"]
            }
        }
