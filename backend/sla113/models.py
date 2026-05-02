"""SLA113 Data Models"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid


# ─── Game Types (Full Taxonomy) ───
GAME_TYPES = {
    # ━━━ ARCADE & ACTION ━━━
    "arcade_classic": {
        "name": "Arcade Classic",
        "description": "Retro coin-op arcade games — high scores, lives, power-ups",
        "category": "arcade",
    },
    "fish_shooting": {
        "name": "Fish Shooting",
        "description": "Multiplayer fish hunting arcade with weapon upgrades and boss fights",
        "category": "arcade",
    },
    "battle_royale": {
        "name": "Battle Royale",
        "description": "Last-player-standing arena combat with shrinking zones and loot",
        "category": "arcade",
    },
    "tactical_fps": {
        "name": "Tactical FPS",
        "description": "Military tactical shooter with loadouts, maps, and multiplayer",
        "category": "arcade",
    },
    "cod_warfare": {
        "name": "COD Warfare",
        "description": "Modern warfare FPS — killstreaks, prestige ranks, competitive multiplayer",
        "category": "arcade",
    },
    "platformer": {
        "name": "Platformer",
        "description": "Side-scrolling platform game with levels, enemies, and power-ups",
        "category": "arcade",
    },
    "fighting": {
        "name": "Fighting",
        "description": "2D/3D fighting game — movesets, combos, frame data, special meters",
        "category": "arcade",
    },
    "puzzle": {
        "name": "Puzzle",
        "description": "Match-3, tile-based, or logic puzzle game with progressive difficulty",
        "category": "arcade",
    },
    "adventure": {
        "name": "Adventure",
        "description": "Story-driven adventure with exploration, inventory, and dialogue trees",
        "category": "arcade",
    },
    "open_world": {
        "name": "Open World",
        "description": "GTA-style cinematic open world with missions, vehicles, and NPC AI",
        "category": "arcade",
    },

    # ━━━ CASINO & GAMBLING ━━━
    "slot_machine": {
        "name": "Slot Machine",
        "description": "Classic/video slot with reels, paylines, wilds, scatters, and bonus rounds",
        "category": "casino",
    },
    "video_poker": {
        "name": "Video Poker",
        "description": "Draw poker with paytable odds, hold/discard mechanics, and multi-hand variants",
        "category": "casino",
    },
    "casino_suite": {
        "name": "Casino Suite",
        "description": "Full casino lobby — slots, table games, live dealer, and jackpot network",
        "category": "casino",
    },
    "pachinko": {
        "name": "Pachinko",
        "description": "Japanese pachinko/pachislot with ball physics, fever modes, and jackpot mechanics",
        "category": "casino",
    },
    "lottery": {
        "name": "Lottery",
        "description": "Number draw lottery with instant win, scratch cards, and progressive jackpots",
        "category": "casino",
    },
    "bingo": {
        "name": "Bingo",
        "description": "Multiplayer bingo with pattern matching, power-ups, and themed rooms",
        "category": "casino",
    },
    "sportsbook": {
        "name": "Sportsbook",
        "description": "Sports betting platform with live odds, parlays, and in-play wagering",
        "category": "casino",
    },
    "card_games": {
        "name": "Card Games",
        "description": "Poker, blackjack, baccarat — classic card games with RNG and live variants",
        "category": "casino",
    },

    # ━━━ RPG & NARRATIVE ━━━
    "open_world_rpg": {
        "name": "Open World RPG",
        "description": "Massive RPG with quests, factions, skill trees, and open exploration",
        "category": "rpg",
    },
    "dungeon_crawler": {
        "name": "Dungeon Crawler",
        "description": "Procedural dungeons with loot, permadeath, and escalating difficulty",
        "category": "rpg",
    },
    "fantasy_rpg": {
        "name": "Fantasy RPG",
        "description": "High fantasy RPG with magic systems, crafting, and epic storylines",
        "category": "rpg",
    },
    "cyberpunk": {
        "name": "Cyberpunk",
        "description": "Neon-drenched dystopian RPG with hacking, augmentations, and noir narrative",
        "category": "rpg",
    },
    "horror": {
        "name": "Horror",
        "description": "Survival horror with atmospheric tension, resource scarcity, and jump scares",
        "category": "rpg",
    },
    "southern_barrio": {
        "name": "Southern Barrio",
        "description": "Southern lifestyle narrative — culture, community, and street-level storytelling",
        "category": "rpg",
    },
    "sandbox": {
        "name": "Sandbox",
        "description": "Open creative sandbox — build, destroy, craft, and survive in a voxel/block world",
        "category": "rpg",
    },

    # ━━━ RACING & SIMULATION ━━━
    "racing_sim": {
        "name": "Racing Sim",
        "description": "High-fidelity racing simulation with real physics, tuning, and multiplayer leagues",
        "category": "racing",
    },

    # ━━━ HYBRID & CUSTOM ━━━
    "hybrid_mix": {
        "name": "Hybrid Mix",
        "description": "Cross-genre hybrid combining mechanics from multiple game types",
        "category": "hybrid_custom",
    },
    "generic_game_asset": {
        "name": "Generic Game Asset",
        "description": "Universal game asset generation — sprites, backgrounds, UI, VFX for any genre",
        "category": "hybrid_custom",
    },
    "custom_partner": {
        "name": "Custom Partner Games",
        "description": "White-label custom game builds for partner studios and operators",
        "category": "hybrid_custom",
    },
}

# ─── Audio Middleware Types ───
AUDIO_MIDDLEWARE_TYPES = {
    "sfx": {"name": "SFX", "description": "Sound effects — impacts, explosions, UI clicks, ambient hits"},
    "ambience": {"name": "Ambience", "description": "Environmental soundscapes — rain, wind, crowds, nature"},
    "foley": {"name": "Foley", "description": "Recorded physical sounds — footsteps, cloth, doors, weapons"},
    "music_cues": {"name": "Music Cues", "description": "Dynamic music triggers — victory, defeat, boss intro, menu themes"},
    "stems": {"name": "Stems", "description": "Isolated instrument tracks for adaptive mixing (drums, bass, melody)"},
    "loops": {"name": "Loops", "description": "Seamless looping audio — background music, ambient loops, rhythm patterns"},
    "tts": {"name": "TTS", "description": "Text-to-speech voice generation for NPCs, narration, and UI"},
    "voice_routing": {"name": "Voice Routing", "description": "Live voice processing — spatial audio, radio effects, VOIP integration"},
}

# ─── FMOD-Compatible Audio Engines ───
AUDIO_ENGINES = ["FMOD", "SonicForge", "AudioKing", "VoiceKing"]


# ━━━ Pydantic Models ━━━

class CreateProjectRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    game_type: str = Field(..., description="One of the supported game types")
    description: Optional[str] = None
    theme: Optional[str] = Field(None, description="Visual theme")
    target_platform: str = Field(default="web", description="web, mobile, or both")


class VisionGenerateRequest(BaseModel):
    project_id: str
    asset_type: str = Field(default="sprites")
    style: Optional[str] = None
    count: int = Field(default=5, ge=1, le=20)
    custom_prompt: Optional[str] = None


class LogicGenerateRequest(BaseModel):
    project_id: str
    logic_type: str = Field(default="mechanics")
    difficulty: str = Field(default="medium")
    custom_requirements: Optional[str] = None


class ComposeRequest(BaseModel):
    project_id: str
    include_vision: bool = True
    include_logic: bool = True
    output_format: str = Field(default="json")


class ImageGenRequest(BaseModel):
    prompt: str
    style: str = "pixel_art"
    asset_type: str = "concept_art"
    size: str = "1024x1024"
    quality: str = "high"


class TerminalRequest(BaseModel):
    command: str
    session_id: Optional[str] = "default"


class CreateTenantRequest(BaseModel):
    name: str
    subdomain: str
    config: Optional[dict] = None


class CreateJobRequest(BaseModel):
    preset: str
    config: Optional[dict] = None
    priority: str = "normal"
    depends_on: Optional[List[str]] = None


class CreatePipelineRequest(BaseModel):
    name: str
    type: str = "Automation"
    lane: int = 1


class CreateBuildRequest(BaseModel):
    project_id: str
    target: str = "webgl"
    optimization: str = "balanced"
    include_assets: bool = True
    include_logic: bool = True


class ComplianceCheckRequest(BaseModel):
    project_id: str
    jurisdiction: str = "GLI"
    check_type: str = "full"


class DeployRequest(BaseModel):
    build_id: str
    target_cdn: str = "cloudflare"
    region: str = "us-west"
    auto_ssl: bool = True


class AudioForgeRequest(BaseModel):
    audio_type: str = Field(default="sfx", description="sfx, ambience, foley, music_cues, stems, loops, tts, voice_routing")
    title: str = Field(..., min_length=1, max_length=200)
    game_type: str = Field(default="generic")
    engine: str = Field(default="FMOD")
    custom_params: Optional[dict] = None
