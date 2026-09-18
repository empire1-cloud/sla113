"""Runtime Adapters — SLA113 Runtime API implementations.

Adapters provide a uniform interface over different LLM/tool backends:
- Homie (primary)
- Claude (Anthropic)
- OpenAI (OpenAI)
- Local (Ollama)
- Enterprise (self-hosted)
"""

from base import (
    AdapterRegistry,
    AgentHandle,
    AgentSpec,
    Event,
    RuntimeAdapter,
    Signal,
    ToolResult,
)
from homie_adapter import HomieAdapter, create_default_registry
from cloud_adapters import ClaudeAdapter, OpenAIAdapter
from local_adapters import EnterpriseAdapter, LocalAdapter

__all__ = [
    "AdapterRegistry",
    "RuntimeAdapter",
    "ToolResult",
    "AgentSpec",
    "AgentHandle",
    "Signal",
    "Event",
    "HomieAdapter",
    "ClaudeAdapter",
    "OpenAIAdapter",
    "LocalAdapter",
    "EnterpriseAdapter",
    "create_default_registry",
]
