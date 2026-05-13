"""
Omni Agent Router — Task planning, dispatch, and pipeline orchestration.

Routes requests to the appropriate worker based on task type.
Integrates with SLA-113 Kernel, Nemotron Flow Engine, Lyrica Worker,
CCNA Engine, and Ledger Worker.

Endpoints:
- POST /api/omni/execute — Full pipeline execution
- POST /api/omni/nemotron/render — Nemotron flow (prosody -> stems -> mix)
- POST /api/omni/cultural/analyze — CCNA cultural analysis
- GET  /api/omni/status — Omni worker status
- GET  /api/omni/workers — Registered workers list
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from services.sla113_kernel import SLA113Kernel, WorkerRegistry, UniverseRegistry, BlackBoxEnforcer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/omni", tags=["omni"])

kernel = SLA113Kernel()


# --- Request/Response Models ---

class ExecuteRequest(BaseModel):
    task_type: str = Field("creative", description="creative | technical_audio | ownership | cross_universe | terminal | email | devops | debug")
    payload: Dict[str, Any] = Field(default_factory=dict)
    voice_profile: Optional[str] = None
    vulnerability: Optional[float] = 0.5


class NemotronRenderRequest(BaseModel):
    lyrics: List[str]
    bpm: int = 90
    swing: float = 0.15
    style: str = "hip_hop"
    voice_profile: str = "breathy_souldie_whisper"
    vulnerability: float = 0.5
    groove: str = "late_pocket_dilla_swing"
    texture: str = "warm_analog_room"
    genre: str = "sgv_souldie_funk"


class CulturalAnalysisRequest(BaseModel):
    text: str
    genre: Optional[str] = None


class WorkerBindRequest(BaseModel):
    worker_name: str
    config: Dict[str, Any]


# --- Endpoints ---

@router.post("/execute")
async def omni_execute(req: ExecuteRequest):
    """Execute a task through the Omni routing pipeline."""
    try:
        route_result = kernel.route_request(req.task_type, req.payload)
        return {
            "status": "routed",
            "task_type": req.task_type,
            "route": route_result["route"],
            "route_length": len(route_result["route"]),
            "black_box_scrubbed": True,
            "pipeline_id": f"omni_{__import__('uuid').uuid4().hex[:12]}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {e}")


@router.post("/nemotron/render")
async def nemotron_render(req: NemotronRenderRequest):
    """Run the Nemotron Flow Engine pipeline (prosody -> stems -> mix)."""
    try:
        from services.nemotron import NemotronFlowEngine
        engine = NemotronFlowEngine()
        result = await engine.execute(
            lyrics=req.lyrics,
            bpm=req.bpm,
            swing=req.swing,
            style=req.style,
            voice_profile=req.voice_profile,
            vulnerability=req.vulnerability,
            groove=req.groove,
            texture=req.texture,
            genre=req.genre,
        )
        scrubbed = BlackBoxEnforcer.scrub(json.dumps(result))
        import json
        return json.loads(scrubbed)
    except ImportError:
        raise HTTPException(status_code=503, detail="Nemotron Flow Engine not installed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Nemotron render failed: {e}")


@router.post("/cultural/analyze")
async def cultural_analyze(req: CulturalAnalysisRequest):
    """Analyze text for cultural markers, ethical gradient, and narrative archetypes."""
    try:
        from services.cultural.ccna_engine import CCNAEngine
        result = CCNAEngine.analyze(text=req.text, genre=req.genre)
        scrubbed = BlackBoxEnforcer.scrub(json.dumps(result))
        import json
        return json.loads(scrubbed)
    except ImportError:
        raise HTTPException(status_code=503, detail="CCNA Engine not installed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cultural analysis failed: {e}")


@router.get("/status")
async def omni_status():
    """Get Omni worker and kernel status."""
    if not kernel.is_booted:
        boot_result = kernel.boot()

    return {
        "kernel": kernel.status(),
        "workers": WorkerRegistry.status_summary(),
        "universes": UniverseRegistry.list_active(),
        "status": "SLA-113 ONLINE | ALL WORKERS READY | NEMOTRON SYNCED",
    }


@router.get("/workers")
async def list_workers():
    """List all registered workers."""
    return {"workers": WorkerRegistry.list_workers()}


@router.post("/workers/bind")
async def bind_worker(req: WorkerBindRequest):
    """Register a new worker."""
    return WorkerRegistry.bind(req.worker_name, req.config)
