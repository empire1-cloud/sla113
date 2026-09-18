"""AI Router — Universal AI request layer.

Every application calls AI.request() instead of directly calling
OpenAI, Vertex, Claude, or any other provider.

Flow:
  App → AI.request() → Runtime → Provider Router → Best available provider
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from SLA113.runtime import CapabilityRuntime
from SLA113.execution_engine.provider import ProviderDef, ProviderType


@dataclass
class AIResponse:
    content: str
    model: str
    provider: str
    usage: Dict[str, int] = field(default_factory=dict)
    latency_ms: int = 0
    cost: float = 0.0


@dataclass
class EmbeddingResponse:
    embeddings: List[List[float]]
    model: str
    provider: str
    dimensions: int = 0
    latency_ms: int = 0


class AIRouter:
    """Universal AI interface. Routes all requests through the CapabilityRuntime.

    Example:
        ai = AIRouter()
        ai.register_providers(runtime)

        resp = ai.complete([
            {"role": "user", "content": "Hello"}
        ])
        print(resp.content)
    """

    CAPABILITY = "ai"

    def __init__(self, runtime: Optional[CapabilityRuntime] = None):
        self.runtime = runtime or CapabilityRuntime()
        self._key_checks: Dict[str, bool] = {}

    def register_providers(self, runtime: Optional[CapabilityRuntime] = None):
        if runtime:
            self.runtime = runtime

        self.runtime.register_provider(
            ProviderDef(id="openai", name="OpenAI", provider_type=ProviderType.CLOUD_API,
                         lifecycle="active" if self._key_available("EMERGENT_LLM_KEY") else "development",
                         priority=20, cost_per_call=0.01, latency_ms=2000,
                         config={"capability": "ai", "key_var": "EMERGENT_LLM_KEY"}),
            self._handle_openai,
        )
        self.runtime.register_provider(
            ProviderDef(id="vertex-ai", name="Vertex AI (Gemini)", provider_type=ProviderType.CLOUD_API,
                         lifecycle="development", priority=10, cost_per_call=0.002, latency_ms=3000,
                         config={"capability": "ai", "requires_iam": True}),
            self._handle_vertex,
        )
        self.runtime.register_provider(
            ProviderDef(id="local-llm", name="Local LLM", provider_type=ProviderType.LOCAL_MODEL,
                         lifecycle="development", priority=80, cost_per_call=0.0, latency_ms=5000,
                         config={"capability": "ai"}),
            self._handle_local,
        )
        self.runtime.register_provider(
            ProviderDef(id="mock-llm", name="Mock LLM (dev)", provider_type=ProviderType.LOCAL_DSP,
                         lifecycle="active", priority=95, cost_per_call=0.0, latency_ms=10,
                         config={"capability": "ai"}),
            self._handle_mock,
        )

    def _key_available(self, key_name: str) -> bool:
        if key_name not in self._key_checks:
            self._key_checks[key_name] = bool(os.environ.get(key_name))
        return self._key_checks[key_name]

    def _handle_openai(self, capability: str, inputs: Dict[str, Any],
                       provider: ProviderDef, creator_id: str) -> Dict[str, Any]:
        import json

        messages = inputs.get("messages", [])
        model = inputs.get("model", "gpt-4o")
        temperature = inputs.get("temperature", 0.7)
        max_tokens = inputs.get("max_tokens", 1024)

        api_key = os.environ.get(provider.config.get("key_var", "EMERGENT_LLM_KEY"), "")
        if not api_key:
            raise RuntimeError(f"OpenAI key not available")

        import urllib.request

        body = json.dumps({
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        return {
            "content": data["choices"][0]["message"]["content"],
            "model": data.get("model", model),
            "provider": provider.id,
            "usage": data.get("usage", {}),
        }

    def _handle_vertex(self, capability: str, inputs: Dict[str, Any],
                       provider: ProviderDef, creator_id: str) -> Dict[str, Any]:
        raise RuntimeError("Vertex AI provider not yet configured")

    def _handle_local(self, capability: str, inputs: Dict[str, Any],
                      provider: ProviderDef, creator_id: str) -> Dict[str, Any]:
        raise RuntimeError("Local LLM provider not yet configured")

    def _handle_mock(self, capability: str, inputs: Dict[str, Any],
                     provider: ProviderDef, creator_id: str) -> Dict[str, Any]:
        messages = inputs.get("messages", [])
        last = messages[-1]["content"] if messages else ""
        return {
            "content": f"[Mock AI] Received: {last[:100]}...",
            "model": "mock-llm-v1",
            "provider": provider.id,
            "usage": {"prompt_tokens": len(last), "completion_tokens": 20},
        }

    def complete(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        preference: Optional[str] = None,
        creator_id: str = "system",
    ) -> AIResponse:
        result = self.runtime.request(
            self.CAPABILITY,
            {
                "messages": messages,
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            preference=preference,
            creator_id=creator_id,
        )
        return AIResponse(
            content=result.get("content", ""),
            model=result.get("model", "unknown"),
            provider=result.get("provider", "unknown"),
            usage=result.get("usage", {}),
        )

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        preference: Optional[str] = None,
        creator_id: str = "system",
    ) -> str:
        return self.complete(
            [{"role": "user", "content": prompt}],
            model=model,
            preference=preference,
            creator_id=creator_id,
        ).content

    def embed(self, text: str, preference: Optional[str] = None) -> EmbeddingResponse:
        raise NotImplementedError("Embedding provider not yet implemented")

    def transcribe(self, audio_path: str, preference: Optional[str] = None) -> str:
        raise NotImplementedError("Transcription provider not yet implemented")
