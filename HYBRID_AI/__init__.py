"""HYBRID_AI — Local Gemma 4 Inference Engine

Replaces external emergentintegrations dependency with self-hosted
Gemma 4 26B A4B MoE inference. No external API keys required.

Drop-in replacement for:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
"""

from .orchestrator import LlmChat, ChatLLM, UserMessage, SystemMessage, AssistantMessage

from .models import (
    ChatRequest,
    ChatResponse,
    EngineTask,
    GenerationConfig,
)

__version__ = "1.0.0"
__all__ = [
    "LlmChat",
    "ChatLLM",
    "UserMessage",
    "SystemMessage",
    "AssistantMessage",
    "GemmaInference",
    "ChatRequest",
    "ChatResponse",
    "EngineTask",
    "GenerationConfig",
]
