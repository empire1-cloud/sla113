"""
Anime Character Engine endpoints.
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

from services.anime_character_engine import AnimeCharacterEngine
from services.canon_enforcer import CanonEnforcer
from services.drift_monitor import DriftMonitor
from services.error_handler import ErrorHandler, PipelineStage

router = APIRouter(tags=["anime"])


class AnimeCharacterRequest(BaseModel):
    concept: str
    role: Optional[str] = None
    genre: Optional[str] = None
    abilities_type: Optional[str] = None
    context: Optional[str] = None
    model: Optional[str] = None


class ProtagonistRequest(BaseModel):
    concept: str
    genre: Optional[str] = None
    abilities_type: Optional[str] = None


class AntagonistRequest(BaseModel):
    concept: str
    genre: Optional[str] = None
    protagonist: Optional[str] = None


class CastRequest(BaseModel):
    story_concept: str
    genre: Optional[str] = None
    cast_size: Optional[int] = 5


class CharacterRelationshipsModel(BaseModel):
    allies: List[str]
    rivals: List[str]
    enemies: List[str]


class AnimeCharacterResponse(BaseModel):
    name: str
    role: str
    appearance: str
    personality: List[str]
    abilities: List[str]
    motivations: List[str]
    backstory: str
    relationships: CharacterRelationshipsModel
    arc: str


@router.post("/anime/character", response_model=AnimeCharacterResponse)
async def generate_anime_character(payload: AnimeCharacterRequest):
    """Generate an original anime character."""
    try:
        raw_character = await AnimeCharacterEngine.generate_character_async(
            concept=payload.concept,
            role=payload.role,
            genre=payload.genre,
            abilities_type=payload.abilities_type,
            context=payload.context,
            model=payload.model
        )
        
        cleaned_character = CanonEnforcer.normalize(raw_character)
        DriftMonitor.check(cleaned_character, payload.model or "claude-sonnet-4.5")
        
        return AnimeCharacterResponse(**cleaned_character)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/anime/protagonist", response_model=AnimeCharacterResponse)
async def generate_protagonist(payload: ProtagonistRequest):
    """Generate an anime protagonist character."""
    try:
        raw_character = await AnimeCharacterEngine.generate_protagonist_async(
            concept=payload.concept,
            genre=payload.genre,
            abilities_type=payload.abilities_type
        )
        
        cleaned_character = CanonEnforcer.normalize(raw_character)
        DriftMonitor.check(cleaned_character, "claude-sonnet-4.5")
        
        return AnimeCharacterResponse(**cleaned_character)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/anime/antagonist", response_model=AnimeCharacterResponse)
async def generate_antagonist(payload: AntagonistRequest):
    """Generate an anime antagonist/villain character."""
    try:
        raw_character = await AnimeCharacterEngine.generate_antagonist_async(
            concept=payload.concept,
            genre=payload.genre,
            protagonist=payload.protagonist
        )
        
        cleaned_character = CanonEnforcer.normalize(raw_character)
        DriftMonitor.check(cleaned_character, "claude-sonnet-4.5")
        
        return AnimeCharacterResponse(**cleaned_character)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/anime/cast")
async def generate_cast(payload: CastRequest):
    """Generate a full cast of anime characters for a story."""
    try:
        characters = await AnimeCharacterEngine.generate_cast_async(
            story_concept=payload.story_concept,
            genre=payload.genre,
            cast_size=payload.cast_size or 5
        )
        
        cleaned_characters = [CanonEnforcer.normalize(c) for c in characters]
        
        return {"cast": cleaned_characters, "count": len(cleaned_characters)}
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.get("/anime/archetypes")
async def get_character_archetypes():
    """Get available character archetypes."""
    return AnimeCharacterEngine.get_archetypes()


@router.get("/anime/genres")
async def get_anime_genres():
    """Get available anime genres."""
    return AnimeCharacterEngine.get_genres()
