"""
Emergent Integrations - Self-Contained LLM Package
Drop-in replacement for the emergentintegrations package.

This module provides a unified interface for:
- OpenAI (GPT-4o, GPT-4-turbo, etc.)
- Anthropic (Claude Sonnet, Opus, Haiku)
- Google (Gemini 2.0, 1.5)

Usage:
    from emergentintegrations.llm.chat import LlmChat, UserMessage, SystemMessage
    
    chat = LlmChat(api_key="...", system_message="You are helpful.")
    chat = chat.with_model("openai", "gpt-4o")
    response = await chat.send_message(UserMessage(text="Hello"))
"""

from .llm import LlmChat, UserMessage, SystemMessage, AssistantMessage
from .llm.chat import ChatLLM
from .llm.config import LLMConfig, ModelProvider

__version__ = "1.0.0"
__all__ = [
    "LlmChat",
    "UserMessage", 
    "SystemMessage",
    "AssistantMessage",
    "ChatLLM",
    "LLMConfig",
    "ModelProvider",
]
