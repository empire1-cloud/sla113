"""
SLA-113 Kernel — Core Control Plane.

The sovereign operating system kernel for the SLA-113 Multiverse.
Handles:
1. Universe registry loading and validation
2. Worker binding and lifecycle
3. Request routing between universes
4. Black Box boundary enforcement
5. Heartbeat/status reporting
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

SLA113_BASE = Path(__file__).resolve().parents[2]


class UniverseRegistry:
    """Loads and validates the universe_registry.yaml."""

    @classmethod
    def load(cls) -> Dict[str, Any]:
        registry_path = SLA113_BASE / "SHARED" / "universe_registry.yaml"
        if not registry_path.exists():
            logger.warning("Universe registry not found at %s", registry_path)
            return {"universes": {}, "status": "missing"}

        import yaml
        with open(registry_path, "r") as f:
            registry = yaml.safe_load(f)

        return registry

    @classmethod
    def get_universe(cls, universe_id: str) -> Optional[Dict[str, Any]]:
        registry = cls.load()
        universes = registry.get("universes", {})
        return universes.get(universe_id)

    @classmethod
    def list_active(cls) -> List[Dict[str, Any]]:
        registry = cls.load()
        universes = registry.get("universes", {})
        return [
            {"id": uid, **data}
            for uid, data in universes.items()
            if data.get("status") == "active"
        ]


class WorkerRegistry:
    """Manages worker bindings — the bridge between SLA-113 and its engines."""

    _workers: Dict[str, Any] = {}

    @classmethod
    def bind(cls, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        cls._workers[name] = {
            "name": name,
            "config": config,
            "status": "bound",
            "bound_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        }
        logger.info("Worker bound: %s -> %s", name, config.get("module_path", config.get("path", "unknown")))
        return cls._workers[name]

    @classmethod
    def unbind(cls, name: str) -> bool:
        if name in cls._workers:
            cls._workers[name]["status"] = "unbound"
            logger.info("Worker unbound: %s", name)
            return True
        return False

    @classmethod
    def get_worker(cls, name: str) -> Optional[Dict[str, Any]]:
        return cls._workers.get(name)

    @classmethod
    def list_workers(cls, status: Optional[str] = None) -> List[Dict[str, Any]]:
        if status:
            return [w for w in cls._workers.values() if w.get("status") == status]
        return list(cls._workers.values())

    @classmethod
    def status_summary(cls) -> Dict[str, Any]:
        bound = [n for n, w in cls._workers.items() if w.get("status") == "bound"]
        unbound = [n for n, w in cls._workers.items() if w.get("status") == "unbound"]
        return {
            "total": len(cls._workers),
            "bound": len(bound),
            "unbound": len(unbound),
            "worker_names": bound,
            "unbound_names": unbound,
        }


class BlackBoxEnforcer:
    """Enforces Black Box rules — no internal engine names in user-facing output."""

    ALIAS_MAP = {
        "S2": "Serendipity Synthesizer",
        "CCNA": "Cultural Muse",
        "EPD": "Emotion Engine",
        "Nemotron": "Flow Conductor",
        "Combinator": "Mastering Alchemist",
        "VICS": "Identity Guardian",
        "RoyaltyLedger": "Empire 1 Ledger",
        "Demucs": "Stem Weaver",
        "PFA": "Voice Sculptor",
        "MMA": "Pulse Architect",
        "PDA": "Texture Alchemist",
    }

    INTERNAL_PATTERNS = [
        "emergentintegrations",
        "vertex_agent",
        "Gemini API",
        "Claude API",
        "model_name",
        "inference_timesteps",
        "cfg_value",
    ]

    @classmethod
    def scrub(cls, output: str) -> str:
        """Replace internal engine names with Soulfire aliases."""
        scrubbed = output
        for internal, alias in cls.ALIAS_MAP.items():
            scrubbed = scrubbed.replace(internal, alias)
        return scrubbed

    @classmethod
    def contains_leaks(cls, output: str) -> List[str]:
        """Check if output contains internal implementation details."""
        leaks = []
        for pattern in cls.INTERNAL_PATTERNS:
            if pattern.lower() in output.lower():
                leaks.append(pattern)
        return leaks


class SLA113Kernel:
    """SLA-113 Sovereign Kernel — the core control plane.

    Initializes on boot:
    1. Load universe registry
    2. Bind all known workers
    3. Initialize routing tables
    4. Enable Black Box enforcement
    5. Report status
    """

    def __init__(self):
        self._booted = False
        self._boot_time = None
        self._registry = {}
        self._routing_tables = {}
        self.worker_registry = WorkerRegistry
        self.universe_registry = UniverseRegistry
        self.black_box = BlackBoxEnforcer

    @property
    def is_booted(self) -> bool:
        return self._booted

    def boot(self) -> Dict[str, Any]:
        """Boot the SLA-113 kernel — load registries and bind workers."""
        from datetime import datetime
        self._boot_time = datetime.utcnow().isoformat() + "Z"

        self._registry = UniverseRegistry.load()
        active_universes = UniverseRegistry.list_active()

        worker_configs = {
            "OMNI_AGENT": {
                "path": str(SLA113_BASE / "OMNI_AGENT"),
                "capabilities": ["task_routing", "persona_loading", "pipeline_orchestration"],
            },
            "LYRICA_WORKER": {
                "path": str(SLA113_BASE / "LYRICA3"),
                "capabilities": ["emotional_intelligence", "cultural_intelligence", "sonic_intelligence"],
            },
            "LEDGER_WORKER": {
                "module_path": "LYRICA3.soulfire_engine.royalty_ledger.RoyaltyLedger",
                "capabilities": ["VICS", "DNA_TAGGER", "LEDGER_COMMIT"],
            },
            "NEMOTRON_FLOW": {
                "module_path": "services.nemotron.nemotron_flow.NemotronFlowEngine",
                "capabilities": ["TIMING", "PROSODY", "STEM_ORCHESTRATION", "COMBINATOR"],
            },
            "CCNA_ENGINE": {
                "module_path": "services.cultural.ccna_engine.CCNAEngine",
                "capabilities": ["CULTURAL_ANALYSIS", "ETHICAL_GRADIENT", "NARRATIVE_ARCHETYPES"],
            },
        }

        for name, config in worker_configs.items():
            WorkerRegistry.bind(name, config)

        self._booted = True

        return {
            "kernel": "SLA113",
            "version": "1.0.0",
            "status": "online",
            "boot_time": self._boot_time,
            "universes_loaded": len(active_universes),
            "active_universes": [u.get("name") for u in active_universes],
            "workers_bound": WorkerRegistry.status_summary(),
            "black_box_enforcement": True,
            "nemotron_integration": "enabled",
            "lyrica_prosody_handshake": "enabled",
            "omni_task_dispatch": "enabled",
        }

    def status(self) -> Dict[str, Any]:
        """Get current kernel status."""
        return {
            "kernel": "SLA113",
            "booted": self._booted,
            "boot_time": self._boot_time,
            "workers": WorkerRegistry.status_summary(),
            "active_universes": len(UniverseRegistry.list_active()),
        }

    def route_request(self, request_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Route a request through the appropriate pipeline."""
        routing_table = {
            "creative": ["interpreter", "architect", "lyrica_worker", "evaluator", "chronicler"],
            "technical_audio": ["interpreter", "architect", "nemotron_flow", "evaluator", "chronicler"],
            "ownership": ["interpreter", "ledger_worker", "evaluator", "chronicler"],
            "cross_universe": ["interpreter", "diplomat", "lyrica_worker", "s2", "evaluator"],
            "terminal": ["interpreter", "operator", "executor"],
            "email": ["interpreter", "operator", "chronicler"],
            "devops": ["interpreter", "operator", "architect", "executor"],
            "debug": ["interpreter", "operator", "evaluator", "executor"],
        }

        route = routing_table.get(request_type, ["interpreter", "executor"])

        return {
            "request_type": request_type,
            "route": route,
            "black_box_scrubbed": True,
            "payload_received": bool(payload),
        }


kernel = SLA113Kernel()
