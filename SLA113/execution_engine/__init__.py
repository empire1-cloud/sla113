"""SLA113 Execution Engine — DAG-based workflow runner.

Usage:
    from execution_engine import Engine

    engine = Engine()
    engine.load_registries()
    result = engine.run("instrumental_generation", {
        "prompt": "Chicano soul at 92 BPM in C minor",
        "bpm": 92,
        "key": "C",
        "cultural_matrix": "LA SGV Chicano Heritage"
    })
    print(result.success, result.final_outputs)
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from .node import GraphResult
from .register import RegistryLoader
from .runner import Runner


class Engine:
    """Top-level SLA113 Execution Engine. Loads registries, resolves services, runs workflows."""

    def __init__(self, registry_path: Optional[str] = None):
        self.loader = RegistryLoader(registry_path)
        self.runner: Optional[Runner] = None
        self._initialized = False

    def load_registries(self):
        self.runner = self.loader.build_runner()
        self._initialized = True

    def register_handler(self, service_id: str, handler: Callable):
        if not self._initialized:
            self.load_registries()
        self.runner.register_handler(service_id, handler)

    def run(self, workflow_id: str, inputs: Dict[str, Any], creator_id: str = "anonymous") -> GraphResult:
        if not self._initialized:
            self.load_registries()

        workflows = self.loader.load_workflows()
        workflow = workflows.get(workflow_id)
        if not workflow:
            return GraphResult(
                workflow_id=workflow_id,
                success=False,
                error=f"Workflow '{workflow_id}' not found in registry",
            )

        if workflow.lifecycle != "active":
            return GraphResult(
                workflow_id=workflow_id,
                success=False,
                error=f"Workflow '{workflow_id}' is in lifecycle '{workflow.lifecycle}', not 'active'",
            )

        return self.runner.run(workflow, inputs, creator_id)

    def list_workflows(self) -> Dict[str, str]:
        workflows = self.loader.load_workflows()
        return {wid: w.name for wid, w in workflows.items()}

    def list_universes(self) -> list:
        return self.loader.load_universes()

    def list_products(self) -> list:
        return self.loader.load_products()

    def list_agents(self) -> list:
        return self.loader.load_agents()
