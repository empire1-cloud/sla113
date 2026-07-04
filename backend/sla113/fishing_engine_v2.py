"""
fishing_engine_v2.py
SLA113 Arcade — Fish Shooting Engine V2
Derived from SLA113_BUILD_SPEC.yaml: machine_profiles.fish

Config (from Build Spec):
  default_rtp: 0.94
  default_volatility: 0.5
  player_skill_factor: 0.30  (30% skill, 70% chance)
  narrative_beat_primary: "climactic"

Catch rates & multipliers (from Build Spec):
  common:    rate=0.70  multiplier=1.0x
  uncommon:  rate=0.25  multiplier=3.0x
  rare:      rate=0.04  multiplier=10.0x
  epic:      rate=0.01  multiplier=50.0x

Economic canon (from Build Spec):
  win_ceiling_multiplier: 100.0
  loss_limit_per_session_pct: 0.50
"""

import random
import uuid
import time
from typing import Optional


# -- Build Spec constants --
FISH_RTP_DEFAULT = 0.94
FISH_VOLATILITY_DEFAULT = 0.5
FISH_SKILL_FACTOR = 0.30
FISH_WIN_CEILING = 100.0

CATCH_TIERS = [
    {"tier": "epic",     "rate": 0.01, "multiplier": 50.0},
    {"tier": "rare",     "rate": 0.04, "multiplier": 10.0},
    {"tier": "uncommon", "rate": 0.25, "multiplier": 3.0},
    {"tier": "common",   "rate": 0.70, "multiplier": 1.0},
]


class FishingEngineV2:
    ENGINE_ID = "fishing_engine_v2"
    ENGINE_TYPE = "arcade"
    VERSION = "2.0.0"

    def __init__(
        self,
        rtp: float = FISH_RTP_DEFAULT,
        volatility: float = FISH_VOLATILITY_DEFAULT,
        skill_factor: float = FISH_SKILL_FACTOR,
    ):
        self.rtp = rtp
        self.volatility = volatility
        self.skill_factor = skill_factor

    def cast(
        self,
        tenant_id: str,
        player_id: str,
        bet_amount: float,
        skill_score: float = 0.5,
        session_id: Optional[str] = None,
    ) -> dict:
        """
        Execute a single cast/shot.
        skill_score: 0.0–1.0, supplied by client (clamped internally).
        Returns catch result, payout, and narrative beat.
        """
        session_id = session_id or str(uuid.uuid4())
        skill_score = max(0.0, min(1.0, skill_score))

        # Blend skill influence into effective hit probability
        # 30% of outcome from skill, 70% pure RNG (Build Spec: player_skill_factor=0.30)
        skill_bonus = self.skill_factor * skill_score
        base_roll = random.random()
        effective_roll = base_roll * (1.0 - self.skill_factor) + (1.0 - skill_score) * self.skill_factor

        tier = self._resolve_tier(effective_roll)
        multiplier = tier["multiplier"]

        # Apply RTP correction: scale multiplier toward configured RTP
        adjusted_multiplier = multiplier * self.rtp

        # Enforce win ceiling (Build Spec: win_ceiling_multiplier=100.0)
        adjusted_multiplier = min(adjusted_multiplier, FISH_WIN_CEILING)

        payout = round(bet_amount * adjusted_multiplier, 2)
        net = round(payout - bet_amount, 2)

        return {
            "engine": self.ENGINE_ID,
            "version": self.VERSION,
            "session_id": session_id,
            "tenant_id": tenant_id,
            "player_id": player_id,
            "bet_amount": bet_amount,
            "catch_tier": tier["tier"],
            "multiplier": adjusted_multiplier,
            "payout": payout,
            "net": net,
            "narrative_beat": "climactic" if tier["tier"] in ("rare", "epic") else "ambient",
            "timestamp": int(time.time()),
        }

    def _resolve_tier(self, roll: float) -> dict:
        """Resolve catch tier from roll using cumulative probabilities."""
        cumulative = 0.0
        for tier in CATCH_TIERS:
            cumulative += tier["rate"]
            if roll <= cumulative:
                return tier
        return CATCH_TIERS[-1]  # fallback: common
