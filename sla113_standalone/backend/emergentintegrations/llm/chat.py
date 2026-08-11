"""HYBRID_AI drop-in replacement for emergentintegrations.llm.chat.

Usage (unchanged):
    from emergentintegrations.llm.chat import LlmChat, UserMessage

    chat = LlmChat(system_message="You are helpful.")
    response = await chat.send_message(UserMessage(text="Hello"))
"""

from HYBRID_AI.orchestrator import LlmChat, ChatLLM, ChatResponse
from HYBRID_AI.orchestrator import UserMessage, SystemMessage, AssistantMessage

__all__ = [
    "LlmChat",
    "ChatLLM",
    "ChatResponse",
    "UserMessage",
    "SystemMessage",
    "AssistantMessage",
]
