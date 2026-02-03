"""
Art Direction Engine endpoints.
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

from services.art_direction_engine import ArtDirectionEngine
from services.canon_enforcer import CanonEnforcer
from services.drift_monitor import DriftMonitor
from services.error_handler import ErrorHandler, PipelineStage

router = APIRouter(tags=["art-direction"])


class ArtDirectionRequest(BaseModel):
    project: str
    genre: Optional[str] = None
    mood: Optional[str] = None
    target_audience: Optional[str] = None
    medium: Optional[str] = None
    constraints: Optional[List[str]] = None
    model: Optional[str] = None


class AnimeArtRequest(BaseModel):
    project: str
    sub_style: Optional[str] = None
    era: Optional[str] = None


class GameArtRequest(BaseModel):
    project: str
    game_genre: str
    platform: Optional[str] = None


class FilmArtRequest(BaseModel):
    project: str
    film_genre: str
    aspect_ratio: Optional[str] = None


class BrandArtRequest(BaseModel):
    brand_name: str
    industry: str
    personality: List[str]


class CharacterArtRequest(BaseModel):
    character_name: str
    character_type: str
    visual_style: str


class VisualStyleModel(BaseModel):
    genre: str
    influences: List[str]
    description: str


class ColorPaletteModel(BaseModel):
    primary: List[str]
    secondary: List[str]
    accents: List[str]
    mood_notes: str


class CharacterStyleModel(BaseModel):
    proportions: str
    linework: str
    shading: str
    expression_rules: List[str]
    silhouette_rules: List[str]


class EnvironmentStyleModel(BaseModel):
    lighting: str
    atmosphere: str
    detail_level: str
    composition_rules: List[str]


class CameraDirectionModel(BaseModel):
    framing: List[str]
    angles: List[str]
    motion_rules: List[str]


class TextureRulesModel(BaseModel):
    materials: List[str]
    surface_treatment: str
    consistency_requirements: List[str]


class ArtDirectionResponse(BaseModel):
    project_name: str
    visual_style: VisualStyleModel
    color_palette: ColorPaletteModel
    character_style: CharacterStyleModel
    environment_style: EnvironmentStyleModel
    camera_direction: CameraDirectionModel
    texture_rules: TextureRulesModel
    production_constraints: List[str]
    do_not_use: List[str]


@router.post("/art-direction", response_model=ArtDirectionResponse)
async def generate_art_direction(payload: ArtDirectionRequest):
    """Generate complete art direction for a creative project."""
    try:
        raw_direction = await ArtDirectionEngine.generate_direction_async(
            project=payload.project,
            genre=payload.genre,
            mood=payload.mood,
            target_audience=payload.target_audience,
            medium=payload.medium,
            constraints=payload.constraints,
            model=payload.model
        )
        
        cleaned_direction = CanonEnforcer.normalize(raw_direction)
        DriftMonitor.check(cleaned_direction, payload.model or "claude-sonnet-4.5")
        
        return ArtDirectionResponse(**cleaned_direction)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/art-direction/anime", response_model=ArtDirectionResponse)
async def generate_anime_art_direction(payload: AnimeArtRequest):
    """Generate anime-specific art direction."""
    try:
        raw_direction = await ArtDirectionEngine.anime_direction_async(
            project=payload.project,
            sub_style=payload.sub_style,
            era=payload.era
        )
        
        cleaned_direction = CanonEnforcer.normalize(raw_direction)
        DriftMonitor.check(cleaned_direction, "claude-sonnet-4.5")
        
        return ArtDirectionResponse(**cleaned_direction)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/art-direction/game", response_model=ArtDirectionResponse)
async def generate_game_art_direction(payload: GameArtRequest):
    """Generate game-specific art direction."""
    try:
        raw_direction = await ArtDirectionEngine.game_direction_async(
            project=payload.project,
            game_genre=payload.game_genre,
            platform=payload.platform
        )
        
        cleaned_direction = CanonEnforcer.normalize(raw_direction)
        DriftMonitor.check(cleaned_direction, "claude-sonnet-4.5")
        
        return ArtDirectionResponse(**cleaned_direction)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/art-direction/film", response_model=ArtDirectionResponse)
async def generate_film_art_direction(payload: FilmArtRequest):
    """Generate film/animation art direction."""
    try:
        raw_direction = await ArtDirectionEngine.film_direction_async(
            project=payload.project,
            film_genre=payload.film_genre,
            aspect_ratio=payload.aspect_ratio
        )
        
        cleaned_direction = CanonEnforcer.normalize(raw_direction)
        DriftMonitor.check(cleaned_direction, "claude-sonnet-4.5")
        
        return ArtDirectionResponse(**cleaned_direction)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/art-direction/brand", response_model=ArtDirectionResponse)
async def generate_brand_art_direction(payload: BrandArtRequest):
    """Generate brand visual identity direction."""
    try:
        raw_direction = await ArtDirectionEngine.brand_direction_async(
            brand_name=payload.brand_name,
            industry=payload.industry,
            personality=payload.personality
        )
        
        cleaned_direction = CanonEnforcer.normalize(raw_direction)
        DriftMonitor.check(cleaned_direction, "claude-sonnet-4.5")
        
        return ArtDirectionResponse(**cleaned_direction)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.post("/art-direction/character", response_model=ArtDirectionResponse)
async def generate_character_art_direction(payload: CharacterArtRequest):
    """Generate character-specific art direction."""
    try:
        raw_direction = await ArtDirectionEngine.character_art_direction_async(
            character_name=payload.character_name,
            character_type=payload.character_type,
            visual_style=payload.visual_style
        )
        
        cleaned_direction = CanonEnforcer.normalize(raw_direction)
        DriftMonitor.check(cleaned_direction, "claude-sonnet-4.5")
        
        return ArtDirectionResponse(**cleaned_direction)
    except Exception as e:
        error_response = ErrorHandler.handle(e, PipelineStage.STRATEGY)
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


@router.get("/art-direction/styles")
async def get_style_templates():
    """Get available visual style templates."""
    return ArtDirectionEngine.get_style_templates()


@router.get("/art-direction/color-moods")
async def get_color_moods():
    """Get available color mood presets."""
    return ArtDirectionEngine.get_color_moods()
