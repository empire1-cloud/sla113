"""
Strategy Engine
Generates actionable strategies using the hybrid AI stack.

Supports: OpenAI, Anthropic, Google models
"""

import os
import json
import asyncio
from typing import Optional, Dict, Any

# Use local integrations (replaces emergentintegrations)
from integrations.llm import ChatLLM, LLMConfig, ModelProvider


class StrategyEngine:
    """Generates actionable strategies using the hybrid AI stack."""
    
    MODEL_CONFIG = {
        "gpt-5.2": ("openai", "gpt-4o"),
        "gpt-4o": ("openai", "gpt-4o"),
        "claude-sonnet-4.5": ("anthropic", "claude-sonnet-4-5-20250929"),
        "claude-3-5-sonnet": ("anthropic", "claude-3-5-sonnet-20241022"),
        "gemini-3-flash": ("google", "gemini-2.0-flash"),
        "gemini-2.0-flash": ("google", "gemini-2.0-flash"),
    }
    
    SYSTEM_PROMPT = """You are the Strategy Engine.

Your job is to take any goal the user gives you and return a clear, structured, actionable strategy that creates momentum, removes confusion, and breaks the goal into steps anyone can follow.

RULES:
1. Always return valid JSON only — no markdown, no explanations outside JSON.
2. Never ramble, never fluff, never repeat the user's words back to them.
3. Keep the tone direct, practical, and operator-minded.
4. Break everything into steps that can be executed immediately.
5. If the user's goal is vague, infer the most useful interpretation and proceed.
6. Never ask questions.
7. Always include risks, blind spots, and next actions.
8. Always assume the user wants clarity, speed, and momentum.

OUTPUT FORMAT (JSON ONLY):
{
  "summary": "One paragraph explaining the strategy at a high level.",
  "steps": ["Step 1...", "Step 2...", "Step 3..."],
  "risks": ["Risk 1...", "Risk 2..."],
  "resources": ["Resource 1...", "Resource 2..."],
  "next_action": "The single most important thing the user should do immediately."
}

Return ONLY the JSON object. No other text."""
    
    @classmethod
    def _get_api_key(cls, provider: str) -> str:
        """Get API key for provider from environment."""
        provider_map = {
            "openai": ModelProvider.OPENAI,
            "anthropic": ModelProvider.ANTHROPIC,
            "google": ModelProvider.GOOGLE,
        }
        return LLMConfig.get_api_key(provider_map.get(provider, ModelProvider.OPENAI))
    
    @classmethod
    async def _generate_async(
        cls, 
        model: str, 
        goal: str, 
        context: str = None, 
        tone: str = "direct"
    ) -> Dict[str, Any]:
        """Generate strategy asynchronously."""
        
        # Get provider and model ID
        provider, model_id = cls.MODEL_CONFIG.get(model, ("openai", "gpt-4o"))
        
        # Get API key
        api_key = cls._get_api_key(provider)
        if not api_key:
            raise ValueError(f"No API key configured for {provider}")
        
        # Build prompt
        prompt = f"Goal: {goal}"
        if context:
            prompt += f"\nContext: {context}"
        if tone:
            prompt += f"\nTone: {tone}"
        
        # Call LLM
        messages = [{"role": "user", "content": prompt}]
        
        response = await ChatLLM.chat(
            api_key=api_key,
            model=model_id,
            provider=provider,
            messages=messages,
            system_prompt=cls.SYSTEM_PROMPT,
            temperature=0.7,
            max_tokens=4096,
        )
        
        response_text = response.content
        
        # Parse JSON from response
        try:
            # Try to extract JSON if wrapped in markdown
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Return structured error if JSON parsing fails
            return {
                "summary": response_text[:500],
                "steps": ["Review the generated content and extract actionable steps"],
                "risks": ["Response was not in expected JSON format"],
                "resources": [],
                "next_action": "Retry with a more specific goal"
            }
    
    @classmethod
    def generate(
        cls, 
        model: str, 
        goal: str, 
        context: str = None, 
        tone: str = "direct"
    ) -> Dict[str, Any]:
        """Synchronous wrapper for async generation."""
        return asyncio.run(cls._generate_async(model, goal, context, tone))
    
    @classmethod
    async def generate_async(
        cls, 
        model: str, 
        goal: str, 
        context: str = None, 
        tone: str = "direct"
    ) -> Dict[str, Any]:
        """Async generation method."""
        return await cls._generate_async(model, goal, context, tone)
