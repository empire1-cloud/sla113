"""
Empire Lyric Master - Backend API Router
FastAPI endpoints for the UI
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from LYRICA3.empire_lyric_master import EmpireLyricMaster

router = APIRouter(prefix="/api/empire", tags=["Empire Lyric Master"])

# Global instance (initialized once)
empire_master = None


class GenerateRequest(BaseModel):
    """Track generation request"""
    prompt: str
    genre_override: Optional[str] = None
    bpm_override: Optional[int] = None
    vulnerability_override: Optional[float] = None


@router.post("/generate")
async def generate_track(request: GenerateRequest):
    """
    Generate complete track from prompt
    
    POST /api/empire/generate
    {
        "prompt": "toxic breakup anthem trap 120bpm",
        "genre_override": "trap",  // optional
        "bpm_override": 120,        // optional
        "vulnerability_override": 0.7  // optional
    }
    
    Returns complete track blueprint with lyrics, MIDI, DSP, etc.
    """
    global empire_master
    
    # Initialize on first use
    if empire_master is None:
        empire_master = EmpireLyricMaster()
    
    try:
        # Generate track
        result = empire_master.generate_complete_track(
            user_prompt=request.prompt,
            genre_override=request.genre_override,
            bpm_override=request.bpm_override,
            vulnerability_override=request.vulnerability_override
        )
        
        # Convert to dict for JSON response
        return {
            "status": result.status,
            "user_prompt": result.user_prompt,
            "generation_time_ms": result.generation_time_ms,
            "track_metadata": result.track_metadata,
            "intent_analysis": result.intent_analysis,
            "creative_strategy": result.creative_strategy,
            "lyrics": result.lyrics,
            "rhythm_blueprint": result.rhythm_blueprint,
            "mastering_blueprint": result.mastering_blueprint,
            "soulfire_payload": result.soulfire_payload,
            "empire_performance_metrics": result.empire_performance_metrics,
            "warnings": result.warnings,
            "errors": result.errors
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Check if Empire Lyric Master is ready
    
    GET /api/empire/health
    """
    return {
        "status": "online",
        "message": "Empire Lyric Master ready",
        "api_cost": "$0 forever",
        "processing": "100% local"
    }


@router.get("/genres")
async def list_genres():
    """
    List supported genres
    
    GET /api/empire/genres
    """
    return {
        "genres": [
            {"value": "trap", "label": "Trap", "category": "urban"},
            {"value": "drill", "label": "Drill", "category": "urban"},
            {"value": "soul", "label": "Soul", "category": "classic"},
            {"value": "corrido", "label": "Corrido", "category": "latin"},
            {"value": "afrobeats", "label": "Afrobeats", "category": "global"},
            {"value": "uk_drill", "label": "UK Drill", "category": "global"},
            {"value": "kpop", "label": "K-pop", "category": "global"},
            {"value": "reggaeton", "label": "Reggaeton", "category": "latin"},
            {"value": "amapiano", "label": "Amapiano", "category": "global"},
            {"value": "dancehall", "label": "Dancehall", "category": "caribbean"},
            {"value": "french_rap", "label": "French Rap", "category": "global"},
            {"value": "german_trap", "label": "German Trap", "category": "global"},
            {"value": "brazilian_funk", "label": "Brazilian Funk", "category": "latin"},
            {"value": "arabic_trap", "label": "Arabic Trap", "category": "global"},
            {"value": "bollywood_pop", "label": "Bollywood Pop", "category": "global"},
            {"value": "jpop", "label": "J-pop", "category": "global"},
            {"value": "aus_hiphop", "label": "Australian Hip-Hop", "category": "global"},
            {"value": "nordic_folk", "label": "Nordic Folk-Pop", "category": "global"},
            {"value": "mainstream_pop", "label": "Mainstream Pop", "category": "pop"},
            {"value": "edm", "label": "EDM", "category": "electronic"}
        ]
    }
