"""
Persona Engine

Converts target audiences, user segments, or customer types into
clear, actionable personas for strategy, marketing, product, or sales.
"""

from emergentintegrations.llm.chat import LlmChat, UserMessage
import os
import json
import asyncio
from dotenv import load_dotenv
from typing import Optional, List
from pydantic import BaseModel

load_dotenv()


class Persona(BaseModel):
    """Complete persona definition."""
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


class PersonaEngine:
    """Generates actionable user personas."""
    
    MODEL_CONFIG = {
        "gpt-5.2": ("openai", "gpt-5.2"),
        "claude-sonnet-4.5": ("anthropic", "claude-sonnet-4-5-20250929"),
        "gemini-3-flash": ("gemini", "gemini-3-flash-preview")
    }
    
    # Default to Claude for personas (strong at human behavior understanding)
    DEFAULT_MODEL = "claude-sonnet-4.5"
    
    # Persona templates by category
    PERSONA_TEMPLATES = {
        "b2b_buyer": {
            "typical_roles": ["Decision maker", "Budget holder", "End user", "Technical evaluator"],
            "key_attributes": ["Company size", "Industry", "Budget authority", "Tech stack"]
        },
        "consumer": {
            "typical_roles": ["Early adopter", "Mainstream user", "Price-sensitive", "Premium buyer"],
            "key_attributes": ["Demographics", "Lifestyle", "Values", "Media consumption"]
        },
        "developer": {
            "typical_roles": ["Solo developer", "Team lead", "Architect", "DevOps engineer"],
            "key_attributes": ["Tech stack", "Experience level", "Company type", "Learning style"]
        },
        "founder": {
            "typical_roles": ["First-time founder", "Serial entrepreneur", "Technical founder", "Non-technical founder"],
            "key_attributes": ["Stage", "Funding status", "Team size", "Industry focus"]
        }
    }
    
    SYSTEM_PROMPT = """You are the Persona Engine.

Your job is to convert a target audience, user segment, or customer type into a clear, actionable persona that can be used for strategy, marketing, product, or sales.

RULES:
1. Always return valid JSON only — no markdown, no commentary.
2. Focus on behavior, motivations, and decision drivers.
3. Make the persona specific, realistic, and operational.
4. No disclaimers, no model identity, no filler.
5. Ensure all attributes are concrete and usable.
6. Give the persona a realistic name that reflects their segment.
7. Include at least 3-4 items for each list attribute.

OUTPUT FORMAT (JSON ONLY):
{
  "name": "Persona name (realistic first name + role descriptor)",
  "role": "Job/identity in their world",
  "background": "Short description of who they are (2-3 sentences).",
  "goals": ["Goal 1", "Goal 2", "Goal 3"],
  "pains": ["Pain 1", "Pain 2", "Pain 3"],
  "triggers": ["Event or situation that makes them act"],
  "buying_criteria": ["What they care about when choosing a solution"],
  "objections": ["Common reasons they say no"],
  "preferred_channels": ["Channel 1", "Channel 2"],
  "preferred_messaging": ["Messaging angle 1", "Messaging angle 2"]
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
            session_id=f"persona-{model}",
            system_message=cls.SYSTEM_PROMPT
        ).with_model(provider, model_name)
        
        return chat
    
    @classmethod
    async def generate_persona_async(
        cls,
        audience: str,
        context: Optional[str] = None,
        product: Optional[str] = None,
        industry: Optional[str] = None,
        model: Optional[str] = None
    ) -> dict:
        """
        Generate a persona from an audience description.
        
        Args:
            audience: Target audience description
            context: Additional context about the business
            product: Product/service being sold
            industry: Target industry
            model: Override LLM model selection
            
        Returns:
            Persona as dict
        """
        chat = cls._create_chat(model)
        
        # Build prompt
        prompt_parts = [f"Create a detailed persona for: {audience}"]
        
        if context:
            prompt_parts.append(f"\nBusiness context: {context}")
        
        if product:
            prompt_parts.append(f"\nProduct/service: {product}")
        
        if industry:
            prompt_parts.append(f"\nTarget industry: {industry}")
        
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
                "name": "Unnamed Persona",
                "role": audience,
                "background": "Persona generation failed - retry required",
                "goals": ["TBD"],
                "pains": ["TBD"],
                "triggers": ["TBD"],
                "buying_criteria": ["TBD"],
                "objections": ["TBD"],
                "preferred_channels": ["TBD"],
                "preferred_messaging": ["TBD"]
            }
    
    @classmethod
    def generate_persona(
        cls,
        audience: str,
        context: Optional[str] = None,
        product: Optional[str] = None,
        industry: Optional[str] = None,
        model: Optional[str] = None
    ) -> dict:
        """Synchronous wrapper for persona generation."""
        return asyncio.run(cls.generate_persona_async(
            audience, context, product, industry, model
        ))
    
    @classmethod
    async def generate_multiple_personas_async(
        cls,
        audiences: List[str],
        context: Optional[str] = None,
        product: Optional[str] = None
    ) -> List[dict]:
        """
        Generate multiple personas.
        
        Args:
            audiences: List of audience descriptions
            context: Shared business context
            product: Product/service being sold
            
        Returns:
            List of Persona dicts
        """
        personas = []
        for audience in audiences:
            persona = await cls.generate_persona_async(
                audience=audience,
                context=context,
                product=product
            )
            personas.append(persona)
        return personas
    
    @classmethod
    async def buyer_persona_async(
        cls,
        role: str,
        company_size: Optional[str] = None,
        industry: Optional[str] = None,
        budget_range: Optional[str] = None
    ) -> dict:
        """
        Generate B2B buyer persona.
        
        Args:
            role: Buyer's role/title
            company_size: Company size segment
            industry: Target industry
            budget_range: Expected budget
            
        Returns:
            Persona as dict
        """
        audience = f"B2B buyer: {role}"
        context_parts = []
        
        if company_size:
            context_parts.append(f"Company size: {company_size}")
        if budget_range:
            context_parts.append(f"Budget range: {budget_range}")
        
        context = "; ".join(context_parts) if context_parts else None
        
        return await cls.generate_persona_async(
            audience=audience,
            context=context,
            industry=industry
        )
    
    @classmethod
    async def user_persona_async(
        cls,
        user_type: str,
        use_case: Optional[str] = None,
        experience_level: Optional[str] = None
    ) -> dict:
        """
        Generate end-user persona.
        
        Args:
            user_type: Type of user
            use_case: Primary use case
            experience_level: Technical experience
            
        Returns:
            Persona as dict
        """
        audience = f"End user: {user_type}"
        context_parts = []
        
        if use_case:
            context_parts.append(f"Primary use case: {use_case}")
        if experience_level:
            context_parts.append(f"Experience level: {experience_level}")
        
        context = "; ".join(context_parts) if context_parts else None
        
        return await cls.generate_persona_async(
            audience=audience,
            context=context
        )
    
    @classmethod
    async def icp_persona_async(
        cls,
        product: str,
        ideal_customer: str,
        market: Optional[str] = None
    ) -> dict:
        """
        Generate Ideal Customer Profile (ICP) persona.
        
        Args:
            product: Product being sold
            ideal_customer: Description of ideal customer
            market: Target market
            
        Returns:
            Persona as dict
        """
        audience = f"Ideal Customer Profile: {ideal_customer}"
        
        return await cls.generate_persona_async(
            audience=audience,
            product=product,
            industry=market
        )
    
    @classmethod
    async def anti_persona_async(cls, product: str, bad_fit: str) -> dict:
        """
        Generate anti-persona (who NOT to target).
        
        Args:
            product: Product being sold
            bad_fit: Description of bad-fit customer
            
        Returns:
            Persona as dict (representing who to avoid)
        """
        audience = f"Anti-persona (bad fit customer): {bad_fit}"
        context = "This persona represents who we should NOT target. Focus on why they are a poor fit."
        
        return await cls.generate_persona_async(
            audience=audience,
            context=context,
            product=product
        )
    
    @classmethod
    def get_persona_templates(cls) -> dict:
        """Get available persona templates."""
        return cls.PERSONA_TEMPLATES
