"""
Lyrica Render Engine — MSGO Protocol (Multi-Stage GPU Orchestration).

Three render tiers with cost transparency:

  DRAFT:   22050Hz/16-bit, timesteps=5,  cfg=1.5, effects bypass   — $0.0003/clip
  PREVIEW: 44100Hz/16-bit, timesteps=8,  cfg=2.0, effects half-res — $0.0008/clip
  FINAL:   48000Hz/24-bit, timesteps=12, cfg=2.5, effects full+dither — $0.0020/clip
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

RENDER_TIERS = {
    "DRAFT": {
        "sample_rate": 22050,
        "bit_depth": 16,
        "subtype": "PCM_16",
        "inference_timesteps": 5,
        "cfg_value": 1.5,
        "effects_mode": "bypass",
        "est_cost_usd": 0.0003,
        "description": "Fast preview — low quality, no effects, minimal GPU",
    },
    "PREVIEW": {
        "sample_rate": 44100,
        "bit_depth": 16,
        "subtype": "PCM_16",
        "inference_timesteps": 8,
        "cfg_value": 2.0,
        "effects_mode": "half_res",
        "est_cost_usd": 0.0008,
        "description": "Mid-quality preview — effects at half resolution",
    },
    "FINAL": {
        "sample_rate": 48000,
        "bit_depth": 24,
        "subtype": "FLOAT",
        "inference_timesteps": 12,
        "cfg_value": 2.5,
        "effects_mode": "full_res_dithered",
        "est_cost_usd": 0.0020,
        "description": "Studio master — 48kHz/24-bit, full effects with dithering",
    },
}


def get_render_config(mode: str = "FINAL") -> dict:
    """Get render configuration for the specified tier."""
    tier = RENDER_TIERS.get(mode.upper(), RENDER_TIERS["DRAFT"])
    logger.info("[MSGO] Initializing %s render. Cost: $%s/clip", mode, tier["est_cost_usd"])
    return {"mode": mode.upper(), **tier}


def estimate_session_cost(
    num_clips: int = 1,
    mode: str = "FINAL",
    apply_effects: bool = True,
    num_stems: int = 1,
) -> dict:
    """Estimate total cost for a production session."""
    tier = RENDER_TIERS.get(mode.upper(), RENDER_TIERS["DRAFT"])
    base_cost = tier["est_cost_usd"] * num_clips

    fx_multiplier = 1.2 if apply_effects and tier["effects_mode"] != "bypass" else 1.0
    stem_multiplier = 1.0 + (num_stems - 1) * 0.3

    total = base_cost * fx_multiplier * stem_multiplier

    return {
        "mode": mode.upper(),
        "num_clips": num_clips,
        "cost_per_clip": tier["est_cost_usd"],
        "effects_applied": apply_effects,
        "num_stems": num_stems,
        "estimated_total_usd": round(total, 6),
        "breakdown": {
            "base_generation": round(base_cost, 6),
            "effects_overhead": round(base_cost * (fx_multiplier - 1), 6),
            "stem_overhead": round(base_cost * (stem_multiplier - 1), 6),
        },
    }


def list_render_tiers() -> dict:
    return {
        name: {
            "sample_rate": t["sample_rate"],
            "bit_depth": t["bit_depth"],
            "inference_timesteps": t["inference_timesteps"],
            "cfg_value": t["cfg_value"],
            "effects_mode": t["effects_mode"],
            "est_cost_usd": t["est_cost_usd"],
            "description": t["description"],
        }
        for name, t in RENDER_TIERS.items()
    }
