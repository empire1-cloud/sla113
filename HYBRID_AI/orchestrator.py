"""Hybrid Orchestrator — Drop-in Replacement for emergentintegrations.llm.chat

Provides the same LlmChat + UserMessage API surface that SLA113 engines
expect, but backed by local Gemma 4 inference instead of external APIs.

Usage (matching existing engine code):
    from HYBRID_AI.orchestrator import LlmChat, UserMessage

    chat = LlmChat(
        api_key=None,  # not needed — local inference
        session_id="vision-engine",
        system_message="You are an expert game asset designer.",
    )
    chat = chat.with_model("local", "gemma-4-26b-a4b")
    response = await chat.send_message(UserMessage(text="Generate sprites..."))
"""

from __future__ import annotations

import asyncio
import os
import uuid
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any, Union

from .gemma_loader import GemmaInference, InferenceResult
from .canon_enforcer import CanonEnforcer

logger = logging.getLogger(__name__)


@dataclass
class Message:
    role: str
    content: str
    name: Optional[str] = None

    def to_dict(self) -> Dict[str, str]:
        d = {"role": self.role, "content": self.content}
        if self.name:
            d["name"] = self.name
        return d


class UserMessage:
    def __init__(self, text: str):
        self.text = text
        self.content = text


class SystemMessage:
    def __init__(self, text: str):
        self.text = text
        self.content = text


class AssistantMessage:
    def __init__(self, text: str):
        self.text = text
        self.content = text


class LlmChat:
    def __init__(
        self,
        api_key: Optional[str] = None,
        session_id: Optional[str] = None,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        timeout: float = 120.0,
    ):
        self.api_key = api_key
        self.session_id = session_id or str(uuid.uuid4())
        self.system_message = system_message
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.provider = "local"
        self.model = "gemma-4-26b-a4b"
        self.history: List[Dict[str, str]] = []
        self._inference = GemmaInference()
        self._canon = CanonEnforcer()

    def with_model(self, provider: str, model: str) -> LlmChat:
        self.provider = provider
        self.model = model
        return self

    def with_temperature(self, temperature: float) -> LlmChat:
        self.temperature = temperature
        return self

    def with_max_tokens(self, max_tokens: int) -> LlmChat:
        self.max_tokens = max_tokens
        return self

    def with_timeout(self, timeout: float) -> LlmChat:
        self.timeout = timeout
        return self

    async def send_message(self, message: Union[UserMessage, str]) -> str:
        if isinstance(message, str):
            message = UserMessage(text=message)

        prompt = message.content
        try:
            result = await self._inference.generate(
                prompt=prompt,
                system_prompt=self.system_message,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
        except Exception as e:
            logger.error(f"Inference failed for session {self.session_id}: {e}")
            result = InferenceResult(content="", tokens_used=0, finish_reason="error")

        content = self._canon.enforce(result.content)

        self.history.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.utcnow().isoformat(),
        })
        self.history.append({
            "role": "assistant",
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        })

        return content

    async def generate(self, prompt: str) -> str:
        return await self.send_message(UserMessage(text=prompt))

    def send_message_sync(self, message: Union[UserMessage, str]) -> str:
        return asyncio.run(self.send_message(message))

    def generate_sync(self, prompt: str) -> str:
        return asyncio.run(self.generate(prompt))

    def clear_history(self):
        self.history = []

    def get_history(self) -> List[Dict[str, str]]:
        return self.history.copy()

    def __repr__(self) -> str:
        return f"LlmChat(provider={self.provider}, model={self.model}, session={self.session_id})"


class ChatLLM:
    DEFAULT_TIMEOUT = 120.0

    @classmethod
    async def chat(
        cls,
        api_key: str,
        model: str,
        messages: List[Dict[str, str]],
        provider: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        timeout: float = DEFAULT_TIMEOUT,
        **kwargs,
    ) -> "ChatResponse":
        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_msg = m["content"]
                break

        inference = GemmaInference()
        canon = CanonEnforcer()
        try:
            result = await inference.generate(
                prompt=last_user_msg,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as e:
            logger.error(f"ChatLLM inference failed: {e}")
            result = InferenceResult(content="", tokens_used=0, finish_reason="error")

        content = canon.enforce(result.content)

        return ChatResponse(
            content=content,
            model=model,
            provider=provider or "local",
            usage={"prompt_tokens": 0, "completion_tokens": result.tokens_used},
            finish_reason=result.finish_reason,
        )


@dataclass
class ChatResponse:
    content: str
    model: str
    provider: str
    usage: Dict[str, int] = field(default_factory=dict)
    raw_response: Dict[str, Any] = field(default_factory=dict)
    finish_reason: str = "stop"


@dataclass
class Conversation:
    messages: List[Message] = field(default_factory=list)

    def add_message(self, role: str, content: str):
        self.messages.append(Message(role=role, content=content))

    def to_list(self) -> List[Dict[str, str]]:
        return [m.to_dict() for m in self.messages]
