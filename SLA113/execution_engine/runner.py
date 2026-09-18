from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional

from .graph import Graph
from .logging import node_end, node_start, workflow_end, workflow_start
from .node import (
    CapabilityDef,
    GraphResult,
    NodeResult,
    ServiceDef,
    WorkflowDef,
)


class ServiceResolver:
    """Resolves services for a given capability."""

    def __init__(self, services: Dict[str, ServiceDef], capabilities: Dict[str, CapabilityDef]):
        self.services = services
        self.capabilities = capabilities

    def resolve(self, capability: str, preference: Optional[str] = None) -> Optional[ServiceDef]:
        if preference and preference in self.services:
            svc = self.services[preference]
            if svc.capability == capability and svc.lifecycle == "active":
                return svc

        cap = self.capabilities.get(capability)
        if not cap:
            return None

        candidates = [
            self.services[sid]
            for sid in cap.services
            if sid in self.services and self.services[sid].lifecycle == "active"
        ]
        candidates.sort(key=lambda s: s.priority, reverse=True)
        return candidates[0] if candidates else None

    def resolve_all(self, capability: str) -> List[ServiceDef]:
        cap = self.capabilities.get(capability)
        if not cap:
            return []
        candidates = [
            self.services[sid]
            for sid in cap.services
            if sid in self.services
        ]
        candidates.sort(key=lambda s: s.priority, reverse=True)
        return candidates


class Runner:
    """Executes a workflow graph by resolving services and running nodes in dependency order."""

    def __init__(self, resolver: ServiceResolver, handlers: Dict[str, Callable] = None):
        self.resolver = resolver
        self.handlers: Dict[str, Callable] = handlers or {}

    def register_handler(self, service_id: str, handler: Callable):
        self.handlers[service_id] = handler

    def run(self, workflow: WorkflowDef, inputs: Dict[str, Any], creator_id: str = "anonymous") -> GraphResult:
        workflow_start(workflow.id, inputs)
        wf_start = time.time()
        graph = Graph(workflow)
        errors = graph.validate()
        if errors:
            return GraphResult(
                workflow_id=workflow.id,
                success=False,
                error=f"Graph validation failed: {'; '.join(errors)}",
            )

        order = graph.execution_order()
        node_results: Dict[str, NodeResult] = {}
        ctx: Dict[str, Any] = dict(inputs)

        for node_id in order:
            node = graph.nodes[node_id]
            start = time.time()

            resolved_inputs = {}
            for k, v in node.inputs.items():
                if k in ctx:
                    resolved_inputs[k] = ctx[k]

            preference = node.config.get("service_preference")
            service = self.resolver.resolve(node.capability, preference)

            if not service:
                node_results[node_id] = NodeResult(
                    node_id=node_id,
                    success=False,
                    error=f"No active service for capability '{node.capability}'",
                )
                continue

            handler = self.handlers.get(service.id)
            if not handler:
                node_results[node_id] = NodeResult(
                    node_id=node_id,
                    success=False,
                    error=f"No handler registered for service '{service.id}'",
                    service_used=service.id,
                    latency_ms=int((time.time() - start) * 1000),
                )
                continue

            try:
                node_start(node_id, node.capability, service.id)
                result = handler(node, resolved_inputs, service, creator_id)
                elapsed = int((time.time() - start) * 1000)
                node_results[node_id] = NodeResult(
                    node_id=node_id,
                    success=True,
                    outputs=result if isinstance(result, dict) else {"output": result},
                    service_used=service.id,
                    latency_ms=elapsed,
                )
                node_end(node_id, True, elapsed)
                if isinstance(result, dict):
                    ctx.update(result)
                else:
                    ctx[node.outputs.get("output", "output")] = result
            except Exception as e:
                elapsed = int((time.time() - start) * 1000)
                node_results[node_id] = NodeResult(
                    node_id=node_id,
                    success=False,
                    error=str(e),
                    service_used=service.id,
                    latency_ms=elapsed,
                )
                node_end(node_id, False, elapsed, str(e))

        all_success = all(r.success for r in node_results.values())
        wf_elapsed = (time.time() - wf_start) * 1000
        final_outputs = {}
        if all_success:
            for nid in order:
                for field_name in graph.nodes[nid].outputs:
                    if field_name in ctx:
                        final_outputs[field_name] = ctx[field_name]

        return GraphResult(
            workflow_id=workflow.id,
            success=all_success,
            node_results=node_results,
            final_outputs=final_outputs,
            error=None if all_success else "One or more nodes failed",
        )
        workflow_end(workflow.id, all_success, wf_elapsed, result.error if not all_success else None)
