"""AI Capability Pack — Universal AI request layer.

Usage:
    from SLA113.capabilities.ai import AIRouter
    from SLA113.runtime import CapabilityRuntime

    rt = CapabilityRuntime()
    ai = AIRouter(rt)
    ai.register_providers()

    resp = ai.complete([{"role": "user", "content": "Hello"}])
    print(resp.content)
"""

from .router import AIRouter, AIResponse, EmbeddingResponse

__all__ = ["AIRouter", "AIResponse", "EmbeddingResponse"]
