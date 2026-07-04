from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class TenantContext(BaseModel):
    tenant_id: str
    tenant_name: str
    tenant_type: str  # "empire1" | "southern_lyfestyle_arcade"


class EngineInvocationRequest(BaseModel):
    engine: str  # "vision_smith" | "voice_king" | "sonic_forge" | "vo_engine"
    action: str  # "generate" | "upscale" | "clone" | etc.
    payload: dict
    tenant_id: str


class UsageLogEntry(BaseModel):
    id: str
    tenant_id: str
    tenant_name: str
    engine: str
    action: str
    timestamp: datetime
    credits_used: int
    metadata: Optional[dict] = None


class PermissionCheckRequest(BaseModel):
    tenant_id: str
    engine: str
    action: str


# ---------------------------------------------------------
# TENANT DEFINITIONS (from canon)
# ---------------------------------------------------------
TENANTS = {
    "empire1": {
        "id": "empire1",
        "name": "EMPIRE1",
        "type": "business_tenant",
        "allowed_engines": ["vision_smith", "voice_king", "sonic_forge", "vo_engine"],
    },
    "southern_lyfestyle_arcade": {
        "id": "southern_lyfestyle_arcade",
        "display_name": "Southern Lyfestyle Arcade",
        "name": "Southern Lyfestyle Arcade",
        "type": "cultural_gaming_tenant",
        "theme": "THEME_SOUTHERN_LYFESTYLE",
        "allowed_engines": [
            "vision_smith", "voice_king", "sonic_forge", "vo_engine",
            "fishing_engine_v2", "payout_engine", "machine_engine",
            "canon_layer_sgv_aztec",
        ],
        "machine_catalog": {
            "fish_shooting": 20,
            "slots": 0,
            "keno": 0,
            "custom_games": [],
        },
        "overrides": {
            "volatility_curve": "high_risk_sgv",
            "emotional_curve": "street_glow_arc",
            "cinematic_pacing": "barrio_intensity",
            "payout_profile": "high_risk_high_reward",
        },
    },
    "horror_arcade": {
        "id": "horror_arcade",
        "display_name": "Horror Arcade",
        "name": "Horror Arcade",
        "type": "gaming_tenant",
        "theme": "THEME_HORROR",
        "allowed_engines": [
            "vision_smith", "voice_king", "sonic_forge", "vo_engine",
            "slots_engine_v1", "payout_engine", "machine_engine",
        ],
        "machine_catalog": {
            "fish_shooting": 0,
            "slots": 30,
            "keno": 0,
            "custom_games": ["haunted_reels", "dread_shooter"],
        },
        "overrides": {
            "volatility_curve": "slow_rise_dread",
            "emotional_curve": "fear_tension_arc",
            "cinematic_pacing": "dark_suspense",
            "payout_profile": "slow_burn_spike",
        },
    },
    "anime_arcade": {
        "id": "anime_arcade",
        "display_name": "Anime Arcade",
        "name": "Anime Arcade",
        "type": "gaming_tenant",
        "theme": "THEME_ANIME",
        "allowed_engines": [
            "vision_smith", "voice_king", "sonic_forge", "vo_engine",
            "fishing_engine_v2", "slots_engine_v1", "payout_engine", "machine_engine",
        ],
        "machine_catalog": {
            "fish_shooting": 10,
            "slots": 10,
            "keno": 0,
            "custom_games": ["rhythm_battle", "hero_duel"],
        },
        "overrides": {
            "volatility_curve": "fast_rise_shonen",
            "emotional_curve": "hero_arc",
            "cinematic_pacing": "explosive_crests",
            "payout_profile": "frequent_small_big_peak",
        },
    },
    # Build Spec tenants (vegas, london, sydney)
    "tenant_casino_vegas": {
        "id": "tenant_casino_vegas",
        "display_name": "Downtown Vegas Casino",
        "name": "Downtown Vegas Casino",
        "type": "gaming_tenant",
        "theme": "theme_vegas_classic",
        "allowed_engines": [
            "fishing_engine_v2", "slots_engine_v1", "keno_engine_v1",
            "payout_engine", "machine_engine", "tenant_engine",
        ],
        "machine_catalog": {
            "fish_shooting": 10,
            "slots": 20,
            "keno": 10,
            "custom_games": [],
        },
    },
    "tenant_arcade_london": {
        "id": "tenant_arcade_london",
        "display_name": "London Arcade Club",
        "name": "London Arcade Club",
        "type": "gaming_tenant",
        "theme": "theme_london_neon",
        "allowed_engines": [
            "fishing_engine_v2", "slots_engine_v1",
            "payout_engine", "machine_engine", "tenant_engine",
        ],
        "machine_catalog": {
            "fish_shooting": 15,
            "slots": 15,
            "keno": 0,
            "custom_games": [],
        },
    },
    "tenant_gaming_sydney": {
        "id": "tenant_gaming_sydney",
        "display_name": "Sydney Gaming Hub",
        "name": "Sydney Gaming Hub",
        "type": "gaming_tenant",
        "theme": "theme_sydney_modern",
        "allowed_engines": [
            "fishing_engine_v2", "slots_engine_v1", "keno_engine_v1",
            "payout_engine", "machine_engine", "tenant_engine",
        ],
        "machine_catalog": {
            "fish_shooting": 10,
            "slots": 20,
            "keno": 10,
            "custom_games": [],
        },
    },
}

# ---------------------------------------------------------
# ENGINE ROUTE MAPPING (Hybrid backend endpoints)
# ---------------------------------------------------------
ENGINE_ROUTES = {
    "vision_smith": {
        "generate": "/vision/generate",
        "upscale": "/vision/upscale",
        "metadata": "/vision/metadata",
    },
    "voice_king": {
        "generate": "/voice/generate",
        "clone": "/voice/clone",
        "list_voices": "/voice/voices",
    },
    "sonic_forge": {
        "generate": "/sonicforge/generate",
        "separate": "/sonicforge/separate",
        "status": "/sonicforge/status",
    },
    "vo_engine": {
        "generate": "/video/generate",
        "status": "/video/status",
        "frames": "/video/frames",
    },
    # Arcade engines
    "fishing_engine_v2": {
        "cast": "/sla113/arcade/fish/spin",
    },
    "slots_engine_v1": {
        "spin": "/sla113/arcade/slots/spin",
    },
    "keno_engine_v1": {
        "draw": "/sla113/arcade/keno/draw",
    },
    "payout_engine": {
        "settle": "/sla113/arcade/payout/settle",
    },
    "machine_engine": {
        "catalog": "/sla113/machines/{tenant_id}",
        "resolve": "/sla113/machines/{tenant_id}/resolve",
    },
    "tenant_engine": {
        "resolve": "/sla113/tenant/{tenant_id}",
        "list": "/sla113/tenant/list",
    },
    "canon_layer_sgv_aztec": {
        "apply": "/sla113/arcade/canon/sgv-aztec/apply",
        "symbols": "/sla113/arcade/canon/sgv-aztec/symbols",
    },
}
