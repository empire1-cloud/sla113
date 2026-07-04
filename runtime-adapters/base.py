"""Abstract base class and interface for all SLA113 Runtime Adapters.

The Runtime API defines how the Intelligence Layer interacts with
the underlying LLM/tool runtime. Each adapter implements this interface
for a specific backend (Homie, Claude, OpenAI, Local, Enterprise).

The Homie adapter is the primary implementation. Others are alternatives.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ToolResult:
    success: bool
    output: str = ""
    error: Optional[str] = None
    data: Optional[Dict] = None
    duration_ms: float = 0.0


@dataclass
class AgentSpec:
    persona: str
    goal: str
    context: Optional[Dict] = None
    tools: List[str] = field(default_factory=list)
    max_steps: int = 20


@dataclass
class AgentHandle:
    agent_id: str
    status: str = "running"
    result: Optional[Dict] = None


@dataclass
class Signal:
    source: str
    type: str
    payload: Dict
    timestamp: float = 0.0


@dataclass
class Event:
    type: str
    data: Dict
    source: str = ""


class RuntimeAdapter(ABC):
    """Abstract interface for all SLA113 Runtime Adapters."""

    name: str = "base"
    supports_tools: bool = False
    supports_agents: bool = False
    supports_memory: bool = False

    @abstractmethod
    async def execute(self, tool: str, args: Dict[str, Any]) -> ToolResult:
        ...

    async def query_knowledge_graph(self, query: str) -> List[Dict]:
        raise NotImplementedError

    async def recall_memory(self, query: str, tier: str = "WORKING") -> List[Dict]:
        raise NotImplementedError

    async def store_memory(self, content: str, tier: str = "WORKING") -> bool:
        raise NotImplementedError

    async def invoke_skill(self, skill: str, context: Dict[str, Any]) -> ToolResult:
        raise NotImplementedError

    async def spawn_agent(self, spec: AgentSpec) -> AgentHandle:
        raise NotImplementedError

    async def observe(self, source: str, signal: Signal) -> None:
        raise NotImplementedError

    async def dispatch(self, event: Event) -> None:
        raise NotImplementedError

    @abstractmethod
    async def health(self) -> Dict[str, Any]:
        ...


class AdapterRegistry:
    """Registry of available runtime adapters."""

    def __init__(self):
        self._adapters: Dict[str, RuntimeAdapter] = {}
        self._primary: Optional[str] = None

    def register(self, adapter: RuntimeAdapter, primary: bool = False) -> None:
        self._adapters[adapter.name] = adapter
        if primary or self._primary is None:
            self._primary = adapter.name

    def get(self, name: Optional[str] = None) -> Optional[RuntimeAdapter]:
        key = name or self._primary
        if key is None and self._adapters:
            key = next(iter(self._adapters))
        return self._adapters.get(key) if key else None

    def list(self) -> Dict[str, Dict[str, Any]]:
        return {
            name: {
                "supports_tools": a.supports_tools,
                "supports_agents": a.supports_agents,
                "supports_memory": a.supports_memory,
                "primary": name == self._primary,
            }
            for name, a in self._adapters.items()
        }

    @property
    def primary(self) -> Optional[RuntimeAdapter]:
        return self._adapters.get(self._primary) if self._primary else None
