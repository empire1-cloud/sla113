from typing import Optional
from pydantic import BaseModel


class EngineMetadata(BaseModel):
    name: str
    service: str
    router: str
    credit_cost: int
    enabled_for: list[str]
    description: str
    status: str  # "active" | "placeholder" | "unavailable"
    canon_lock: bool = False  # True for Canon engines
    engine_type: Optional[str] = None  # "canon" | "universal" | "revenue"


# ========================================================
# REVENUE ENGINES (Hybrid Intelligence)
# ========================================================
ENGINES = {
    # Creative Engines (Southern Lyfestyle Foundry)
    "vision_smith": EngineMetadata(
        name="VisionSmith",
        service="app.services.vision_smith",
        router="app.routers.vision",
        credit_cost=10,
        enabled_for=["EMPIRE1", "SLA113", "Southern"],  # Full SaaS support
        description="Text-to-image generation for Southern Lyfestyle",
        status="placeholder",
        canon_lock=False,
        engine_type="revenue",
    ),
    "voice_king": EngineMetadata(
        name="VoiceKing",
        service="app.services.voice_king",
        router="app.routers.voice",
        credit_cost=5,
        enabled_for=["EMPIRE1", "SLA113", "Southern"],  # Full SaaS support
        description="Text-to-speech for Southern Lyfestyle",
        status="placeholder",
        canon_lock=False,
        engine_type="revenue",
    ),
    "sonic_forge": EngineMetadata(
        name="SonicForge",
        service="app.services.sonic_forge",
        router="app.routers.sonicforge",
        credit_cost=15,
        enabled_for=["EMPIRE1", "SLA113", "Southern"],  # Full SaaS support
        description="Music generation for Southern Lyfestyle",
        status="placeholder",
        canon_lock=False,
        engine_type="revenue",
    ),
    "vo_engine": EngineMetadata(
        name="VOEngine",
        service="app.services.vo_engine",
        router="app.routers.video",
        credit_cost=20,
        enabled_for=["EMPIRE1", "SLA113", "Southern"],  # Full SaaS support
        description="Video generation for Southern Lyfestyle",
        status="placeholder",
        canon_lock=False,
        engine_type="revenue",
    ),
    # Additional Creative Engines (Placeholders)
    "image_editor": EngineMetadata(
        name="ImageEditor",
        service="app.services.image_editor",
        router="app.routers.image_editor",
        credit_cost=8,
        enabled_for=["EMPIRE1", "SLA113", "Southern"],
        description="Advanced Southern image editing",
        status="unavailable",
        canon_lock=False,
        engine_type="revenue",
    ),
    "video_editor": EngineMetadata(
        name="VideoEditor",
        service="app.services.video_editor",
        router="app.routers.video_editor",
        credit_cost=25,
        enabled_for=["EMPIRE1", "SLA113", "Southern"],
        description="Southern video composition",
        status="unavailable",
        canon_lock=False,
        engine_type="revenue",
    ),
    "audio_mixer": EngineMetadata(
        name="AudioMixer",
        service="app.services.audio_mixer",
        router="app.routers.audio_mixer",
        credit_cost=12,
        enabled_for=["EMPIRE1", "SLA113", "Southern"],
        description="Southern audio mixing",
        status="unavailable",
        canon_lock=False,
        engine_type="revenue",
    ),
    "speech_to_text": EngineMetadata(
        name="SpeechToText",
        service="app.services.speech_to_text",
        router="app.routers.speech_to_text",
        credit_cost=3,
        enabled_for=["EMPIRE1", "SLA113", "Southern"],
        description="Southern transcription engine",
        status="unavailable",
        canon_lock=False,
        engine_type="revenue",
    ),
    "text_to_3d": EngineMetadata(
        name="TextTo3D",
        service="app.services.text_to_3d",
        router="app.routers.text_to_3d",
        credit_cost=30,
        enabled_for=["EMPIRE1", "SLA113", "Southern"],
        description="Southern 3D asset generation",
        status="unavailable",
        canon_lock=False,
        engine_type="revenue",
    ),
    "animation_engine": EngineMetadata(
        name="AnimationEngine",
        service="app.services.animation_engine",
        router="app.routers.animation_engine",
        credit_cost=35,
        enabled_for=["EMPIRE1", "SLA113", "Southern"],
        description="Southern animation generation",
        status="unavailable",
        canon_lock=False,
        engine_type="revenue",
    ),
}


# ========================================================
# SOUTHERN ENGINE PACK - CANON 5 (Identity Layer)
# ========================================================
CANON_ENGINES = {
    "canon_identity_v1": EngineMetadata(
        name="Playful Rooted Identity Engine",
        service="app.services.southern_engine_pack",
        router="app.routers.southern_engine_pack",
        credit_cost=5,
        enabled_for=["SLA113"],  # SLA113 manufacture only — output delivered to Southern
        description="Generates identity-locked text and metadata tied to Playful, SGV, and Southern Lyfestyle canon",
        status="active",
        canon_lock=True,
        engine_type="canon",
    ),
    "canon_emotion_v1": EngineMetadata(
        name="Southern Lyfestyle Emotional Engine",
        service="app.services.southern_engine_pack",
        router="app.routers.southern_engine_pack",
        credit_cost=4,
        enabled_for=["SLA113"],  # SLA113 manufacture only — output delivered to Southern
        description="Generates emotional overlays and vibe metadata rooted in Southern Lyfestyle canon",
        status="active",
        canon_lock=True,
        engine_type="canon",
    ),
    "canon_music_v1": EngineMetadata(
        name="Oldies / Old School / Rap Music Cue Engine",
        service="app.services.southern_engine_pack",
        router="app.routers.southern_engine_pack",
        credit_cost=5,
        enabled_for=["SLA113"],  # SLA113 manufacture only — output delivered to Southern
        description="Generates music cues, vibe tags, and lyric-style lines rooted in Southern Lyfestyle sound",
        status="active",
        canon_lock=True,
        engine_type="canon",
    ),
    "canon_symbol_v1": EngineMetadata(
        name="Rose + Water Tower Symbol Engine",
        service="app.services.southern_engine_pack",
        router="app.routers.southern_engine_pack",
        credit_cost=3,
        enabled_for=["SLA113"],  # SLA113 manufacture only — output delivered to Southern
        description="Generates Southern symbol combinations (rose, water tower, etc.)",
        status="active",
        canon_lock=True,
        engine_type="canon",
    ),
    "canon_sgv_v1": EngineMetadata(
        name="SGV Story Engine",
        service="app.services.southern_engine_pack",
        router="app.routers.southern_engine_pack",
        credit_cost=6,
        enabled_for=["SLA113"],  # SLA113 manufacture only — output delivered to Southern
        description="Generates San Gabriel Valley cultural stories and narratives",
        status="active",
        canon_lock=True,
        engine_type="canon",
    ),
    "aztec_chicano_engine": EngineMetadata(
        name="SLA113 Aztec-Chicano Engine",
        service="app.services.aztec_engine",
        router="app.routers.admin_universe",
        credit_cost=12,
        enabled_for=["SLA113"],
        description="High-fidelity generation of cultural narratives, Paño Arte, and Varrio Realism. Canon-locked.",
        status="active",
        canon_lock=True,
        engine_type="canon",
    ),
}


# ========================================================
# SOUTHERN ENGINE PACK - UNIVERSAL 15 (Production Layer)
# ========================================================
UNIVERSAL_ENGINES = {
    "univ_mission_v1": EngineMetadata(
        name="Universal Mission Engine",
        service="app.services.southern_engine_pack",
        router="app.routers.southern_engine_pack",
        credit_cost=4,
        enabled_for=["SLA113"],  # SLA113 manufacture only — output delivered to Southern
        description="Generates missions/quests for any theme",
        status="active",
        canon_lock=False,
        engine_type="universal",
    ),
    "univ_story_arc_v1": EngineMetadata(
        name="Universal Story Arc Engine",
        service="app.services.southern_engine_pack",
        router="app.routers.southern_engine_pack",
        credit_cost=5,
        enabled_for=["SLA113"],  # SLA113 manufacture only — output delivered to Southern
        description="Builds multi-stage story arcs for any theme",
        status="active",
        canon_lock=False,
        engine_type="universal",
    ),
    "univ_character_v1": EngineMetadata(
        name="Universal Character Engine",
        service="app.services.southern_engine_pack",
        router="app.routers.southern_engine_pack",
        credit_cost=5,
        enabled_for=["SLA113"],  # SLA113 manufacture only — output delivered to Southern
        description="Generates characters and sprite sheet metadata",
        status="active",
        canon_lock=False,
        engine_type="universal",
    ),
    "univ_outfit_v1": EngineMetadata(
        name="Universal Outfit Engine",
        service="app.services.southern_engine_pack",
        router="app.routers.southern_engine_pack",
        credit_cost=3,
        enabled_for=["SLA113"],  # SLA113 manufacture only — output delivered to Southern
        description="Generates outfits, accessories, and sprite layer metadata",
        status="active",
        canon_lock=False,
        engine_type="universal",
    ),
    "univ_world_v1": EngineMetadata(
        name="Universal World Engine",
        service="app.services.southern_engine_pack",
        router="app.routers.southern_engine_pack",
        credit_cost=6,
        enabled_for=["SLA113"],  # SLA113 manufacture only — output delivered to Southern
        description="Generates environments, locations, and world rules",
        status="active",
        canon_lock=False,
        engine_type="universal",
    ),
    "univ_visual_style_v1": EngineMetadata(
        name="Universal Visual Style Engine",
        service="app.services.southern_engine_pack",
        router="app.routers.southern_engine_pack",
        credit_cost=4,
        enabled_for=["SLA113"],  # SLA113 manufacture only — output delivered to Southern
        description="Generates backgrounds and visual style metadata",
        status="active",
        canon_lock=False,
        engine_type="universal",
    ),
    "univ_dialogue_v1": EngineMetadata(
        name="Universal Dialogue Engine",
        service="app.services.southern_engine_pack",
        router="app.routers.southern_engine_pack",
        credit_cost=4,
        enabled_for=["SLA113"],  # SLA113 manufacture only — output delivered to Southern
        description="Generates dialogue lines and speech patterns",
        status="active",
        canon_lock=False,
        engine_type="universal",
    ),
    "univ_lore_v1": EngineMetadata(
        name="Universal Lore Engine",
        service="app.services.southern_engine_pack",
        router="app.routers.southern_engine_pack",
        credit_cost=5,
        enabled_for=["SLA113"],  # SLA113 manufacture only — output delivered to Southern
        description="Generates lore, history, and mythologies",
        status="active",
        canon_lock=False,
        engine_type="universal",
    ),
    "univ_event_v1": EngineMetadata(
        name="Universal Event Engine",
        service="app.services.southern_engine_pack",
        router="app.routers.southern_engine_pack",
        credit_cost=4,
        enabled_for=["SLA113"],  # SLA113 manufacture only — output delivered to Southern
        description="Generates events, encounters, and dynamic moments",
        status="active",
        canon_lock=False,
        engine_type="universal",
    ),
    "univ_challenge_v1": EngineMetadata(
        name="Universal Challenge Engine",
        service="app.services.southern_engine_pack",
        router="app.routers.southern_engine_pack",
        credit_cost=4,
        enabled_for=["SLA113"],  # SLA113 manufacture only — output delivered to Southern
        description="Generates obstacles, puzzles, and difficulty curves",
        status="active",
        canon_lock=False,
        engine_type="universal",
    ),
    "univ_progression_v1": EngineMetadata(
        name="Universal Progression Engine",
        service="app.services.southern_engine_pack",
        router="app.routers.southern_engine_pack",
        credit_cost=3,
        enabled_for=["SLA113"],  # SLA113 manufacture only — output delivered to Southern
        description="Handles leveling, XP, and unlocks",
        status="active",
        canon_lock=False,
        engine_type="universal",
    ),
    "univ_reward_v1": EngineMetadata(
        name="Universal Reward Engine",
        service="app.services.southern_engine_pack",
        router="app.routers.southern_engine_pack",
        credit_cost=3,
        enabled_for=["SLA113"],  # SLA113 manufacture only — output delivered to Southern
        description="Generates rewards, items, and incentives",
        status="active",
        canon_lock=False,
        engine_type="universal",
    ),
    "univ_title_screen_v1": EngineMetadata(
        name="Universal Title Screen Engine",
        service="app.services.southern_engine_pack",
        router="app.routers.southern_engine_pack",
        credit_cost=4,
        enabled_for=["SLA113"],  # SLA113 manufacture only — output delivered to Southern
        description="Generates title screens and intro framing",
        status="active",
        canon_lock=False,
        engine_type="universal",
    ),
    "univ_theme_filter_v1": EngineMetadata(
        name="Universal Theme Filter Engine",
        service="app.services.southern_engine_pack",
        router="app.routers.southern_engine_pack",
        credit_cost=3,
        enabled_for=["SLA113"],  # SLA113 manufacture only — output delivered to Southern
        description="Applies theme transformations (anime, horror, wizard, etc.) to other engine outputs",
        status="active",
        canon_lock=False,
        engine_type="universal",
    ),
    "univ_emotion_filter_v1": EngineMetadata(
        name="Universal Emotion Filter Engine",
        service="app.services.southern_engine_pack",
        router="app.routers.southern_engine_pack",
        credit_cost=3,
        enabled_for=["SLA113"],  # SLA113 manufacture only — output delivered to Southern
        description="Applies emotional overlays to any content",
        status="active",
        canon_lock=False,
        engine_type="universal",
    ),
}


# ========================================================
# ARCADE ENGINE PACK (SLA113 Arcade Engines)
# Derived from SLA113_BUILD_SPEC.yaml machine_profiles section.
# ========================================================
ARCADE_ENGINES = {
    "fishing_engine_v2": EngineMetadata(
        name="Fishing Engine V2",
        service="app.engines.arcade.fishing_engine_v2",
        router="app.routers.arcade",
        credit_cost=2,
        enabled_for=["tenant_casino_vegas", "tenant_arcade_london", "tenant_gaming_sydney",
                     "Southern", "southern_lyfestyle_arcade"],  # Gaming tenants only
        description="Arcade fish shooting game — 30% skill, 70% chance. RTP 0.94. "
                    "Catch tiers: common/uncommon/rare/epic.",
        status="active",
        canon_lock=False,
        engine_type="arcade",
    ),
    "slots_engine_v1": EngineMetadata(
        name="Slots Engine V1",
        service="app.engines.arcade.slots_engine_v1",
        router="app.routers.arcade",
        credit_cost=2,
        enabled_for=["tenant_casino_vegas", "tenant_arcade_london", "tenant_gaming_sydney",
                     "Southern", "horror_arcade", "anime_arcade"],  # Gaming tenants only
        description="Classic 5-reel 20-payline slots. RTP 0.95. Themes: gold_rush, "
                    "ancient_egypt, space_odyssey, wild_west. Progressive jackpot enabled.",
        status="active",
        canon_lock=False,
        engine_type="arcade",
    ),
    "keno_engine_v1": EngineMetadata(
        name="Keno Engine V1",
        service="app.engines.arcade.keno_engine_v1",
        router="app.routers.arcade",
        credit_cost=1,
        enabled_for=["tenant_casino_vegas", "Southern"],  # Gaming tenants only
        description="Fast-paced keno — pick up to 20 numbers from 1–80. RTP 0.93. "
                    "Draw every 60 seconds. Payout: match-5=1x, match-10=5x, match-15=20x, match-20=500x.",
        status="active",
        canon_lock=False,
        engine_type="arcade",
    ),
    "payout_engine": EngineMetadata(
        name="Payout Engine",
        service="app.engines.arcade.payout_engine",
        router="app.routers.arcade",
        credit_cost=0,
        enabled_for=["tenant_casino_vegas", "tenant_arcade_london", "tenant_gaming_sydney",
                     "southern_lyfestyle_arcade", "Southern", "horror_arcade", "anime_arcade", "SLA113"],  # Southern arcade variants,
        description="Settlement layer for all arcade game results. Enforces win ceiling (100x), "
                    "loss limits (50% of buy-in). Wired to SLA113SettlementEngine.",
        status="active",
        canon_lock=False,
        engine_type="arcade",
    ),
    "machine_engine": EngineMetadata(
        name="Machine Engine",
        service="app.engines.arcade.machine_engine",
        router="app.routers.arcade",
        credit_cost=0,
        enabled_for=["tenant_casino_vegas", "tenant_arcade_london", "tenant_gaming_sydney",
                     "southern_lyfestyle_arcade", "Southern", "horror_arcade", "anime_arcade", "SLA113"],  # Southern arcade variants,
        description="Machine catalog router — resolves tenant → machine_type → engine instance. "
                    "Enforces per-tenant machine catalog from Build Spec.",
        status="active",
        canon_lock=False,
        engine_type="arcade",
    ),
    "tenant_engine": EngineMetadata(
        name="Tenant Engine",
        service="app.engines.arcade.tenant_engine",
        router="app.routers.arcade",
        credit_cost=0,
        enabled_for=["EMPIRE1", "SLA113"],
        description="Tenant context resolver — maps tenant_id to governance profile, "
                    "regulatory profile, revenue routing, and Stripe entitlement check.",
        status="active",
        canon_lock=False,
        engine_type="arcade",
    ),
    "canon_layer_sgv_aztec": EngineMetadata(
        name="Canon Layer: SGV + Aztec",
        service="app.engines.arcade.canon_layer_sgv_aztec",
        router="app.routers.arcade",
        credit_cost=1,
        enabled_for=["Southern", "SLA113"],  # Southern identity layer | SLA113 manufacture
        description="Post-processing canon overlay combining San Gabriel Valley identity "
                    "with Aztec thematic symbols and narrative. Canon-locked. Does not modify game math.",
        status="active",
        canon_lock=True,
        engine_type="canon",
    ),
}


# ========================================================
# SLA113 CORE ENGINES (2) — Root canon + RNG layer
# These are the sovereign foundation engines.
# All generation and math in the platform inherits from these.
# ========================================================
SLA113_CORE_ENGINES = {
    "playful_art_bible": EngineMetadata(
        name="PlayfulArtBible",
        service="SLA113.core.southern.playful_art_bible",
        router="app.routers.southern_engine_pack",
        credit_cost=0,
        enabled_for=["SLA113"],  # Canon-locked — SLA113 internal only, injected into Southern builds
        description=(
            "Root Emotional Canon for Southern Lyfestyle. "
            "Defines emotional core (soft_pain, heartbreak, blooming, loyalty), "
            "visual motifs (chrome, roses, neon_bloom), geographic canon (SGV, El Monte, IELA), "
            "mythic layer (Aztec geometry, Chicano lineage), and tone/voice. "
            "Injected as a canon prefix into all generation engines when Southern mode is active. "
            "Canon-locked. No override permitted."
        ),
        status="active",
        canon_lock=True,
        engine_type="canon",
    ),
    "entropy_engine": EngineMetadata(
        name="EntropyEngine",
        service="SLA113.core.entropy_engine",
        router="app.routers.arcade",
        credit_cost=0,
        enabled_for=["SLA113"],  # Root kernel — /dev/shm only, governance-locked
        description=(
            "Universal RNG Seed Rotator for REV_7 Math. "
            "Generates a high-entropy 256-bit SHA-256 seed from os.urandom(64) every 60 seconds. "
            "Seed is written to /dev/shm/sla113_kernel/live_seed.bin (chmod 400). "
            "All arcade engines (fishing, slots, keno) and the payout engine derive randomness from this seed. "
            "Runs as a root-level background daemon. Governance-locked — cannot be paused during a live session."
        ),
        status="active",
        canon_lock=True,
        engine_type="canon",
    ),
}


# ========================================================
# COMBINED REGISTRY — 39 ENGINES TOTAL
# Revenue×10 | Canon×5 | Universal×15 | Arcade×7 | Core×2
# ========================================================
ALL_ENGINES = {**ENGINES, **CANON_ENGINES, **UNIVERSAL_ENGINES, **ARCADE_ENGINES, **SLA113_CORE_ENGINES}


# ========================================================
# HELPER FUNCTIONS
# ========================================================
def get_engine(engine_id: str) -> Optional[EngineMetadata]:
    """Get engine metadata by ID."""
    return ALL_ENGINES.get(engine_id)


def list_engines(tenant: Optional[str] = None, engine_type: Optional[str] = None) -> list[EngineMetadata]:
    """List engines, optionally filtered by tenant and/or type."""
    engines = ALL_ENGINES
    
    if tenant:
        engines = {k: v for k, v in engines.items() if tenant in v.enabled_for}
    
    if engine_type:
        engines = {k: v for k, v in engines.items() if v.engine_type == engine_type}
    
    return list(engines.values())


def get_canon_engines() -> list[EngineMetadata]:
    """Get all Canon 5 engines."""
    return list(CANON_ENGINES.values())


def get_universal_engines() -> list[EngineMetadata]:
    """Get all Universal 15 engines."""
    return list(UNIVERSAL_ENGINES.values())


def is_engine_available(engine_id: str, tenant: str) -> bool:
    """Check if engine is available for a specific tenant."""
    engine = ALL_ENGINES.get(engine_id)
    if not engine:
        return False
    if tenant not in engine.enabled_for:
        return False
    if engine.status == "unavailable":
        return False
    return True


def get_engine_credit_cost(engine_id: str) -> int:
    """Get credit cost for an engine."""
    engine = ALL_ENGINES.get(engine_id)
    return engine.credit_cost if engine else 0


def get_active_engines(tenant: Optional[str] = None) -> list[EngineMetadata]:
    """Get all active engines."""
    return [e for e in list_engines(tenant) if e.status == "active"]


def get_canv_lock_engines() -> list[EngineMetadata]:
    """Get all canon_locked engines."""
    return [e for e in ALL_ENGINES.values() if e.canon_lock]


# ========================================================
# EMPIRE ONE — 19 FORMAL PIPELINES
# These are the sovereign production pipelines of Empire One.
# Grouped into: Creative/Media (9), Arcade (6), OS Factory (4)
# ========================================================
EMPIRE_PIPELINES = {

    # ── CREATIVE / MEDIA PIPELINES (9) ─────────────────────────────────────

    "image_generation_pipeline": {
        "id":          "image_generation_pipeline",
        "name":        "Image Generation Pipeline",
        "group":       "creative",
        "description": "Text prompt → VisionSmith image generation → upscale refinement",
        "credit_cost": 18,
        "steps": [
            {"engine": "vision_smith",  "action": "generate",  "description": "Text-to-image via VisionSmith"},
            {"engine": "vision_smith",  "action": "upscale",   "description": "SDXL refiner upscale pass"},
        ],
        "output_type": "image",
        "enabled_for": ["SLA113", "Southern"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    "voice_synthesis_pipeline": {
        "id":          "voice_synthesis_pipeline",
        "name":        "Voice Synthesis Pipeline",
        "group":       "creative",
        "description": "Text → VoiceKing TTS with accent model and optional stem export",
        "credit_cost": 8,
        "steps": [
            {"engine": "voice_king",    "action": "synthesize",    "description": "Text-to-speech generation"},
            {"engine": "voice_king",    "action": "post_process",  "description": "EQ, normalization, stem export"},
        ],
        "output_type": "audio",
        "enabled_for": ["SLA113", "Southern"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    "music_generation_pipeline": {
        "id":          "music_generation_pipeline",
        "name":        "Music Generation Pipeline",
        "group":       "creative",
        "description": "Prompt → SonicForge MusicGen → stem separation → export",
        "credit_cost": 22,
        "steps": [
            {"engine": "sonic_forge",   "action": "generate",      "description": "MusicGen audio generation"},
            {"engine": "sonic_forge",   "action": "separate_stems","description": "Demucs stem separation"},
            {"engine": "audio_mixer",   "action": "master",        "description": "Final mastering pass"},
        ],
        "output_type": "audio",
        "enabled_for": ["SLA113", "Southern"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    "video_production_pipeline": {
        "id":          "video_production_pipeline",
        "name":        "Video Production Pipeline",
        "group":       "creative",
        "description": "Assets + prompt → VOEngine video assembly with voice-over",
        "credit_cost": 40,
        "steps": [
            {"engine": "vision_smith",  "action": "generate",      "description": "Scene image generation"},
            {"engine": "sonic_forge",   "action": "generate",      "description": "Background score generation"},
            {"engine": "voice_king",    "action": "synthesize",    "description": "Voice-over narration"},
            {"engine": "vo_engine",     "action": "assemble",      "description": "Video assembly and render"},
        ],
        "output_type": "video",
        "enabled_for": ["SLA113", "Southern"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    "content_edit_pipeline": {
        "id":          "content_edit_pipeline",
        "name":        "Content Edit Pipeline",
        "group":       "creative",
        "description": "Existing asset → ImageEditor inpainting → AudioMixer grade",
        "credit_cost": 20,
        "steps": [
            {"engine": "image_editor",  "action": "inpaint",       "description": "Inpainting and outpainting"},
            {"engine": "audio_mixer",   "action": "mix",           "description": "Audio mix and EQ"},
        ],
        "output_type": "mixed",
        "enabled_for": ["SLA113", "Southern"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    "speech_transcription_pipeline": {
        "id":          "speech_transcription_pipeline",
        "name":        "Speech Transcription Pipeline",
        "group":       "creative",
        "description": "Audio → SpeechToText → structured transcript → export",
        "credit_cost": 6,
        "steps": [
            {"engine": "speech_to_text","action": "transcribe",    "description": "Whisper transcription"},
            {"engine": "speech_to_text","action": "diarize",       "description": "Speaker diarization"},
            {"engine": "speech_to_text","action": "export",        "description": "SRT/VTT/JSON export"},
        ],
        "output_type": "text",
        "enabled_for": ["SLA113", "Southern"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    "3d_asset_pipeline": {
        "id":          "3d_asset_pipeline",
        "name":        "3D Asset Pipeline",
        "group":       "creative",
        "description": "Text/image → TextTo3D mesh → rig → animation preview",
        "credit_cost": 65,
        "steps": [
            {"engine": "text_to_3d",         "action": "generate",  "description": "Text-to-3D mesh generation"},
            {"engine": "animation_engine",   "action": "rig",       "description": "Auto-rig mesh"},
            {"engine": "animation_engine",   "action": "preview",   "description": "Generate animation preview"},
        ],
        "output_type": "3d",
        "enabled_for": ["SLA113", "Southern"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    "creative_media_pipeline": {
        "id":          "creative_media_pipeline",
        "name":        "Creative Media Pipeline",
        "group":       "creative",
        "description": "Full creative bundle: image + music + voice → packaged media asset",
        "credit_cost": 38,
        "steps": [
            {"engine": "vision_smith",  "action": "generate",      "description": "Visual generation"},
            {"engine": "sonic_forge",   "action": "generate",      "description": "Music generation"},
            {"engine": "voice_king",    "action": "synthesize",    "description": "Voice synthesis"},
            {"engine": "vo_engine",     "action": "package",       "description": "Package into deliverable"},
        ],
        "output_type": "media_pack",
        "enabled_for": ["SLA113", "Southern"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    "full_production_pipeline": {
        "id":          "full_production_pipeline",
        "name":        "Full Production Pipeline",
        "group":       "creative",
        "description": "Premium end-to-end: image → edit → 3D → animate → music → VO → video render",
        "credit_cost": 120,
        "steps": [
            {"engine": "vision_smith",       "action": "generate",       "description": "Base image"},
            {"engine": "image_editor",       "action": "inpaint",        "description": "Scene refinement"},
            {"engine": "text_to_3d",         "action": "generate",       "description": "3D asset"},
            {"engine": "animation_engine",   "action": "animate",        "description": "Animation sequence"},
            {"engine": "sonic_forge",        "action": "generate",       "description": "Score generation"},
            {"engine": "voice_king",         "action": "synthesize",     "description": "VO narration"},
            {"engine": "audio_mixer",        "action": "master",         "description": "Final mix"},
            {"engine": "vo_engine",          "action": "render",         "description": "Full render output"},
        ],
        "output_type": "video",
        "enabled_for": ["SLA113", "Southern"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    # ── ARCADE PIPELINES (6) ────────────────────────────────────────────────

    "fish_game_pipeline": {
        "id":          "fish_game_pipeline",
        "name":        "Fish Game Pipeline",
        "group":       "arcade",
        "description": "Tenant context → fish shooting session → payout settlement",
        "credit_cost": 2,
        "steps": [
            {"engine": "tenant_engine",       "action": "resolve",   "description": "Resolve tenant + governance"},
            {"engine": "fishing_engine_v2",   "action": "play",      "description": "Fish shooting game session"},
            {"engine": "payout_engine",       "action": "settle",    "description": "Payout settlement (RTP 0.94)"},
        ],
        "output_type": "game_result",
        "enabled_for": ["Southern", "SLA113"],  # Southern arcade | SLA113 math
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    "slots_game_pipeline": {
        "id":          "slots_game_pipeline",
        "name":        "Slots Game Pipeline",
        "group":       "arcade",
        "description": "Tenant context → 5-reel slot session → progressive jackpot check → payout",
        "credit_cost": 2,
        "steps": [
            {"engine": "tenant_engine",   "action": "resolve",   "description": "Resolve tenant + governance"},
            {"engine": "slots_engine_v1", "action": "spin",      "description": "5-reel 20-payline spin"},
            {"engine": "slots_engine_v1", "action": "jackpot",   "description": "Progressive jackpot evaluation"},
            {"engine": "payout_engine",   "action": "settle",    "description": "Payout settlement (RTP 0.95)"},
        ],
        "output_type": "game_result",
        "enabled_for": ["EMPIRE1", "SLA113"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    "keno_game_pipeline": {
        "id":          "keno_game_pipeline",
        "name":        "Keno Game Pipeline",
        "group":       "arcade",
        "description": "Tenant context → keno draw → multiplier evaluation → payout",
        "credit_cost": 1,
        "steps": [
            {"engine": "tenant_engine",   "action": "resolve",   "description": "Resolve tenant + governance"},
            {"engine": "keno_engine_v1",  "action": "draw",      "description": "Keno number draw (80-ball)"},
            {"engine": "keno_engine_v1",  "action": "evaluate",  "description": "Match evaluation + multiplier"},
            {"engine": "payout_engine",   "action": "settle",    "description": "Payout settlement (RTP 0.93)"},
        ],
        "output_type": "game_result",
        "enabled_for": ["EMPIRE1", "SLA113"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    "arcade_tenant_onboard_pipeline": {
        "id":          "arcade_tenant_onboard_pipeline",
        "name":        "Arcade Tenant Onboard Pipeline",
        "group":       "arcade",
        "description": "New tenant → governance profile → machine catalog → canon overlay → stage deploy",
        "credit_cost": 0,
        "steps": [
            {"engine": "tenant_engine",   "action": "create",    "description": "Create tenant profile + Stripe entitlement"},
            {"engine": "machine_engine",  "action": "catalog",   "description": "Assign machine catalog from Build Spec"},
            {"engine": "canon_layer_sgv_aztec", "action": "apply","description": "Apply canon overlay (SGV/Aztec) if applicable"},
        ],
        "output_type": "tenant_config",
        "enabled_for": ["EMPIRE1", "SLA113"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    "sgv_arcade_pipeline": {
        "id":          "sgv_arcade_pipeline",
        "name":        "SGV Arcade Pipeline",
        "group":       "arcade",
        "description": "Canon-locked SGV+Aztec overlay applied to fish shooting session",
        "credit_cost": 3,
        "steps": [
            {"engine": "tenant_engine",         "action": "resolve",   "description": "Resolve tenant"},
            {"engine": "canon_layer_sgv_aztec", "action": "activate",  "description": "Activate SGV/Aztec canon layer"},
            {"engine": "fishing_engine_v2",     "action": "play",      "description": "Canon-skinned fish session"},
            {"engine": "payout_engine",         "action": "settle",    "description": "Payout settlement"},
        ],
        "output_type": "game_result",
        "enabled_for": ["Southern", "SLA113"],  # Southern arcade | SLA113 math
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
        "canon_lock":  True,
    },

    "arcade_session_pipeline": {
        "id":          "arcade_session_pipeline",
        "name":        "Arcade Session Pipeline",
        "group":       "arcade",
        "description": "Full session manager: tenant resolve → machine route → game dispatch → settle → log",
        "credit_cost": 2,
        "steps": [
            {"engine": "tenant_engine",   "action": "resolve",   "description": "Tenant + governance"},
            {"engine": "machine_engine",  "action": "route",     "description": "Route to correct game engine"},
            {"engine": "payout_engine",   "action": "settle",    "description": "Settlement + win ceiling enforcement"},
        ],
        "output_type": "game_result",
        "enabled_for": ["EMPIRE1", "SLA113"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    # ── OS FACTORY PIPELINES (4) ────────────────────────────────────────────

    "game_os_build_pipeline": {
        "id":          "game_os_build_pipeline",
        "name":        "Game OS Build Pipeline",
        "group":       "os_factory",
        "description": "Manufacture a full Game OS: character + world + story arc + visual style + music + title screen",
        "credit_cost": 32,
        "steps": [
            {"engine": "univ_character_v1",    "action": "generate",  "description": "Character roster generation"},
            {"engine": "univ_world_v1",        "action": "generate",  "description": "World + environment generation"},
            {"engine": "univ_story_arc_v1",    "action": "generate",  "description": "Multi-stage story arc"},
            {"engine": "univ_visual_style_v1", "action": "generate",  "description": "Background + visual style"},
            {"engine": "sonic_forge",          "action": "generate",  "description": "OS soundtrack generation"},
            {"engine": "univ_title_screen_v1", "action": "generate",  "description": "Title screen framing"},
        ],
        "output_type": "game_os",
        "enabled_for": ["SLA113"],  # SLA113 manufacture — builds FOR Southern, delivered via signed receipt
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    "canon_identity_pipeline": {
        "id":          "canon_identity_pipeline",
        "name":        "Canon Identity Pipeline",
        "group":       "os_factory",
        "description": "Run all 5 Canon engines to produce a fully identity-locked content layer",
        "credit_cost": 23,
        "steps": [
            {"engine": "canon_identity_v1", "action": "generate",  "description": "Rooted identity + metadata"},
            {"engine": "canon_emotion_v1",  "action": "generate",  "description": "Emotional overlay + vibe tags"},
            {"engine": "canon_music_v1",    "action": "generate",  "description": "Music cue + lyric-style lines"},
            {"engine": "canon_symbol_v1",   "action": "generate",  "description": "Symbol combinations (rose, water tower)"},
            {"engine": "canon_sgv_v1",      "action": "generate",  "description": "SGV cultural story + narrative"},
        ],
        "output_type": "identity_pack",
        "enabled_for": ["SLA113"],  # SLA113 manufacture — identity layer
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
        "canon_lock":  True,
    },

    "tenant_content_pack_pipeline": {
        "id":          "tenant_content_pack_pipeline",
        "name":        "Tenant Content Pack Pipeline",
        "group":       "os_factory",
        "description": "Full Universal 15 run: missions + characters + outfits + lore + events + rewards + progression",
        "credit_cost": 50,
        "steps": [
            {"engine": "univ_mission_v1",      "action": "generate",  "description": "Mission + quest set"},
            {"engine": "univ_character_v1",    "action": "generate",  "description": "Character profiles"},
            {"engine": "univ_outfit_v1",       "action": "generate",  "description": "Outfit + accessory layers"},
            {"engine": "univ_world_v1",        "action": "generate",  "description": "World + locations"},
            {"engine": "univ_lore_v1",         "action": "generate",  "description": "Lore + mythology"},
            {"engine": "univ_event_v1",        "action": "generate",  "description": "Events + encounters"},
            {"engine": "univ_challenge_v1",    "action": "generate",  "description": "Challenges + difficulty curves"},
            {"engine": "univ_progression_v1",  "action": "generate",  "description": "XP + leveling + unlocks"},
            {"engine": "univ_reward_v1",       "action": "generate",  "description": "Rewards + item catalog"},
            {"engine": "univ_dialogue_v1",     "action": "generate",  "description": "Dialogue + speech patterns"},
            {"engine": "univ_theme_filter_v1", "action": "apply",     "description": "Theme transformation pass"},
            {"engine": "univ_emotion_filter_v1","action": "apply",    "description": "Emotion overlay pass"},
        ],
        "output_type": "content_pack",
        "enabled_for": ["SLA113"],  # SLA113 internal manufacture
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    "deployment_pipeline": {
        "id":          "deployment_pipeline",
        "name":        "Deployment Pipeline",
        "group":       "os_factory",
        "description": "Build spec → tenant engine → stage deploy → production verification",
        "credit_cost": 0,
        "steps": [
            {"engine": "tenant_engine",  "action": "validate",  "description": "Validate build spec + Stripe entitlement"},
            {"engine": "tenant_engine",  "action": "provision", "description": "Provision tenant workspace"},
            {"engine": "machine_engine", "action": "install",   "description": "Install machine catalog"},
            {"engine": "tenant_engine",  "action": "verify",    "description": "Health check + boundary verification"},
        ],
        "output_type": "deployment",
        "enabled_for": ["SLA113"],  # SLA113 internal manufacture
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },
}


# ========================================================
# PIPELINE HELPERS
# ========================================================
def get_pipeline(pipeline_id: str) -> Optional[dict]:
    return EMPIRE_PIPELINES.get(pipeline_id)


def list_pipelines(group: Optional[str] = None, tenant: Optional[str] = None) -> list[dict]:
    pipes = EMPIRE_PIPELINES.values()
    if group:
        pipes = (p for p in pipes if p.get("group") == group)
    if tenant:
        pipes = (p for p in pipes if tenant in p.get("enabled_for", []))
    return list(pipes)


def calculate_pipeline_cost(pipeline_id: str) -> int:
    pipeline = EMPIRE_PIPELINES.get(pipeline_id)
    if not pipeline:
        return 0
    return pipeline.get("credit_cost", 0)


def get_pipeline_engine_ids(pipeline_id: str) -> list[str]:
    pipeline = EMPIRE_PIPELINES.get(pipeline_id)
    if not pipeline:
        return []
    return [step["engine"] for step in pipeline.get("steps", [])]


# ========================================================
# SOUTHERN PIPELINES (20) — Consumer Arcade + Game OS
# Executed BY SLA113, delivered TO Southern Lyfestyle.
# Southern never calls these directly — SLA113 orchestrates.
# ========================================================
SOUTHERN_PIPELINES = {

    # ── ARCADE SESSION PIPELINES (4) ──────────────────────────────────────────

    "arcade_session_pipeline": {
        "id":          "arcade_session_pipeline",
        "name":        "Arcade Session Pipeline",
        "group":       "arcade_session",
        "description": "Canon inject → machine resolve → session open → entropy seed lock",
        "credit_cost": 2,
        "steps": [
            {"engine": "playful_art_bible",   "action": "inject",   "description": "Inject Southern canon prefix"},
            {"engine": "machine_engine",       "action": "resolve",  "description": "Resolve tenant → machine instance"},
            {"engine": "entropy_engine",       "action": "seed",     "description": "Lock live entropy seed for session"},
        ],
        "output_type": "session_token",
        "enabled_for": ["Southern", "SLA113"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    "slots_play_pipeline": {
        "id":          "slots_play_pipeline",
        "name":        "Slots Play Pipeline",
        "group":       "arcade_session",
        "description": "Entropy seed → slots spin → payout settlement",
        "credit_cost": 2,
        "steps": [
            {"engine": "entropy_engine",  "action": "seed",    "description": "Derive spin seed from live pool"},
            {"engine": "slots_engine_v1", "action": "spin",    "description": "5-reel spin with REV_7 RTP"},
            {"engine": "payout_engine",   "action": "settle",  "description": "Settle win/loss against ledger"},
        ],
        "output_type": "spin_result",
        "enabled_for": ["Southern", "SLA113"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    "fishing_play_pipeline": {
        "id":          "fishing_play_pipeline",
        "name":        "Fishing Play Pipeline",
        "group":       "arcade_session",
        "description": "Entropy seed → fishing round → catch tier → payout",
        "credit_cost": 2,
        "steps": [
            {"engine": "entropy_engine",      "action": "seed",   "description": "Derive round seed from live pool"},
            {"engine": "fishing_engine_v2",   "action": "cast",   "description": "Fish catch round with tier logic"},
            {"engine": "payout_engine",       "action": "settle", "description": "Settle catch payout"},
        ],
        "output_type": "round_result",
        "enabled_for": ["Southern", "SLA113"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    "keno_play_pipeline": {
        "id":          "keno_play_pipeline",
        "name":        "Keno Play Pipeline",
        "group":       "arcade_session",
        "description": "Entropy seed → keno draw → match score → payout",
        "credit_cost": 1,
        "steps": [
            {"engine": "entropy_engine",  "action": "seed",    "description": "Derive draw seed from live pool"},
            {"engine": "keno_engine_v1",  "action": "draw",    "description": "60s keno draw with REV_7 RTP"},
            {"engine": "payout_engine",   "action": "settle",  "description": "Match-based payout settlement"},
        ],
        "output_type": "draw_result",
        "enabled_for": ["Southern", "SLA113"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    # ── GAME OS MANUFACTURE PIPELINES (6) ────────────────────────────────────

    "full_game_os_pipeline": {
        "id":          "full_game_os_pipeline",
        "name":        "Full Game OS Pipeline",
        "group":       "game_os",
        "description": "Canon inject → world + character + narrative + audio → REV_7 sign → Southern deploy",
        "credit_cost": 60,
        "steps": [
            {"engine": "playful_art_bible",    "action": "inject",    "description": "Root canon injection"},
            {"engine": "univ_world_v1",        "action": "generate",  "description": "World environment generation"},
            {"engine": "univ_character_v1",    "action": "generate",  "description": "Character roster generation"},
            {"engine": "univ_narrative_v1",    "action": "generate",  "description": "Story arc + narrative"},
            {"engine": "univ_challenge_v1",    "action": "generate",  "description": "Challenge + difficulty curves"},
            {"engine": "univ_progression_v1",  "action": "generate",  "description": "XP + leveling + unlocks"},
            {"engine": "univ_reward_v1",       "action": "generate",  "description": "Reward catalog"},
            {"engine": "univ_dialogue_v1",     "action": "generate",  "description": "Dialogue + speech"},
            {"engine": "univ_theme_filter_v1", "action": "apply",     "description": "Theme transformation pass"},
            {"engine": "univ_emotion_filter_v1","action": "apply",    "description": "Emotion overlay pass"},
        ],
        "output_type": "game_os_bundle",
        "enabled_for": ["SLA113"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    "world_build_pipeline": {
        "id":          "world_build_pipeline",
        "name":        "World Build Pipeline",
        "group":       "game_os",
        "description": "Canon prefix → world engine → visual style → lore",
        "credit_cost": 18,
        "steps": [
            {"engine": "playful_art_bible",    "action": "inject",   "description": "Canon prefix injection"},
            {"engine": "univ_world_v1",        "action": "generate", "description": "World + environment rules"},
            {"engine": "univ_visual_style_v1", "action": "generate", "description": "Visual style metadata"},
            {"engine": "univ_lore_v1",         "action": "generate", "description": "World lore + mythology"},
        ],
        "output_type": "world_pack",
        "enabled_for": ["SLA113"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    "character_build_pipeline": {
        "id":          "character_build_pipeline",
        "name":        "Character Build Pipeline",
        "group":       "game_os",
        "description": "Canon prefix → character → outfit → dialogue",
        "credit_cost": 14,
        "steps": [
            {"engine": "playful_art_bible",  "action": "inject",   "description": "Canon prefix injection"},
            {"engine": "univ_character_v1",  "action": "generate", "description": "Character + sprite metadata"},
            {"engine": "univ_outfit_v1",     "action": "generate", "description": "Outfit + accessory layers"},
            {"engine": "univ_dialogue_v1",   "action": "generate", "description": "Character dialogue lines"},
        ],
        "output_type": "character_pack",
        "enabled_for": ["SLA113"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    "narrative_build_pipeline": {
        "id":          "narrative_build_pipeline",
        "name":        "Narrative Build Pipeline",
        "group":       "game_os",
        "description": "Canon prefix → story arc → missions → events → lore",
        "credit_cost": 20,
        "steps": [
            {"engine": "playful_art_bible",  "action": "inject",   "description": "Canon prefix injection"},
            {"engine": "univ_story_arc_v1",  "action": "generate", "description": "Multi-stage story arc"},
            {"engine": "univ_mission_v1",    "action": "generate", "description": "Mission + quest generation"},
            {"engine": "univ_event_v1",      "action": "generate", "description": "Dynamic events + encounters"},
            {"engine": "univ_lore_v1",       "action": "generate", "description": "Narrative lore + history"},
        ],
        "output_type": "narrative_pack",
        "enabled_for": ["SLA113"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    "asset_pack_pipeline": {
        "id":          "asset_pack_pipeline",
        "name":        "Asset Pack Pipeline",
        "group":       "game_os",
        "description": "Canon prefix → visual style → title screen → theme filter → emotion overlay",
        "credit_cost": 16,
        "steps": [
            {"engine": "playful_art_bible",     "action": "inject",   "description": "Canon prefix injection"},
            {"engine": "univ_visual_style_v1",  "action": "generate", "description": "Backgrounds + style metadata"},
            {"engine": "univ_title_screen_v1",  "action": "generate", "description": "Title screen + intro"},
            {"engine": "univ_theme_filter_v1",  "action": "apply",    "description": "Theme transformation pass"},
            {"engine": "univ_emotion_filter_v1","action": "apply",    "description": "Emotion overlay pass"},
        ],
        "output_type": "asset_pack",
        "enabled_for": ["SLA113"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    "progression_reward_pipeline": {
        "id":          "progression_reward_pipeline",
        "name":        "Progression + Reward Pipeline",
        "group":       "game_os",
        "description": "Progression system → challenge curves → reward catalog",
        "credit_cost": 10,
        "steps": [
            {"engine": "univ_progression_v1", "action": "generate", "description": "XP + leveling + unlocks"},
            {"engine": "univ_challenge_v1",   "action": "generate", "description": "Difficulty curves + obstacles"},
            {"engine": "univ_reward_v1",      "action": "generate", "description": "Rewards + item catalog"},
        ],
        "output_type": "progression_pack",
        "enabled_for": ["SLA113"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    # ── CANON + IDENTITY PIPELINES (4) ───────────────────────────────────────

    "canon_injection_pipeline": {
        "id":          "canon_injection_pipeline",
        "name":        "Canon Injection Pipeline",
        "group":       "canon",
        "description": "PlayfulArtBible prefix → SGV+Aztec canon overlay → emotion filter",
        "credit_cost": 4,
        "steps": [
            {"engine": "playful_art_bible",     "action": "inject",  "description": "Root emotional canon prefix"},
            {"engine": "canon_layer_sgv_aztec", "action": "overlay", "description": "SGV + Aztec identity overlay"},
            {"engine": "univ_emotion_filter_v1","action": "apply",   "description": "Emotion overlay pass"},
        ],
        "output_type": "canon_prefix",
        "enabled_for": ["SLA113"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    "theme_apply_pipeline": {
        "id":          "theme_apply_pipeline",
        "name":        "Theme Apply Pipeline",
        "group":       "canon",
        "description": "Canon inject → theme filter → emotion overlay → visual style refresh",
        "credit_cost": 8,
        "steps": [
            {"engine": "playful_art_bible",     "action": "inject",   "description": "Canon prefix injection"},
            {"engine": "univ_theme_filter_v1",  "action": "apply",    "description": "Theme transformation pass"},
            {"engine": "univ_emotion_filter_v1","action": "apply",    "description": "Emotion overlay pass"},
            {"engine": "univ_visual_style_v1",  "action": "generate", "description": "Refreshed visual style"},
        ],
        "output_type": "themed_content",
        "enabled_for": ["SLA113"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    "lounge_build_pipeline": {
        "id":          "lounge_build_pipeline",
        "name":        "Lounge Hub Build Pipeline",
        "group":       "canon",
        "description": "Canon inject → hub layout → world env → audio pack → title screen",
        "credit_cost": 22,
        "steps": [
            {"engine": "playful_art_bible",    "action": "inject",   "description": "Root canon injection"},
            {"engine": "univ_world_v1",        "action": "generate", "description": "Hub environment + layout"},
            {"engine": "univ_visual_style_v1", "action": "generate", "description": "Visual style + atmosphere"},
            {"engine": "univ_title_screen_v1", "action": "generate", "description": "Lounge title + branding"},
            {"engine": "univ_dialogue_v1",     "action": "generate", "description": "Social dialogue lines"},
        ],
        "output_type": "lounge_bundle",
        "enabled_for": ["SLA113"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    "sgv_aztec_overlay_pipeline": {
        "id":          "sgv_aztec_overlay_pipeline",
        "name":        "SGV + Aztec Overlay Pipeline",
        "group":       "canon",
        "description": "Canon inject → SGV+Aztec overlay → lore layer → visual style stamp",
        "credit_cost": 6,
        "steps": [
            {"engine": "playful_art_bible",     "action": "inject",   "description": "Root canon prefix"},
            {"engine": "canon_layer_sgv_aztec", "action": "overlay",  "description": "SGV + Aztec thematic overlay"},
            {"engine": "univ_lore_v1",          "action": "generate", "description": "Cultural lore layer"},
            {"engine": "univ_visual_style_v1",  "action": "generate", "description": "Visual style with canon stamp"},
        ],
        "output_type": "canon_overlay_pack",
        "enabled_for": ["SLA113"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    "aztec_canon_pipeline": {
        "id":          "aztec_canon_pipeline",
        "name":        "Aztec Canon Generation",
        "group":       "canon",
        "description": "Canon inject → Aztec Engine → cultural interpreter → asset audit",
        "credit_cost": 25,
        "steps": [
            {"engine": "playful_art_bible",     "action": "inject",  "description": "Root canon prefix"},
            {"engine": "aztec_chicano_engine",  "action": "generate","description": "Primary Aztec-Chicano generation"},
            {"engine": "canon_layer_sgv_aztec", "action": "overlay", "description": "Identity verification pass"},
        ],
        "output_type": "canon_asset",
        "enabled_for": ["SLA113"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
        "canon_lock":  True,
    },

    # ── DEPLOYMENT + AUDIT PIPELINES (4) ─────────────────────────────────────

    "machine_deploy_pipeline": {
        "id":          "machine_deploy_pipeline",
        "name":        "Machine Deploy Pipeline",
        "group":       "deployment",
        "description": "Tenant validate → machine resolve → build spec sign → Southern stage deploy",
        "credit_cost": 0,
        "steps": [
            {"engine": "tenant_engine",   "action": "validate", "description": "Validate build spec + entitlement"},
            {"engine": "machine_engine",  "action": "resolve",  "description": "Resolve machine catalog"},
            {"engine": "machine_engine",  "action": "deploy",   "description": "Stage deploy to Southern active_builds"},
        ],
        "output_type": "deploy_receipt",
        "enabled_for": ["SLA113"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    "session_audit_pipeline": {
        "id":          "session_audit_pipeline",
        "name":        "Session Audit Pipeline",
        "group":       "deployment",
        "description": "Entropy audit → payout ledger check → REV_7 compliance → health report",
        "credit_cost": 0,
        "steps": [
            {"engine": "entropy_engine",  "action": "audit",   "description": "Verify seed rotation compliance"},
            {"engine": "payout_engine",   "action": "audit",   "description": "Ledger solvency check"},
        ],
        "output_type": "audit_report",
        "enabled_for": ["Southern", "SLA113"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    "rev7_sign_pipeline": {
        "id":          "rev7_sign_pipeline",
        "name":        "REV_7 Sign Pipeline",
        "group":       "deployment",
        "description": "Build spec → REV_7 signature encode → manifest archive → delivery cert",
        "credit_cost": 0,
        "steps": [
            {"engine": "tenant_engine",   "action": "validate",  "description": "Entitlement + spec validation"},
            {"engine": "machine_engine",  "action": "sign",      "description": "REV_7 fingerprint + cert issue"},
        ],
        "output_type": "signed_cert",
        "enabled_for": ["SLA113"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    "health_check_pipeline": {
        "id":          "health_check_pipeline",
        "name":        "Health Check Pipeline",
        "group":       "deployment",
        "description": "Entropy daemon → payout solvency → boundary integrity → REV_7 compliance",
        "credit_cost": 0,
        "steps": [
            {"engine": "entropy_engine",  "action": "health",  "description": "Entropy daemon alive + seed age"},
            {"engine": "payout_engine",   "action": "health",  "description": "Payout pool solvency check"},
        ],
        "output_type": "health_report",
        "enabled_for": ["Southern", "SLA113"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    # ── OG REV_7 BUILD PIPELINE (2) ──────────────────────────────────────────

    "og_rev7_build_pipeline": {
        "id":          "og_rev7_build_pipeline",
        "name":        "OG REV_7 Build Pipeline",
        "group":       "og_build",
        "description": "Original REV_7 manufacture chain: canon → full OS → sign → archive → deliver",
        "credit_cost": 80,
        "steps": [
            {"engine": "playful_art_bible",     "action": "inject",   "description": "Root canon injection"},
            {"engine": "univ_world_v1",         "action": "generate", "description": "World build"},
            {"engine": "univ_character_v1",     "action": "generate", "description": "Character build"},
            {"engine": "univ_narrative_v1",     "action": "generate", "description": "Narrative build"},
            {"engine": "univ_progression_v1",   "action": "generate", "description": "Progression system"},
            {"engine": "univ_reward_v1",        "action": "generate", "description": "Reward catalog"},
            {"engine": "univ_theme_filter_v1",  "action": "apply",    "description": "Theme pass"},
            {"engine": "univ_emotion_filter_v1","action": "apply",    "description": "Emotion pass"},
            {"engine": "canon_layer_sgv_aztec", "action": "overlay",  "description": "Canon stamp"},
            {"engine": "tenant_engine",         "action": "validate", "description": "Entitlement check"},
            {"engine": "machine_engine",        "action": "sign",     "description": "REV_7 sign + archive"},
            {"engine": "machine_engine",        "action": "deploy",   "description": "Deploy to Southern"},
        ],
        "output_type": "og_rev7_bundle",
        "enabled_for": ["SLA113"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },

    "og_rev7_patch_pipeline": {
        "id":          "og_rev7_patch_pipeline",
        "name":        "OG REV_7 Patch Pipeline",
        "group":       "og_build",
        "description": "Targeted patch to an existing OG REV_7 build — re-sign and re-deploy",
        "credit_cost": 20,
        "steps": [
            {"engine": "playful_art_bible",  "action": "inject",   "description": "Canon prefix refresh"},
            {"engine": "univ_theme_filter_v1","action": "apply",   "description": "Theme re-pass"},
            {"engine": "tenant_engine",      "action": "validate", "description": "Entitlement re-check"},
            {"engine": "machine_engine",     "action": "sign",     "description": "REV_7 re-sign"},
            {"engine": "machine_engine",     "action": "deploy",   "description": "Re-deploy patch to Southern"},
        ],
        "output_type": "patch_receipt",
        "enabled_for": ["SLA113"],
        "status":      "active",
        "math_rev":    "MATH_CORE_REV_7",
    },
}


# ========================================================
# SOUTHERN PIPELINE HELPERS
# ========================================================
def get_southern_pipeline(pipeline_id: str) -> Optional[dict]:
    return SOUTHERN_PIPELINES.get(pipeline_id)


def list_southern_pipelines(group: Optional[str] = None, tenant: Optional[str] = None) -> list[dict]:
    pipes = SOUTHERN_PIPELINES.values()
    if group:
        pipes = (p for p in pipes if p.get("group") == group)
    if tenant:
        pipes = (p for p in pipes if tenant in p.get("enabled_for", []))
    return list(pipes)


def calculate_southern_pipeline_cost(pipeline_id: str) -> int:
    pipeline = SOUTHERN_PIPELINES.get(pipeline_id)
    if not pipeline:
        return 0
    return pipeline.get("credit_cost", 0)
