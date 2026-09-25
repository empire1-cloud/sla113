"""SLA113 Genesis Engine API — one request runs the whole deterministic pipeline.

Mounted under /api/sla113/genesis. No LLM calls; see backend/sla113/genesis/.
"""
import logging

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse

from sla113.genesis.logic import verify_math
from sla113.genesis.models import GameSpec, GenerateRequest, GenerateResponse
from sla113.genesis.pipeline import STAGES, GenesisPipeline, job_dir

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sla113/genesis", tags=["sla113-genesis"])
_pipeline = GenesisPipeline()


@router.get("/status")
async def genesis_status():
    return {
        "status": "online",
        "engine": "SLA113 Genesis Engine",
        "pipeline": STAGES,
        "math": "deterministic",
        "llm_calls": False,
        "regulatory_certification": False,
        "supported_game_types": ["fish_shooter"],
    }


@router.post("/verify")
async def genesis_verify(spec: GameSpec):
    return await run_in_threadpool(verify_math, spec)


@router.post("/generate", response_model=GenerateResponse)
async def genesis_generate(request: GenerateRequest):
    try:
        return await run_in_threadpool(
            _pipeline.run, request.spec, request.include_audio, request.include_vision, request.include_build
        )
    except Exception:
        logger.exception("Genesis generation failed")
        raise HTTPException(status_code=500, detail="Genesis generation failed")


@router.get("/jobs/{job_id}/download")
async def genesis_download(job_id: str):
    root = job_dir(job_id)
    if root is None:
        raise HTTPException(status_code=404, detail="Job not found")
    zips = sorted((root / "dist").glob("*_web.zip")) if (root / "dist").is_dir() else []
    if not zips:
        raise HTTPException(status_code=404, detail="Job has no build artifact")
    return FileResponse(zips[0], media_type="application/zip", filename=zips[0].name)
