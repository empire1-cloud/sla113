from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from .node import CapabilityDef, ServiceDef, WorkflowDef
from .runner import Runner, ServiceResolver


class RegistryLoader:
    """Loads registry data from the registries/ directory."""

    def __init__(self, registry_path: str = None):
        if registry_path is None:
            registry_path = os.path.join(
                os.path.dirname(__file__), "..", "registries"
            )
        self.registry_path = Path(registry_path)

    def _load_json(self, name: str) -> Dict[str, Any]:
        path = self.registry_path / name
        if not path.exists():
            return {}
        with open(path) as f:
            return json.load(f)

    def load_workflows(self) -> Dict[str, WorkflowDef]:
        data = self._load_json("workflow.json")
        return {
            w["id"]: WorkflowDef.from_dict(w)
            for w in data.get("workflows", [])
        }

    def load_services(self) -> Dict[str, ServiceDef]:
        data = self._load_json("service.json")
        return {
            s["id"]: ServiceDef.from_dict(s)
            for s in data.get("services", [])
        }

    def load_capabilities(self) -> Dict[str, CapabilityDef]:
        data = self._load_json("capability.json")
        return {
            c["id"]: CapabilityDef.from_dict(c)
            for c in data.get("capabilities", [])
        }

    def load_universes(self) -> List[Dict]:
        data = self._load_json("universe.json")
        return data.get("universes", [])

    def load_products(self) -> List[Dict]:
        data = self._load_json("product.json")
        return data.get("products", [])

    def load_agents(self) -> List[Dict]:
        data = self._load_json("agent.json")
        return data.get("agents", [])

    def build_resolver(self) -> ServiceResolver:
        return ServiceResolver(
            services=self.load_services(),
            capabilities=self.load_capabilities(),
        )

    def build_runner(self) -> Runner:
        return Runner(resolver=self.build_resolver())
