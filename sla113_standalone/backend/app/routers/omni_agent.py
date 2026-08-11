"""Omni Agent Router — Persona-Based Task Orchestration

Wraps the omni_agent orchestrator for SLA113 deployment.
Provides scan, run, status, and reporting endpoints.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "OMNI_AGENT"))

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/omni-agent", tags=["omni-agent"])

_ORCHESTRATOR = None


def _get_orchestrator():
    global _ORCHESTRATOR
    if _ORCHESTRATOR is None:
        try:
            from omni_agent.orchestrator import Orchestrator, load_config
            repo_root = Path(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
            config = load_config(repo_root)
            _ORCHESTRATOR = Orchestrator(repo_root, config)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Orchestrator unavailable: {e}")
    return _ORCHESTRATOR


class TaskRunRequest(BaseModel):
    task_id: str
    dry_run: bool = False


@router.get("/status")
async def omni_agent_status():
    try:
        orch = _get_orchestrator()
        return orch.status()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scan")
async def omni_agent_scan():
    try:
        orch = _get_orchestrator()
        return orch.scan()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run")
async def omni_agent_run(req: TaskRunRequest):
    try:
        orch = _get_orchestrator()
        return orch.run_task(req.task_id, dry_run=req.dry_run)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-next")
async def omni_agent_run_next(dry_run: bool = False):
    try:
        orch = _get_orchestrator()
        result = orch.run_next(dry_run=dry_run)
        if result is None:
            return {"message": "No runnable tasks", "result": None}
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report")
async def omni_agent_report():
    try:
        orch = _get_orchestrator()
        path = orch.report()
        return {"report_path": str(path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/roi")
async def omni_agent_roi(window: str = None):
    try:
        orch = _get_orchestrator()
        return orch.compute_roi(window=window)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
