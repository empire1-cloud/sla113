"""
keno_engine_v1.py
SLA113 Arcade — Keno Engine V1
Derived from SLA113_BUILD_SPEC.yaml: machine_profiles.keno

Config (from Build Spec):
  default_rtp: 0.93
  default_volatility: 0.4
  player_skill_factor: 0.0  (pure chance)
  narrative_beat_primary: "ambient"
  max_numbers_selectable: 20
  draw_frequency_seconds: 60

Payout table (from Build Spec):
  match_5:  1.0x
  match_10: 5.0x
  match_15: 20.0x
  match_20: 500.0x
"""

import random
import uuid
import time
from typing import List, Optional

# -- Build Spec constants --
KENO_RTP_DEFAULT = 0.93
KENO_VOLATILITY_DEFAULT = 0.4
KENO_WIN_CEILING = 100.0
KENO_MAX_NUMBERS = 20
KENO_DRAW_POOL = 80   # Standard keno pool: 1–80
KENO_DRAW_COUNT = 20  # 20 numbers drawn per round

# Payout table from Build Spec (matches → multiplier)
PAYOUT_TABLE = {
    20: 500.0,
    15: 20.0,
    10: 5.0,
    5:  1.0,
}


class KenoEngineV1:
    ENGINE_ID = "keno_engine_v1"
    ENGINE_TYPE = "arcade"
    VERSION = "1.0.0"

    def __init__(
        self,
        rtp: float = KENO_RTP_DEFAULT,
        volatility: float = KENO_VOLATILITY_DEFAULT,
    ):
        self.rtp = rtp
        self.volatility = volatility

    def draw(
        self,
        tenant_id: str,
        player_id: str,
        bet_amount: float,
        player_picks: List[int],
        session_id: Optional[str] = None,
    ) -> dict:
        """
        Execute a single keno draw.
        player_picks: list of integers 1–80, max 20 numbers.
        Returns draw result, matches, payout.
        """
        session_id = session_id or str(uuid.uuid4())

        # Validate player picks (Build Spec: max 20 numbers)
        player_picks = [p for p in player_picks if 1 <= p <= KENO_DRAW_POOL][:KENO_MAX_NUMBERS]
        if not player_picks:
            return {
                "engine": self.ENGINE_ID,
                "error": "No valid picks provided",
                "session_id": session_id,
            }

        # Draw 20 random numbers from pool
        drawn_numbers = sorted(random.sample(range(1, KENO_DRAW_POOL + 1), KENO_DRAW_COUNT))

        # Count matches
        matched = sorted(set(player_picks) & set(drawn_numbers))
        match_count = len(matched)

        # Resolve payout from Build Spec payout table
        multiplier = self._resolve_payout(match_count)

        # Apply RTP correction
        adjusted_multiplier = multiplier * self.rtp
        adjusted_multiplier = min(adjusted_multiplier, KENO_WIN_CEILING)

        payout = round(bet_amount * adjusted_multiplier, 2)
        net = round(payout - bet_amount, 2)

        narrative_beat = "climactic" if match_count >= 15 else (
            "endgame" if match_count == 20 else "ambient"
        )

        return {
            "engine": self.ENGINE_ID,
            "version": self.VERSION,
            "session_id": session_id,
            "tenant_id": tenant_id,
            "player_id": player_id,
            "bet_amount": bet_amount,
            "player_picks": sorted(player_picks),
            "drawn_numbers": drawn_numbers,
            "matched_numbers": matched,
            "match_count": match_count,
            "multiplier": adjusted_multiplier,
            "payout": payout,
            "net": net,
            "narrative_beat": narrative_beat,
            "draw_frequency_seconds": 60,  # Build Spec
            "timestamp": int(time.time()),
        }

    def _resolve_payout(self, match_count: int) -> float:
        """Resolve multiplier from Build Spec payout table."""
        # Find the highest matching threshold
        for threshold in sorted(PAYOUT_TABLE.keys(), reverse=True):
            if match_count >= threshold:
                return PAYOUT_TABLE[threshold]
        return 0.0
