"""
Anime Story Engine endpoints.
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

from services.anime_story_engine import AnimeStoryEngine
from services.canon_enforcer import CanonEnforcer
from services.drift_monitor import DriftMonitor
from services.error_handler import ErrorHandler, PipelineStage

router = APIRouter(tags=["anime"])


class AnimeStoryRequest(BaseModel):
    concept: str
    genre: Optional[str] = None
    episode_count: Optional[int] = None
    characters: Optional[List[str]] = None
    lore: Optional[dict] = None
    model: Optional[str] = None


class AnimeStoryResponse(BaseModel):
    title: str
    logline: str
    premise: str
    themes: List[str]
    tone: str
    story_arcs: List[dict]
    key_plot_points: List[str]
    climax: str
    resolution: str
    hooks: List[str]
    episode_structure: List[dict]


@router.post("/anime/story", response_model=AnimeStoryResponse)
async def generate_anime_story(payload: AnimeStoryRequest):
    """Generate narrative structure and story arcs for an anime project."""
    try:
        raw_story = await AnimeStoryEngine.generate_story_async(
            concept=payload.concept,
            genre=payload.genre,
            episode_count=payload.episode_count,
            characters=payload.characters,
            lore=payload.lore,
            model=payload.model
        )
        
        cleaned_story = CanonEnforcer.normalize(raw_story)
        DriftMonitor.check(cleaned_story, payload.model or "claude-sonnet-4.5")
        
        return AnimeStoryResponse(**cleaned_story)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/anime/story/quick")
async def generate_quick_story(concept: str, genre: Optional[str] = None, episode_count: Optional[int] = 12):
    """Generate story with minimal parameters."""
    try:
        raw_story = await AnimeStoryEngine.generate_story_async(
            concept=concept,
            genre=genre,
            episode_count=episode_count
        )
        
        cleaned_story = CanonEnforcer.normalize(raw_story)
        
        return cleaned_story
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )
