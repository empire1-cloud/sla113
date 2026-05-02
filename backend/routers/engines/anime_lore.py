"""
Anime Lore Engine endpoints.
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

from services.anime_lore_engine import AnimeLoreEngine
from services.canon_enforcer import CanonEnforcer
from services.drift_monitor import DriftMonitor
from services.error_handler import ErrorHandler, PipelineStage

router = APIRouter(tags=["anime"])


class AnimeLoreRequest(BaseModel):
    world_concept: str
    genre: Optional[str] = None
    themes: Optional[List[str]] = None
    influences: Optional[List[str]] = None
    model: Optional[str] = None


class AnimeLoreResponse(BaseModel):
    world_name: str
    setting: str
    time_period: str
    core_mythology: List[str]
    factions: List[dict]
    locations: List[dict]
    power_system: dict
    history: List[str]
    cultural_elements: List[str]
    mysteries: List[str]
    rules_of_the_world: List[str]


@router.post("/anime/lore", response_model=AnimeLoreResponse)
async def generate_anime_lore(payload: AnimeLoreRequest):
    """Generate detailed world-building and lore for an anime project."""
    try:
        raw_lore = await AnimeLoreEngine.generate_lore_async(
            world_concept=payload.world_concept,
            genre=payload.genre,
            themes=payload.themes,
            influences=payload.influences,
            model=payload.model
        )
        
        cleaned_lore = CanonEnforcer.normalize(raw_lore)
        DriftMonitor.check(cleaned_lore, payload.model or "claude-sonnet-4.5")
        
        return AnimeLoreResponse(**cleaned_lore)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/anime/lore/quick")
async def generate_quick_lore(world_concept: str, genre: Optional[str] = None):
    """Generate lore with minimal parameters."""
    try:
        raw_lore = await AnimeLoreEngine.generate_lore_async(
            world_concept=world_concept,
            genre=genre
        )
        
        cleaned_lore = CanonEnforcer.normalize(raw_lore)
        
        return cleaned_lore
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )
