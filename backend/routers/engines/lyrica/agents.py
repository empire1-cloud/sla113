"""
Lyrica 3 Pro — Agent API Endpoints.

All Lyrica agents exposed on the main Hybrid AI Stack server under /api/lyrica/*.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

router = APIRouter(prefix="/lyrica", tags=["Lyrica"])


# ---------------------------------------------------------------------------
# Request Models
# ---------------------------------------------------------------------------

class GhostwriterRequest(BaseModel):
    concept: str = Field(..., min_length=3, max_length=1000)
    genre: str = Field(default="trap", description="trap|boom_bap|melodic|corrido|spoken_word|g_funk")
    mood: str = Field(default="struggle", description="struggle|heartbreak|triumph|rage|peace")
    num_verses: int = Field(default=2, ge=1, le=5)
    include_chorus: bool = True
    include_bridge: bool = False
    tempo_bpm: int = Field(default=140, ge=60, le=200)
    custom_instructions: Optional[str] = None


class MMARequest(BaseModel):
    groove: str = Field(default="trap", description="trap|boom_bap|g_funk|corrido")
    tempo_bpm: Optional[int] = Field(default=None, ge=60, le=200)
    bars: int = Field(default=4, ge=1, le=32)
    seed: Optional[int] = None


class PFARequest(BaseModel):
    input_path: str = Field(..., description="Path to vocal audio file")
    apply_fry: bool = True
    apply_breaths: bool = True
    fry_rate: float = Field(default=60.0, ge=40.0, le=80.0)
    fry_depth: float = Field(default=0.05, ge=0.02, le=0.08)
    breath_duration_ms: float = Field(default=400, ge=200, le=600)
    breath_volume_db: float = Field(default=-15, ge=-18, le=-12)


class PDARequest(BaseModel):
    input_path: str = Field(..., description="Path to audio file")
    texture: str = Field(default="vocal_bus", description="tape_saturation|ssl_console|vocal_bus|lofi_vinyl")


class DNATagRequest(BaseModel):
    file_path: str
    contributor_id: Optional[str] = None


class SynapsePayloadRequest(BaseModel):
    track_title: str = Field(..., min_length=1, max_length=200)
    genre: Optional[str] = None
    mood: Optional[str] = None
    contributor_id: Optional[str] = None
    ghostwriter_output: Optional[dict] = None
    mma_output: Optional[dict] = None
    pfa_output: Optional[dict] = None
    pda_output: Optional[dict] = None
    voxcpm_output: Optional[dict] = None
    fx_output: Optional[dict] = None


# ---------------------------------------------------------------------------
# Ghostwriter
# ---------------------------------------------------------------------------

@router.post("/ghostwriter/generate")
async def ghostwriter_generate(request: GhostwriterRequest):
    """Generate Soulfire Injected lyrics in LML format."""
    try:
        from app.services.lyrica.ghostwriter import GhostwriterAgent
        agent = GhostwriterAgent()
        result = await agent.generate(
            concept=request.concept,
            genre=request.genre,
            mood=request.mood,
            num_verses=request.num_verses,
            include_chorus=request.include_chorus,
            include_bridge=request.include_bridge,
            tempo_bpm=request.tempo_bpm,
            custom_instructions=request.custom_instructions,
        )
        return {"success": True, **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ghostwriter/genres")
async def ghostwriter_genres():
    """List available genres and flow styles."""
    from app.services.lyrica.ghostwriter import GENRE_PROMPTS
    return {
        "success": True,
        "genres": {k: v[:60] + "..." for k, v in GENRE_PROMPTS.items()},
    }


# ---------------------------------------------------------------------------
# MMA (Beat Generation)
# ---------------------------------------------------------------------------

@router.post("/mma/generate")
async def mma_generate(request: MMARequest):
    """Generate a humanized beat with Late-Pocket Swing."""
    try:
        from app.services.lyrica.mma import MMAAgent
        agent = MMAAgent()
        result = agent.generate_beat(
            groove=request.groove,
            tempo_bpm=request.tempo_bpm,
            bars=request.bars,
            seed=request.seed,
        )
        return {"success": True, **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mma/grooves")
async def mma_grooves():
    """List available groove templates."""
    from app.services.lyrica.mma import MMAAgent
    agent = MMAAgent()
    return {"success": True, "grooves": agent.list_grooves()}


# ---------------------------------------------------------------------------
# PFA (Vocal Phonation)
# ---------------------------------------------------------------------------

@router.post("/pfa/process")
async def pfa_process(request: PFARequest):
    """Apply vocal fry and adaptive breath insertion to audio."""
    try:
        from app.services.lyrica.pfa import PFAAgent
        agent = PFAAgent()
        result = agent.process(
            input_path=request.input_path,
            apply_fry=request.apply_fry,
            apply_breaths=request.apply_breaths,
            fry_rate=request.fry_rate,
            fry_depth=request.fry_depth,
            breath_duration_ms=request.breath_duration_ms,
            breath_volume_db=request.breath_volume_db,
        )
        return {"success": True, **result}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Audio file not found: {request.input_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# PDA (Psychoacoustic DSP)
# ---------------------------------------------------------------------------

@router.post("/pda/process")
async def pda_process(request: PDARequest):
    """Apply psychoacoustic texture preset to audio."""
    try:
        from app.services.lyrica.pda import PDAAgent
        agent = PDAAgent()
        result = agent.process(input_path=request.input_path, texture=request.texture)
        return {"success": True, **result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Audio file not found: {request.input_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pda/textures")
async def pda_textures():
    """List available PDA texture presets."""
    from app.services.lyrica.pda import PDAAgent
    agent = PDAAgent()
    return {"success": True, "textures": agent.list_textures()}


# ---------------------------------------------------------------------------
# DNA Tagger
# ---------------------------------------------------------------------------

@router.post("/dna/tag")
async def dna_tag(request: DNATagRequest):
    """Compute and store DNA provenance tag for an audio file."""
    try:
        from app.services.lyrica.dna_tagger import tag_audio_file
        result = tag_audio_file(request.file_path, request.contributor_id)
        return {"success": True, **result}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Audio file not found: {request.file_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Soulfire Synapse Payload
# ---------------------------------------------------------------------------

@router.post("/synapse/assemble")
async def synapse_assemble(request: SynapsePayloadRequest):
    """Assemble a Soulfire Synapse Payload from agent outputs."""
    try:
        from app.services.lyrica.dna_tagger import SoulfireSynapsePayload
        assembler = SoulfireSynapsePayload()
        result = assembler.assemble(
            track_title=request.track_title,
            ghostwriter_output=request.ghostwriter_output,
            mma_output=request.mma_output,
            pfa_output=request.pfa_output,
            pda_output=request.pda_output,
            voxcpm_output=request.voxcpm_output,
            fx_output=request.fx_output,
            contributor_id=request.contributor_id,
            genre=request.genre,
            mood=request.mood,
        )
        return {"success": True, **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# S2 Disruption Engine
# ---------------------------------------------------------------------------

class S2GrooveRequest(BaseModel):
    source_path: str = Field(..., description="Path to groove source audio (e.g. SGV beat)")
    target_path: str = Field(..., description="Path to target audio (e.g. choir, strings)")
    smoothing_hz: float = Field(default=10.0, ge=1.0, le=50.0)


class S2MorphRequest(BaseModel):
    audio_a_path: str = Field(..., description="Path to audio A")
    audio_b_path: str = Field(..., description="Path to audio B (rhythmic source)")
    morph_ratio: float = Field(default=0.5, ge=0.0, le=1.0)


class GhostAudioRequest(BaseModel):
    input_path: str = Field(..., description="Path to raw memory audio (VHS, voicemail, cassette)")
    artifact_id: Optional[str] = None


@router.post("/s2/transplant-groove")
async def s2_transplant_groove(request: S2GrooveRequest):
    """Extract groove from source and force target to swing with it."""
    try:
        from app.services.lyrica.s2_engine import S2DisruptionEngine
        engine = S2DisruptionEngine()
        result = engine.transplant_groove(request.source_path, request.target_path, request.smoothing_hz)
        return {"success": True, **result}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/s2/spectral-morph")
async def s2_spectral_morph(request: S2MorphRequest):
    """Fuse frequencies of two audio sources via STFT interpolation."""
    try:
        from app.services.lyrica.s2_engine import S2DisruptionEngine
        engine = S2DisruptionEngine()
        result = engine.spectral_morph(request.audio_a_path, request.audio_b_path, request.morph_ratio)
        return {"success": True, **result}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/s2/ghost-ingest")
async def s2_ghost_ingest(request: GhostAudioRequest):
    """Ingest raw memory audio and separate into ghost drum kit + 808 sub."""
    try:
        from app.services.lyrica.s2_engine import S2DisruptionEngine
        engine = S2DisruptionEngine()
        result = engine.ingest_ghost_audio(request.input_path, request.artifact_id)
        return {"success": True, **result}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Render Engine (MSGO Protocol)
# ---------------------------------------------------------------------------

class RenderEstimateRequest(BaseModel):
    num_clips: int = Field(default=1, ge=1, le=100)
    mode: str = Field(default="FINAL")
    apply_effects: bool = True
    num_stems: int = Field(default=1, ge=1, le=10)


@router.get("/render/tiers")
async def render_tiers():
    """List DRAFT/PREVIEW/FINAL render tiers with costs."""
    from app.services.lyrica.render_engine import list_render_tiers
    return {"success": True, "tiers": list_render_tiers()}


@router.post("/render/estimate")
async def render_estimate(request: RenderEstimateRequest):
    """Estimate session cost for GPU-intensive rendering."""
    from app.services.lyrica.render_engine import estimate_session_cost
    result = estimate_session_cost(request.num_clips, request.mode, request.apply_effects, request.num_stems)
    return {"success": True, **result}


# ---------------------------------------------------------------------------
# Micro-Royalty Ledger (VICS Protocol)
# ---------------------------------------------------------------------------

class RoyaltyRequest(BaseModel):
    track_id: str
    streams: int = Field(..., ge=0)
    territory: str = Field(default="US")
    splits: dict = Field(..., description="Contributor splits, e.g. {'beat_maker': 0.5, 'vocalist': 0.3, 'lyricist': 0.2}")


class FlipItRequest(BaseModel):
    parent_dna_tag: str
    parent_splits: dict
    child_splits: dict


@router.post("/royalty/calculate")
async def royalty_calculate(request: RoyaltyRequest):
    """Calculate micro-royalty distribution across contributors."""
    try:
        from app.services.lyrica.royalty_ledger import calculate_micro_royalty
        result = calculate_micro_royalty(request.track_id, request.streams, request.territory, request.splits)
        return {"success": True, **result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/royalty/flip-it-validate")
async def royalty_flip_it(request: FlipItRequest):
    """Validate Flip It protocol — ensure parent contributors get their cut."""
    from app.services.lyrica.royalty_ledger import validate_flip_it
    result = validate_flip_it(request.parent_dna_tag, request.child_splits, request.parent_splits)
    return {"success": True, **result}


# ---------------------------------------------------------------------------
# CCNA Cultural Matrix
# ---------------------------------------------------------------------------

@router.get("/ccna/corpora")
async def ccna_list():
    """List all cultural corpora, acoustic profiles, and phonetic overrides."""
    from app.services.lyrica.ccna_corpus import list_all
    return {"success": True, **list_all()}


@router.get("/ccna/corpus/{corpus_name}")
async def ccna_corpus(corpus_name: str):
    """Get a specific corpus with all its seeds."""
    try:
        from app.services.lyrica.ccna_corpus import get_corpus
        corpus = get_corpus(corpus_name)
        return {"success": True, "corpus_name": corpus_name, **corpus}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/ccna/profile/{profile_name}")
async def ccna_profile(profile_name: str):
    """Get a specific acoustic profile with texture chain and MMA config."""
    try:
        from app.services.lyrica.ccna_corpus import get_acoustic_profile
        profile = get_acoustic_profile(profile_name)
        return {"success": True, "profile_name": profile_name, **profile}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------

@router.get("/status")
async def lyrica_status():
    """Lyrica 3 Pro agent status and capabilities."""
    return {
        "success": True,
        "platform": "Lyrica 3 Pro: Aether-Nexus Orchestrator",
        "version": "3.0.0",
        "tier": "Execution Universe",
        "agents": {
            "ghostwriter": {"status": "active", "capabilities": ["lml_generation", "emotion_injection", "corpus_seeding"]},
            "mma": {"status": "active", "capabilities": ["late_pocket_swing", "humanized_drums", "groove_templates", "stem_output"]},
            "pfa": {"status": "active", "capabilities": ["vocal_fry", "adaptive_breath", "phrase_detection"]},
            "pda": {"status": "active", "capabilities": ["tape_saturation", "ssl_console", "vocal_bus", "lofi_vinyl"]},
            "dna_tagger": {"status": "active", "capabilities": ["sha256_provenance", "stem_tagging"]},
            "synapse_payload": {"status": "active", "capabilities": ["payload_assembly", "multi_agent_output"]},
            "s2_disruption": {"status": "active", "capabilities": ["groove_transplantation", "spectral_morph", "ghost_audio_ingest"]},
            "render_engine": {"status": "active", "capabilities": ["draft_preview_final", "cost_estimation"]},
            "royalty_ledger": {"status": "active", "capabilities": ["micro_royalty_calculation", "flip_it_protocol"]},
            "ccna": {"status": "active", "capabilities": ["5_cultural_corpora", "5_acoustic_profiles", "phonetic_overrides"]},
        },
        "os_hierarchy": {
            "control_plane": "SLA113",
            "pipeline": "Empire-1",
            "execution": "Lyrica 3",
        },
    }
