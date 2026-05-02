"""
Opportunity Mapper Engine

Scans situations, markets, or strategies to identify highest-leverage opportunities.
Ranks by impact, effort, and time-to-value.
"""

from emergentintegrations.llm.chat import LlmChat, UserMessage
import os
import json
import asyncio
from dotenv import load_dotenv
from typing import Optional, List
from pydantic import BaseModel

load_dotenv()


class Opportunity(BaseModel):
    """Single opportunity structure."""
    name: str
    description: str
    impact: str  # low | medium | high
    effort: str  # low | medium | high
    time_to_value: str
    dependencies: List[str]
    risks: List[str]


class OpportunityMap(BaseModel):
    """Complete opportunity mapping output."""
    context_summary: str
    opportunities: List[Opportunity]
    top_3_opportunities: List[str]
    recommended_next_move: str


class OpportunityMapperEngine:
    """Identifies and ranks highest-leverage opportunities."""
    
    MODEL_CONFIG = {
        "gpt-5.2": ("openai", "gpt-5.2"),
        "claude-sonnet-4.5": ("anthropic", "claude-sonnet-4-5-20250929"),
        "gemini-3-flash": ("gemini", "gemini-3-flash-preview")
    }
    
    # Default to Claude for opportunity mapping (strong analytical reasoning)
    DEFAULT_MODEL = "claude-sonnet-4.5"
    
    SYSTEM_PROMPT = """You are the Opportunity Mapper Engine.

Your job is to scan a situation, market, or strategy and identify the highest-leverage opportunities.

RULES:
1. Always return valid JSON only — no markdown, no explanations outside JSON.
2. Focus on leverage, speed to impact, and feasibility.
3. Rank opportunities by impact and ease.
4. No disclaimers, no model identity, no filler.
5. Be specific and actionable — vague opportunities are useless.
6. Consider both obvious and non-obvious opportunities.
7. Identify at least 5 opportunities, ranked by leverage.

OUTPUT FORMAT (JSON ONLY):
{
  "context_summary": "Short summary of the situation being analyzed.",
  "opportunities": [
    {
      "name": "Opportunity name",
      "description": "What it is and why it matters.",
      "impact": "low | medium | high",
      "effort": "low | medium | high",
      "time_to_value": "e.g. 2 weeks, 1 month, 3 months",
      "dependencies": ["Dependency 1", "Dependency 2"],
      "risks": ["Risk 1", "Risk 2"]
    }
  ],
  "top_3_opportunities": ["Name 1", "Name 2", "Name 3"],
  "recommended_next_move": "Single most important opportunity to pursue first and why."
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
            session_id=f"opportunity-mapper-{model}",
            system_message=cls.SYSTEM_PROMPT
        ).with_model(provider, model_name)
        
        return chat
    
    @classmethod
    async def map_opportunities_async(
        cls,
        situation: str,
        context: Optional[str] = None,
        constraints: Optional[List[str]] = None,
        goals: Optional[List[str]] = None,
        model: Optional[str] = None
    ) -> dict:
        """
        Map opportunities for a given situation.
        
        Args:
            situation: The situation, market, or strategy to analyze
            context: Additional context or background
            constraints: Known constraints (budget, time, resources)
            goals: Specific goals to optimize for
            model: Override model selection
            
        Returns:
            OpportunityMap as dict
        """
        chat = cls._create_chat(model)
        
        # Build prompt
        prompt_parts = [f"Analyze and map opportunities for: {situation}"]
        
        if context:
            prompt_parts.append(f"\nContext: {context}")
        
        if constraints:
            prompt_parts.append(f"\nConstraints: {', '.join(constraints)}")
        
        if goals:
            prompt_parts.append(f"\nGoals to optimize: {', '.join(goals)}")
        
        prompt = "\n".join(prompt_parts)
        
        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        
        # Parse JSON from response
        try:
            # Extract JSON if wrapped in markdown
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
            # Return structured fallback
            return {
                "context_summary": f"Opportunity analysis for: {situation}",
                "opportunities": [
                    {
                        "name": "Retry Analysis",
                        "description": "Response parsing failed - retry with clearer situation description",
                        "impact": "high",
                        "effort": "low",
                        "time_to_value": "immediate",
                        "dependencies": [],
                        "risks": ["May still fail if input is too vague"]
                    }
                ],
                "top_3_opportunities": ["Retry Analysis"],
                "recommended_next_move": "Provide a more specific situation description"
            }
    
    @classmethod
    def map_opportunities(
        cls,
        situation: str,
        context: Optional[str] = None,
        constraints: Optional[List[str]] = None,
        goals: Optional[List[str]] = None,
        model: Optional[str] = None
    ) -> dict:
        """Synchronous wrapper for opportunity mapping."""
        return asyncio.run(cls.map_opportunities_async(
            situation, context, constraints, goals, model
        ))
    
    @classmethod
    async def map_from_strategy_async(cls, strategy: dict) -> dict:
        """
        Map opportunities from a Strategy Engine output.
        
        Args:
            strategy: Output from Strategy Engine
            
        Returns:
            OpportunityMap as dict
        """
        situation = f"Strategy to expand on:\n{json.dumps(strategy, indent=2)}"
        return await cls.map_opportunities_async(
            situation=situation,
            goals=["Identify quick wins", "Find high-leverage moves", "Spot hidden opportunities"]
        )
    
    @classmethod
    async def map_from_analysis_async(cls, analysis: dict) -> dict:
        """
        Map opportunities from an Analysis Engine output.
        
        Args:
            analysis: Output from Analysis Engine (SWOT)
            
        Returns:
            OpportunityMap as dict
        """
        situation = f"SWOT Analysis to extract opportunities from:\n{json.dumps(analysis, indent=2)}"
        return await cls.map_opportunities_async(
            situation=situation,
            context="Focus on converting strengths and opportunities into actionable moves"
        )
    
    @classmethod
    async def map_market_opportunities_async(
        cls,
        market: str,
        current_position: Optional[str] = None,
        competitors: Optional[List[str]] = None,
        budget: Optional[str] = None
    ) -> dict:
        """
        Map market-specific opportunities.
        
        Args:
            market: Target market description
            current_position: Current market position
            competitors: Key competitors
            budget: Available budget/resources
            
        Returns:
            OpportunityMap as dict
        """
        situation = f"Market opportunity scan: {market}"
        
        context_parts = []
        if current_position:
            context_parts.append(f"Current position: {current_position}")
        if competitors:
            context_parts.append(f"Key competitors: {', '.join(competitors)}")
        
        context = "\n".join(context_parts) if context_parts else None
        
        constraints = []
        if budget:
            constraints.append(f"Budget: {budget}")
        
        return await cls.map_opportunities_async(
            situation=situation,
            context=context,
            constraints=constraints if constraints else None,
            goals=["Market share growth", "Revenue acceleration", "Competitive advantage"]
        )
    
    @classmethod
    async def quick_wins_async(
        cls,
        situation: str,
        timeframe: str = "30 days"
    ) -> dict:
        """
        Identify quick-win opportunities only.
        
        Args:
            situation: The situation to analyze
            timeframe: Maximum time to value
            
        Returns:
            OpportunityMap filtered to quick wins
        """
        return await cls.map_opportunities_async(
            situation=situation,
            constraints=[f"Time to value must be under {timeframe}", "Effort must be low or medium"],
            goals=["Quick wins only", "Immediate impact", "Low risk"]
        )
