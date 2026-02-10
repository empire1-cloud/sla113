"""
LLM Integrations Package
Self-contained LLM chat functionality for OpenAI, Anthropic, and Google.
Replaces emergentintegrations for standalone deployment.
"""

from .chat import ChatLLM, ChatResponse, generate, generate_sync
from .config import LLMConfig, ModelConfig, ModelProvider, MODEL_REGISTRY
from .compat import chat, generate_completion

__all__ = [
    "ChatLLM",
    "ChatResponse",
    "generate",
    "generate_sync",
    "LLMConfig",
    "ModelConfig", 
    "ModelProvider",
    "MODEL_REGISTRY",
    "chat",
    "generate_completion",
]
