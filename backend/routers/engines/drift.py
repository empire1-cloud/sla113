"""
Drift Monitor endpoints.
"""
from fastapi import APIRouter, HTTPException
from typing import Optional

from services.drift_monitor import DriftMonitor

router = APIRouter(tags=["drift"])


@router.get("/drift-report")
async def get_drift_report(model: str = "all"):
    """Get drift analysis report for specified model."""
    return DriftMonitor.get_drift_report(model)


@router.get("/drift-report/{model}")
async def get_model_drift_report(model: str):
    """Get drift analysis report for a specific model."""
    valid_models = ["gpt-5.2", "claude-sonnet-4.5", "gemini-3-flash", "all"]
    if model not in valid_models:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid model. Choose from: {', '.join(valid_models)}"
        )
    return DriftMonitor.get_drift_report(model)


@router.post("/drift-reset")
async def reset_drift_metrics(model: Optional[str] = None):
    """Reset drift monitoring metrics."""
    DriftMonitor.reset(model)
    return {"status": "success", "message": f"Metrics reset for {'all models' if not model else model}"}
