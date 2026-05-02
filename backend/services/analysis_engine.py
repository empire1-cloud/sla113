"""
Analysis Engine

Performs deep, structured analysis on any topic or artifact.
Returns SWOT-style analysis with key insights and focus recommendations.
"""

from emergentintegrations.llm.chat import LlmChat, UserMessage
import os
import json
import asyncio
from dotenv import load_dotenv
from typing import Optional, List
from pydantic import BaseModel

load_dotenv()


class AnalysisResult(BaseModel):
    """Structured analysis output."""
    overview: str
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threats: List[str]
    key_insights: List[str]
    recommended_focus: str


class AnalysisEngine:
    """Performs deep, structured analysis on any topic or artifact."""
    
    MODEL_CONFIG = {
        "gpt-5.2": ("openai", "gpt-5.2"),
        "claude-sonnet-4.5": ("anthropic", "claude-sonnet-4-5-20250929"),
        "gemini-3-flash": ("gemini", "gemini-3-flash-preview")
    }
    
    # Default to Claude for analysis (superior at structured thinking)
    DEFAULT_MODEL = "claude-sonnet-4.5"
    
    SYSTEM_PROMPT = """You are the Analysis Engine.

Your job is to perform deep, structured analysis on any topic or artifact provided.

RULES:
1. Always return valid JSON only — no markdown, no explanations outside JSON.
2. Focus on clarity, depth, and diagnostic insight.
3. Do not propose strategies or plans — only analyze.
4. No disclaimers, no model identity, no filler.
5. Be specific and actionable in your insights.
6. Identify non-obvious patterns and blind spots.

OUTPUT FORMAT (JSON ONLY):
{
  "overview": "High-level explanation of what you're analyzing and its current state.",
  "strengths": ["Strength 1", "Strength 2", "Strength 3"],
  "weaknesses": ["Weakness 1", "Weakness 2", "Weakness 3"],
  "opportunities": ["Opportunity 1", "Opportunity 2", "Opportunity 3"],
  "threats": ["Threat 1", "Threat 2", "Threat 3"],
  "key_insights": ["Non-obvious insight 1", "Non-obvious insight 2", "Non-obvious insight 3"],
  "recommended_focus": "The single most important area to focus on based on this analysis."
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
            session_id=f"analysis-{model}",
            system_message=cls.SYSTEM_PROMPT
        ).with_model(provider, model_name)
        
        return chat
    
    @classmethod
    async def analyze_async(
        cls,
        subject: str,
        context: Optional[str] = None,
        focus_area: Optional[str] = None,
        model: Optional[str] = None
    ) -> dict:
        """
        Perform structured analysis on a subject.
        
        Args:
            subject: The topic, artifact, or situation to analyze
            context: Additional context or background
            focus_area: Specific aspect to focus on
            model: Override model selection
            
        Returns:
            AnalysisResult as dict
        """
        chat = cls._create_chat(model)
        
        # Build prompt
        prompt_parts = [f"Analyze the following: {subject}"]
        
        if context:
            prompt_parts.append(f"\nContext: {context}")
        
        if focus_area:
            prompt_parts.append(f"\nFocus particularly on: {focus_area}")
        
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
                "overview": f"Analysis of: {subject}",
                "strengths": ["Unable to parse structured analysis"],
                "weaknesses": ["Response format error"],
                "opportunities": ["Retry with more specific subject"],
                "threats": ["Incomplete analysis"],
                "key_insights": [response[:500] if response else "No response received"],
                "recommended_focus": "Retry the analysis with clearer parameters"
            }
    
    @classmethod
    def analyze(
        cls,
        subject: str,
        context: Optional[str] = None,
        focus_area: Optional[str] = None,
        model: Optional[str] = None
    ) -> dict:
        """Synchronous wrapper for analysis."""
        return asyncio.run(cls.analyze_async(subject, context, focus_area, model))
    
    @classmethod
    async def analyze_strategy_async(cls, strategy: dict) -> dict:
        """
        Analyze a strategy output from the Strategy Engine.
        
        Args:
            strategy: Output from Strategy Engine
            
        Returns:
            AnalysisResult as dict
        """
        subject = f"Strategy Analysis:\n{json.dumps(strategy, indent=2)}"
        return await cls.analyze_async(
            subject=subject,
            focus_area="Evaluate feasibility, risks, and potential blind spots"
        )
    
    @classmethod
    async def analyze_plan_async(cls, plan: dict) -> dict:
        """
        Analyze an execution plan from the Plan Builder Engine.
        
        Args:
            plan: Output from Plan Builder Engine
            
        Returns:
            AnalysisResult as dict
        """
        subject = f"Execution Plan Analysis:\n{json.dumps(plan, indent=2)}"
        return await cls.analyze_async(
            subject=subject,
            focus_area="Evaluate timeline feasibility, resource requirements, and critical path risks"
        )
    
    @classmethod
    async def competitive_analysis_async(
        cls,
        product: str,
        competitors: List[str],
        market: Optional[str] = None
    ) -> dict:
        """
        Perform competitive analysis.
        
        Args:
            product: Your product/service
            competitors: List of competitors
            market: Target market
            
        Returns:
            AnalysisResult as dict
        """
        subject = f"Competitive Analysis for: {product}"
        context = f"Competitors: {', '.join(competitors)}"
        if market:
            context += f"\nTarget Market: {market}"
        
        return await cls.analyze_async(
            subject=subject,
            context=context,
            focus_area="Competitive positioning, differentiation opportunities, and market threats"
        )
    
    @classmethod
    async def risk_analysis_async(
        cls,
        situation: str,
        stakeholders: Optional[List[str]] = None
    ) -> dict:
        """
        Perform risk-focused analysis.
        
        Args:
            situation: The situation to analyze for risks
            stakeholders: Key stakeholders affected
            
        Returns:
            AnalysisResult as dict
        """
        context = None
        if stakeholders:
            context = f"Key stakeholders: {', '.join(stakeholders)}"
        
        return await cls.analyze_async(
            subject=situation,
            context=context,
            focus_area="Risk identification, probability assessment, and mitigation priorities"
        )
