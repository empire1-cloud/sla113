"""SLA113 Admin Dashboard — FastAPI server for registry data and workflow execution."""

import json
import sys
import os
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from SLA113.execution_engine import Engine
from SLA113.execution_engine.logging import configure as configure_logging
from SLA113.execution_engine.handlers import (
    load_procedural_instrumental,
    load_soulfire_mastering,
    load_dna_watermark,
    load_render_engine,
)

configure_logging()

app = FastAPI(
    title="SLA113 Admin",
    description="SLA113 Operating System — Admin Dashboard API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = Engine()
engine.load_registries()
engine.register_handler("procedural-instrumental", load_procedural_instrumental)
engine.register_handler("soulfire-mastering", load_soulfire_mastering)
engine.register_handler("dna-watermark", load_dna_watermark)
engine.register_handler("sonic-forge", load_render_engine)
engine.register_handler("render-engine-preview", load_render_engine)


class RunRequest(BaseModel):
    inputs: Dict[str, Any]
    creator_id: str = "admin"


@app.get("/admin/health")
def health():
    return {"status": "ok", "service": "SLA113 Admin", "version": "1.0.0"}


@app.get("/admin/universes")
def get_universes():
    return engine.list_universes()


@app.get("/admin/products")
def get_products():
    return engine.list_products()


@app.get("/admin/capabilities")
def get_capabilities():
    from SLA113.execution_engine.register import RegistryLoader
    loader = RegistryLoader()
    return list(loader.load_capabilities().values())


@app.get("/admin/services")
def get_services():
    from SLA113.execution_engine.register import RegistryLoader
    loader = RegistryLoader()
    services = list(loader.load_services().values())
    return [
        {
            "id": s.id,
            "name": s.name,
            "capability": s.capability,
            "provider_type": s.provider_type,
            "lifecycle": s.lifecycle,
            "priority": s.priority,
            "cost_per_call": s.cost_per_call,
            "latency_ms": s.latency_ms,
        }
        for s in services
    ]


@app.get("/admin/workflows")
def get_workflows():
    from SLA113.execution_engine.register import RegistryLoader
    loader = RegistryLoader()
    workflows = list(loader.load_workflows().values())
    return [
        {
            "id": w.id,
            "name": w.name,
            "description": w.description,
            "version": w.version,
            "lifecycle": w.lifecycle,
            "owner": w.owner,
            "node_count": len(w.nodes),
            "edge_count": len(w.edges),
        }
        for w in workflows
    ]


@app.get("/admin/agents")
def get_agents():
    return engine.list_agents()


@app.get("/admin/domains/audio/genres")
def get_domain_genres():
    from SLA113.domains.audio import get_genres
    return {"count": len(genres := get_genres()), "genres": [{"id": g["id"], "name": g["name"]} for g in genres]}


@app.get("/admin/domains/audio/cultural-matrices")
def get_domain_matrices():
    from SLA113.domains.audio import get_cultural_matrices
    return {"count": len(m := get_cultural_matrices()), "matrices": [{"id": m["id"], "name": m["name"]} for m in m]}


@app.get("/admin/domains/audio/mastering-presets")
def get_domain_presets():
    from SLA113.domains.audio import get_mastering_presets
    return {"count": len(p := get_mastering_presets()), "presets": [{"id": p["id"], "name": p["name"]} for p in p]}


@app.post("/admin/run/{workflow_id}")
def run_workflow(workflow_id: str, req: RunRequest):
    result = engine.run(workflow_id, req.inputs, req.creator_id)
    return {
        "success": result.success,
        "error": result.error,
        "nodes": {
            nid: {
                "success": nr.success,
                "error": nr.error,
                "service_used": nr.service_used,
                "latency_ms": nr.latency_ms,
            }
            for nid, nr in result.node_results.items()
        },
        "outputs": {
            k: str(v)[:200] if isinstance(v, bytes) else v
            for k, v in result.final_outputs.items()
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9090)
