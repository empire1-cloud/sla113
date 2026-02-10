"""
Engine Base Class
Provides common functionality for all AI engines.
"""

import os
import asyncio
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
from integrations.llm import ChatLLM, LLMConfig, ModelProvider


class BaseEngine(ABC):
    """
    Base class for all AI engines.
    Provides common LLM interaction methods.
    """
    
    # Default model for this engine (override in subclass)
    DEFAULT_MODEL = "gpt-4o"
    
    # Default temperature (override in subclass)
    DEFAULT_TEMPERATURE = 0.7
    
    # Maximum tokens (override in subclass)
    MAX_TOKENS = 4096
    
    @classmethod
    def _get_api_key(cls, model: str = None) -> str:
        """Get API key for the model's provider."""
        model = model or cls.DEFAULT_MODEL
        
        # Detect provider from model
        if "gpt" in model.lower() or "o1" in model.lower():
            provider = ModelProvider.OPENAI
        elif "claude" in model.lower():
            provider = ModelProvider.ANTHROPIC
        elif "gemini" in model.lower():
            provider = ModelProvider.GOOGLE
        else:
            provider = ModelProvider.OPENAI
        
        api_key = LLMConfig.get_api_key(provider)
        if not api_key:
            raise ValueError(
                f"No API key configured for {provider.value}. "
                f"Set {LLMConfig.ENV_KEYS[provider]} or EMERGENT_LLM_KEY"
            )
        return api_key
    
    @classmethod
    async def _generate(
        cls,
        prompt: str,
        model: str = None,
        system_prompt: str = None,
        temperature: float = None,
        max_tokens: int = None,
        **kwargs
    ) -> str:
        """
        Generate text using the LLM.
        
        Args:
            prompt: User prompt
            model: Model name (default: cls.DEFAULT_MODEL)
            system_prompt: System prompt
            temperature: Sampling temperature
            max_tokens: Max tokens
            
        Returns:
            Generated text
        """
        model = model or cls.DEFAULT_MODEL
        temperature = temperature if temperature is not None else cls.DEFAULT_TEMPERATURE
        max_tokens = max_tokens or cls.MAX_TOKENS
        
        api_key = cls._get_api_key(model)
        
        messages = [{"role": "user", "content": prompt}]
        
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
    
    @classmethod
    def _generate_sync(cls, prompt: str, **kwargs) -> str:
        """Synchronous wrapper for _generate."""
        return asyncio.run(cls._generate(prompt, **kwargs))
    
    @classmethod
    async def _chat(
        cls,
        messages: List[Dict[str, str]],
        model: str = None,
        system_prompt: str = None,
        temperature: float = None,
        max_tokens: int = None,
        **kwargs
    ) -> str:
        """
        Multi-turn chat using the LLM.
        
        Args:
            messages: List of message dicts with "role" and "content"
            model: Model name
            system_prompt: System prompt
            temperature: Sampling temperature
            max_tokens: Max tokens
            
        Returns:
            Assistant's response text
        """
        model = model or cls.DEFAULT_MODEL
        temperature = temperature if temperature is not None else cls.DEFAULT_TEMPERATURE
        max_tokens = max_tokens or cls.MAX_TOKENS
        
        api_key = cls._get_api_key(model)
        
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
    
    @classmethod
    def _chat_sync(cls, messages: List[Dict[str, str]], **kwargs) -> str:
        """Synchronous wrapper for _chat."""
        return asyncio.run(cls._chat(messages, **kwargs))


# Convenience functions that match emergentintegrations patterns
async def llm_generate(
    model: str,
    prompt: str,
    system_prompt: str = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    **kwargs
) -> str:
    """
    Generate text using the specified model.
    Drop-in replacement for emergentintegrations calls.
    """
    # Get appropriate API key
    if "gpt" in model.lower() or "o1" in model.lower():
        provider = ModelProvider.OPENAI
    elif "claude" in model.lower():
        provider = ModelProvider.ANTHROPIC
    elif "gemini" in model.lower():
        provider = ModelProvider.GOOGLE
    else:
        provider = ModelProvider.OPENAI
    
    api_key = LLMConfig.get_api_key(provider)
    if not api_key:
        raise ValueError(f"No API key for {provider.value}")
    
    messages = [{"role": "user", "content": prompt}]
    
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


def llm_generate_sync(model: str, prompt: str, **kwargs) -> str:
    """Synchronous wrapper for llm_generate."""
    return asyncio.run(llm_generate(model, prompt, **kwargs))
