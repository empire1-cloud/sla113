"""
Pricing Engine

Proposes clear, defensible pricing structures for products or services.
Anchors pricing to value, includes tiers, segments, and rationale.
"""

from emergentintegrations.llm.chat import LlmChat, UserMessage
import os
import json
import asyncio
from dotenv import load_dotenv
from typing import Optional, List
from pydantic import BaseModel

load_dotenv()


class PricingTier(BaseModel):
    """Single pricing tier."""
    name: str
    price: str
    ideal_for: str
    limits: List[str]
    features: List[str]
    value_prop: str


class PricingStructure(BaseModel):
    """Complete pricing structure output."""
    offer_summary: str
    target_segments: List[str]
    pricing_model: str  # subscription | usage-based | hybrid | one-time
    tiers: List[PricingTier]
    monetization_risks: List[str]
    expansion_opportunities: List[str]
    recommended_entry_tier: str


class PricingEngine:
    """Proposes pricing structures anchored to value."""
    
    MODEL_CONFIG = {
        "gpt-5.2": ("openai", "gpt-5.2"),
        "claude-sonnet-4.5": ("anthropic", "claude-sonnet-4-5-20250929"),
        "gemini-3-flash": ("gemini", "gemini-3-flash-preview")
    }
    
    # Default to Claude for pricing (strategic reasoning)
    DEFAULT_MODEL = "claude-sonnet-4.5"
    
    # Pricing model templates
    PRICING_MODELS = {
        "subscription": {
            "description": "Recurring monthly/annual payments",
            "best_for": ["SaaS products", "Content platforms", "Service businesses"],
            "typical_tiers": ["Free/Freemium", "Starter", "Professional", "Enterprise"]
        },
        "usage-based": {
            "description": "Pay per use/consumption",
            "best_for": ["API products", "Infrastructure", "Transactional services"],
            "typical_tiers": ["Pay-as-you-go", "Volume discounts", "Committed use"]
        },
        "hybrid": {
            "description": "Base subscription + usage overage",
            "best_for": ["API + features", "Platform + compute", "Tools + resources"],
            "typical_tiers": ["Base + overage", "Included quota + extra", "Platform fee + usage"]
        },
        "one-time": {
            "description": "Single purchase",
            "best_for": ["Digital products", "Courses", "Templates", "Licenses"],
            "typical_tiers": ["Basic", "Standard", "Premium", "Lifetime"]
        }
    }
    
    SYSTEM_PROMPT = """You are the Pricing Engine.

Your job is to propose a clear, defensible pricing structure for a product or service.

RULES:
1. Always return valid JSON only — no markdown, no explanations outside JSON.
2. Anchor pricing to value delivered, not just cost to produce.
3. Include 3-4 tiers targeting different segments.
4. No disclaimers, no model identity, no filler.
5. Be specific with prices — use real numbers, not ranges.
6. Consider psychological pricing (e.g., $29 not $30).
7. Include clear differentiation between tiers.

OUTPUT FORMAT (JSON ONLY):
{
  "offer_summary": "What is being priced.",
  "target_segments": ["Segment 1", "Segment 2", "Segment 3"],
  "pricing_model": "subscription | usage-based | hybrid | one-time",
  "tiers": [
    {
      "name": "Tier name",
      "price": "e.g. $29/month",
      "ideal_for": "Who this tier is for.",
      "limits": ["Limit 1", "Limit 2"],
      "features": ["Feature 1", "Feature 2"],
      "value_prop": "Why this tier makes sense."
    }
  ],
  "monetization_risks": ["Risk 1", "Risk 2"],
  "expansion_opportunities": ["Upsell opportunity 1", "Cross-sell opportunity 2"],
  "recommended_entry_tier": "Tier name to push first."
}

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
            session_id=f"pricing-{model}",
            system_message=cls.SYSTEM_PROMPT
        ).with_model(provider, model_name)
        
        return chat
    
    @classmethod
    async def generate_pricing_async(
        cls,
        product: str,
        description: Optional[str] = None,
        target_market: Optional[str] = None,
        competitors: Optional[List[str]] = None,
        pricing_model: Optional[str] = None,
        constraints: Optional[List[str]] = None,
        model: Optional[str] = None
    ) -> dict:
        """
        Generate pricing structure for a product.
        
        Args:
            product: Product or service name
            description: What the product does
            target_market: Target audience
            competitors: Competitor products/prices for reference
            pricing_model: Preferred model (subscription, usage-based, etc.)
            constraints: Pricing constraints (e.g., "must have free tier")
            model: Override LLM model selection
            
        Returns:
            PricingStructure as dict
        """
        chat = cls._create_chat(model)
        
        # Build prompt
        prompt_parts = [f"Create pricing structure for: {product}"]
        
        if description:
            prompt_parts.append(f"\nProduct description: {description}")
        
        if target_market:
            prompt_parts.append(f"\nTarget market: {target_market}")
        
        if competitors:
            prompt_parts.append(f"\nCompetitor reference: {', '.join(competitors)}")
        
        if pricing_model:
            prompt_parts.append(f"\nPreferred pricing model: {pricing_model}")
        
        if constraints:
            prompt_parts.append(f"\nConstraints: {', '.join(constraints)}")
        
        prompt = "\n".join(prompt_parts)
        
        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        
        # Parse JSON from response
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
            return {
                "offer_summary": product,
                "target_segments": ["General market"],
                "pricing_model": "subscription",
                "tiers": [
                    {
                        "name": "Starter",
                        "price": "Contact for pricing",
                        "ideal_for": "Small teams",
                        "limits": ["Basic usage"],
                        "features": ["Core features"],
                        "value_prop": "Entry point"
                    }
                ],
                "monetization_risks": ["Pricing not generated - retry required"],
                "expansion_opportunities": ["TBD"],
                "recommended_entry_tier": "Starter"
            }
    
    @classmethod
    def generate_pricing(
        cls,
        product: str,
        description: Optional[str] = None,
        target_market: Optional[str] = None,
        competitors: Optional[List[str]] = None,
        pricing_model: Optional[str] = None,
        constraints: Optional[List[str]] = None,
        model: Optional[str] = None
    ) -> dict:
        """Synchronous wrapper for pricing generation."""
        return asyncio.run(cls.generate_pricing_async(
            product, description, target_market, competitors,
            pricing_model, constraints, model
        ))
    
    @classmethod
    async def price_from_strategy_async(cls, strategy: dict) -> dict:
        """
        Generate pricing from a Strategy Engine output.
        
        Args:
            strategy: Output from Strategy Engine
            
        Returns:
            PricingStructure as dict
        """
        summary = strategy.get("summary", "")
        steps = strategy.get("steps", [])
        
        product_desc = f"Strategy: {summary}\nKey elements: {'; '.join(steps[:3])}"
        
        return await cls.generate_pricing_async(
            product="Product/Service from Strategy",
            description=product_desc
        )
    
    @classmethod
    async def saas_pricing_async(
        cls,
        product: str,
        features: List[str],
        target_arr: Optional[str] = None
    ) -> dict:
        """
        Generate SaaS-specific pricing.
        
        Args:
            product: SaaS product name
            features: List of features to price
            target_arr: Target annual recurring revenue
            
        Returns:
            PricingStructure as dict
        """
        description = f"SaaS product with features: {', '.join(features)}"
        constraints = ["Must include free trial or freemium tier"]
        
        if target_arr:
            constraints.append(f"Target ARR: {target_arr}")
        
        return await cls.generate_pricing_async(
            product=product,
            description=description,
            pricing_model="subscription",
            constraints=constraints
        )
    
    @classmethod
    async def api_pricing_async(
        cls,
        api_name: str,
        use_cases: List[str],
        competitors: Optional[List[str]] = None
    ) -> dict:
        """
        Generate API-specific pricing.
        
        Args:
            api_name: API product name
            use_cases: Primary use cases
            competitors: Competitor APIs
            
        Returns:
            PricingStructure as dict
        """
        description = f"API for: {', '.join(use_cases)}"
        
        return await cls.generate_pricing_async(
            product=api_name,
            description=description,
            competitors=competitors,
            pricing_model="usage-based",
            constraints=["Must have pay-as-you-go option", "Must have volume discounts"]
        )
    
    @classmethod
    async def optimize_pricing_async(
        cls,
        current_pricing: dict,
        feedback: Optional[str] = None,
        goals: Optional[List[str]] = None
    ) -> dict:
        """
        Optimize existing pricing structure.
        
        Args:
            current_pricing: Current pricing structure
            feedback: Market/customer feedback
            goals: Optimization goals
            
        Returns:
            Optimized PricingStructure as dict
        """
        product = f"Pricing Optimization for: {current_pricing.get('offer_summary', 'Product')}"
        description = f"Current pricing:\n{json.dumps(current_pricing, indent=2)}"
        
        constraints = []
        if feedback:
            constraints.append(f"Customer feedback: {feedback}")
        if goals:
            constraints.extend(goals)
        
        return await cls.generate_pricing_async(
            product=product,
            description=description,
            constraints=constraints if constraints else None
        )
    
    @classmethod
    def get_pricing_models(cls) -> dict:
        """Get available pricing model templates."""
        return cls.PRICING_MODELS
