"""
Compatibility Layer for emergentintegrations
This module provides backward compatibility with the emergentintegrations package.
Import from here instead of emergentintegrations.llm.chat
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from .chat import ChatLLM, ChatResponse
from .config import LLMConfig, ModelProvider, MODEL_REGISTRY


class chat:
    """
    Compatibility class matching emergentintegrations.llm.chat interface.
    
    Original usage:
        from emergentintegrations.llm.chat import chat
        response = await chat(
            api_key="...",
            base_url="...",
            model="gpt-4o",
            messages=[...]
        )
    
    New usage (same interface):
        from integrations.llm.compat import chat
        response = await chat(
            api_key="...",  # Optional if env var set
            model="gpt-4o",
            messages=[...]
        )
    """
    
    @staticmethod
    async def completions(
        model: str,
        messages: List[Dict[str, str]],
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,  # Ignored, kept for compatibility
        temperature: float = 0.7,
        max_tokens: int = 4096,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate a chat completion.
        
        Args:
            model: Model name (e.g., "gpt-4o", "claude-sonnet-4.5")
            messages: List of message dicts
            api_key: API key (optional if env var set)
            base_url: Ignored (kept for compatibility)
            temperature: Sampling temperature
            max_tokens: Max tokens in response
            system_prompt: Optional system prompt
            
        Returns:
            Generated text content
        """
        # Get API key from environment if not provided
        if not api_key:
            config = MODEL_REGISTRY.get(model)
            if config:
                api_key = LLMConfig.get_api_key(config.provider)
            else:
                # Try to detect provider from model name
                if "gpt" in model.lower() or "o1" in model.lower():
                    api_key = LLMConfig.get_api_key(ModelProvider.OPENAI)
                elif "claude" in model.lower():
                    api_key = LLMConfig.get_api_key(ModelProvider.ANTHROPIC)
                elif "gemini" in model.lower():
                    api_key = LLMConfig.get_api_key(ModelProvider.GOOGLE)
        
        if not api_key:
            raise ValueError(
                f"No API key found for model {model}. "
                "Set OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY, or EMERGENT_LLM_KEY"
            )
        
        response = await ChatLLM.chat(
            api_key=api_key,
            model=model,
            messages=messages,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        return response.content
    
    @staticmethod
    def completions_sync(
        model: str,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """Synchronous wrapper for completions."""
        return asyncio.run(chat.completions(model, messages, **kwargs))


# Also export as function for direct use
async def generate_completion(
    model: str,
    prompt: str,
    api_key: Optional[str] = None,
    system_prompt: Optional[str] = None,
    **kwargs
) -> str:
    """
    Convenience function for single-prompt generation.
    
    Args:
        model: Model name
        prompt: User prompt
        api_key: Optional API key
        system_prompt: Optional system prompt
        
    Returns:
        Generated text
    """
    messages = [{"role": "user", "content": prompt}]
    return await chat.completions(
        model=model,
        messages=messages,
        api_key=api_key,
        system_prompt=system_prompt,
        **kwargs
    )


# Export for backward compatibility
__all__ = ["chat", "generate_completion", "ChatLLM", "ChatResponse", "LLMConfig"]
