"""
Evaluator Engine

Scores and evaluates ideas, strategies, offers, or plans against clear criteria.
Provides weighted scoring with go/no-go recommendations.
"""

from emergentintegrations.llm.chat import LlmChat, UserMessage
import os
import json
import asyncio
from dotenv import load_dotenv
from typing import Optional, List
from pydantic import BaseModel

load_dotenv()


class Criterion(BaseModel):
    """Single evaluation criterion."""
    name: str
    score: int  # 1-10
    weight: float  # 0.0-1.0
    rationale: str


class EvaluationResult(BaseModel):
    """Complete evaluation output."""
    subject: str
    criteria: List[Criterion]
    weighted_score: float
    strengths: List[str]
    weaknesses: List[str]
    improvement_suggestions: List[str]
    go_no_go: str  # go | no_go | revise


class EvaluatorEngine:
    """Scores and evaluates ideas, strategies, or plans."""
    
    MODEL_CONFIG = {
        "gpt-5.2": ("openai", "gpt-5.2"),
        "claude-sonnet-4.5": ("anthropic", "claude-sonnet-4-5-20250929"),
        "gemini-3-flash": ("gemini", "gemini-3-flash-preview")
    }
    
    # Default to Claude for evaluation (strong analytical reasoning)
    DEFAULT_MODEL = "claude-sonnet-4.5"
    
    # Standard evaluation criteria sets
    CRITERIA_PRESETS = {
        "strategy": [
            {"name": "Clarity", "weight": 0.15, "description": "How clear and understandable is the strategy?"},
            {"name": "Feasibility", "weight": 0.20, "description": "How realistic is execution?"},
            {"name": "Impact Potential", "weight": 0.20, "description": "What's the potential upside?"},
            {"name": "Risk Level", "weight": 0.15, "description": "How manageable are the risks?"},
            {"name": "Resource Efficiency", "weight": 0.15, "description": "How well does it use available resources?"},
            {"name": "Differentiation", "weight": 0.15, "description": "How unique is the approach?"}
        ],
        "idea": [
            {"name": "Originality", "weight": 0.20, "description": "How novel is the idea?"},
            {"name": "Market Fit", "weight": 0.25, "description": "Does it solve a real problem?"},
            {"name": "Scalability", "weight": 0.20, "description": "Can it grow?"},
            {"name": "Execution Complexity", "weight": 0.15, "description": "How hard to build?"},
            {"name": "Competitive Advantage", "weight": 0.20, "description": "What's the moat?"}
        ],
        "plan": [
            {"name": "Completeness", "weight": 0.20, "description": "Are all steps covered?"},
            {"name": "Timeline Realism", "weight": 0.20, "description": "Are timelines achievable?"},
            {"name": "Resource Allocation", "weight": 0.15, "description": "Are resources properly assigned?"},
            {"name": "Risk Mitigation", "weight": 0.15, "description": "Are risks addressed?"},
            {"name": "Dependency Management", "weight": 0.15, "description": "Are dependencies clear?"},
            {"name": "Success Metrics", "weight": 0.15, "description": "Are outcomes measurable?"}
        ],
        "offer": [
            {"name": "Value Proposition", "weight": 0.25, "description": "Is the value clear?"},
            {"name": "Price-Value Alignment", "weight": 0.20, "description": "Is pricing fair?"},
            {"name": "Target Fit", "weight": 0.20, "description": "Right audience?"},
            {"name": "Urgency/Scarcity", "weight": 0.15, "description": "Compelling to act now?"},
            {"name": "Trust Signals", "weight": 0.20, "description": "Credibility established?"}
        ]
    }
    
    SYSTEM_PROMPT = """You are the Evaluator Engine.

Your job is to score and evaluate ideas, strategies, offers, or plans against clear criteria.

RULES:
1. Always return valid JSON only — no markdown, no explanations outside JSON.
2. Be explicit and consistent in scoring (1-10 scale).
3. Justify scores briefly but concretely — no vague reasoning.
4. No disclaimers, no model identity, no filler.
5. Calculate weighted_score correctly: sum of (score × weight) for all criteria.
6. Be honest — don't inflate scores. A 7 is good, 8+ is excellent.
7. go_no_go decision: go (7.0+), revise (5.0-6.9), no_go (<5.0).

OUTPUT FORMAT (JSON ONLY):
{
  "subject": "What is being evaluated.",
  "criteria": [
    {
      "name": "Criterion name",
      "score": 1-10,
      "weight": 0.0-1.0,
      "rationale": "Short explanation for the score."
    }
  ],
  "weighted_score": 0.0,
  "strengths": ["Strength 1", "Strength 2"],
  "weaknesses": ["Weakness 1", "Weakness 2"],
  "improvement_suggestions": ["Suggestion 1", "Suggestion 2"],
  "go_no_go": "go | no_go | revise"
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
            session_id=f"evaluator-{model}",
            system_message=cls.SYSTEM_PROMPT
        ).with_model(provider, model_name)
        
        return chat
    
    @classmethod
    async def evaluate_async(
        cls,
        subject: str,
        content: str,
        criteria: Optional[List[dict]] = None,
        criteria_preset: Optional[str] = None,
        context: Optional[str] = None,
        model: Optional[str] = None
    ) -> dict:
        """
        Evaluate a subject against criteria.
        
        Args:
            subject: What is being evaluated (name/title)
            content: The actual content to evaluate
            criteria: Custom criteria list
            criteria_preset: Use preset criteria (strategy, idea, plan, offer)
            context: Additional context
            model: Override model selection
            
        Returns:
            EvaluationResult as dict
        """
        chat = cls._create_chat(model)
        
        # Determine criteria to use
        if criteria:
            criteria_text = json.dumps(criteria, indent=2)
        elif criteria_preset and criteria_preset in cls.CRITERIA_PRESETS:
            criteria_text = json.dumps(cls.CRITERIA_PRESETS[criteria_preset], indent=2)
        else:
            criteria_text = "Use appropriate criteria for the subject type."
        
        # Build prompt
        prompt_parts = [
            f"Evaluate the following:",
            f"Subject: {subject}",
            f"Content: {content}",
            f"\nEvaluation Criteria:\n{criteria_text}"
        ]
        
        if context:
            prompt_parts.append(f"\nAdditional Context: {context}")
        
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
            
            result = json.loads(response)
            
            # Validate and recalculate weighted score
            if "criteria" in result:
                weighted_sum = sum(
                    c.get("score", 0) * c.get("weight", 0) 
                    for c in result["criteria"]
                )
                result["weighted_score"] = round(weighted_sum, 2)
                
                # Determine go/no_go based on score
                if result["weighted_score"] >= 7.0:
                    result["go_no_go"] = "go"
                elif result["weighted_score"] >= 5.0:
                    result["go_no_go"] = "revise"
                else:
                    result["go_no_go"] = "no_go"
            
            return result
        except json.JSONDecodeError:
            return {
                "subject": subject,
                "criteria": [],
                "weighted_score": 0.0,
                "strengths": ["Unable to parse evaluation"],
                "weaknesses": ["Response format error"],
                "improvement_suggestions": ["Retry with clearer content"],
                "go_no_go": "revise"
            }
    
    @classmethod
    def evaluate(
        cls,
        subject: str,
        content: str,
        criteria: Optional[List[dict]] = None,
        criteria_preset: Optional[str] = None,
        context: Optional[str] = None,
        model: Optional[str] = None
    ) -> dict:
        """Synchronous wrapper for evaluation."""
        return asyncio.run(cls.evaluate_async(
            subject, content, criteria, criteria_preset, context, model
        ))
    
    @classmethod
    async def evaluate_strategy_async(cls, strategy: dict) -> dict:
        """Evaluate a strategy from Strategy Engine."""
        subject = "Strategy Evaluation"
        content = json.dumps(strategy, indent=2)
        return await cls.evaluate_async(
            subject=subject,
            content=content,
            criteria_preset="strategy"
        )
    
    @classmethod
    async def evaluate_plan_async(cls, plan: dict) -> dict:
        """Evaluate a plan from Plan Builder Engine."""
        subject = "Execution Plan Evaluation"
        content = json.dumps(plan, indent=2)
        return await cls.evaluate_async(
            subject=subject,
            content=content,
            criteria_preset="plan"
        )
    
    @classmethod
    async def evaluate_idea_async(cls, idea: str, context: Optional[str] = None) -> dict:
        """Evaluate a business/product idea."""
        return await cls.evaluate_async(
            subject="Idea Evaluation",
            content=idea,
            criteria_preset="idea",
            context=context
        )
    
    @classmethod
    async def evaluate_offer_async(cls, offer: str, target_audience: Optional[str] = None) -> dict:
        """Evaluate a business offer/proposal."""
        context = f"Target audience: {target_audience}" if target_audience else None
        return await cls.evaluate_async(
            subject="Offer Evaluation",
            content=offer,
            criteria_preset="offer",
            context=context
        )
    
    @classmethod
    async def compare_async(
        cls,
        options: List[dict],
        criteria: Optional[List[dict]] = None,
        criteria_preset: Optional[str] = None
    ) -> dict:
        """
        Compare multiple options and rank them.
        
        Args:
            options: List of {"name": "...", "content": "..."} dicts
            criteria: Custom criteria
            criteria_preset: Preset criteria type
            
        Returns:
            Comparison result with rankings
        """
        evaluations = []
        
        for option in options:
            eval_result = await cls.evaluate_async(
                subject=option.get("name", "Option"),
                content=option.get("content", ""),
                criteria=criteria,
                criteria_preset=criteria_preset
            )
            evaluations.append({
                "name": option.get("name"),
                "weighted_score": eval_result.get("weighted_score", 0),
                "go_no_go": eval_result.get("go_no_go", "revise"),
                "evaluation": eval_result
            })
        
        # Sort by score
        evaluations.sort(key=lambda x: x["weighted_score"], reverse=True)
        
        return {
            "comparison_type": criteria_preset or "custom",
            "rankings": [
                {"rank": i+1, "name": e["name"], "score": e["weighted_score"], "decision": e["go_no_go"]}
                for i, e in enumerate(evaluations)
            ],
            "winner": evaluations[0]["name"] if evaluations else None,
            "detailed_evaluations": evaluations
        }
    
    @classmethod
    def get_available_presets(cls) -> dict:
        """Get available criteria presets."""
        return {
            preset: [c["name"] for c in criteria]
            for preset, criteria in cls.CRITERIA_PRESETS.items()
        }
