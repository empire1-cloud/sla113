from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class NodeDef:
    """A single execution node in a workflow graph."""
    id: str
    capability: str
    inputs: Dict[str, str]
    outputs: Dict[str, str]
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EdgeDef:
    """A directed edge connecting two nodes with field mapping."""
    from_node: str
    to_node: str
    map: Dict[str, str]


@dataclass
class WorkflowDef:
    """A registered workflow DAG."""
    id: str
    name: str
    description: str
    version: str
    lifecycle: str
    owner: str
    nodes: List[NodeDef]
    edges: List[EdgeDef]

    @classmethod
    def from_dict(cls, data: dict) -> WorkflowDef:
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            version=data.get("version", "0.1.0"),
            lifecycle=data.get("lifecycle", "development"),
            owner=data.get("owner", ""),
            nodes=[NodeDef(**n) for n in data.get("nodes", [])],
            edges=[EdgeDef(from_node=e["from"], to_node=e["to"], map=e["map"]) for e in data.get("edges", [])],
        )


@dataclass
class ServiceDef:
    """A concrete service implementing a capability."""
    id: str
    name: str
    capability: str
    provider_type: str
    lifecycle: str
    priority: int
    cost_per_call: float = 0.0
    latency_ms: int = 0
    config: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> ServiceDef:
        return cls(
            id=data["id"],
            name=data.get("name", data["id"]),
            capability=data["capability"],
            provider_type=data.get("provider_type", "local_dsp"),
            lifecycle=data.get("lifecycle", "development"),
            priority=data.get("priority", 50),
            cost_per_call=data.get("cost_per_call", 0.0),
            latency_ms=data.get("latency_ms", 0),
            config=data.get("config", {}),
        )


@dataclass
class CapabilityDef:
    """A capability the platform provides."""
    id: str
    name: str
    description: str
    lifecycle: str
    services: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> CapabilityDef:
        return cls(
            id=data["id"],
            name=data.get("name", data["id"]),
            description=data.get("description", ""),
            lifecycle=data.get("lifecycle", "development"),
            services=data.get("services", []),
        )


@dataclass
class NodeResult:
    """Result from executing a single node."""
    node_id: str
    success: bool
    outputs: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    service_used: Optional[str] = None
    latency_ms: int = 0


@dataclass
class GraphResult:
    """Result from executing an entire workflow graph."""
    workflow_id: str
    success: bool
    node_results: Dict[str, NodeResult] = field(default_factory=dict)
    final_outputs: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
