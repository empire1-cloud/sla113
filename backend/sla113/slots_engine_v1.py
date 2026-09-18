"""
slots_engine_v1.py
SLA113 Arcade — Classic Slots Engine V1
Derived from SLA113_BUILD_SPEC.yaml: machine_profiles.slots

Config (from Build Spec):
  default_rtp: 0.95
  default_volatility: 0.6
  player_skill_factor: 0.0  (pure chance)
  narrative_beat_primary: "climactic"
  reel_count_standard: 5       (from canon.shell)
  payline_count_standard: 20   (from canon.shell)
  symbol_count_unique: 12      (from canon.shell)

Bonus features (from Build Spec):
  free_spins_enabled: true
  multiplier_bonus_enabled: true
  progressive_jackpot_enabled: true
  progressive_pool_contribution_pct: 0.02

Themes: gold_rush | ancient_egypt | space_odyssey | wild_west
"""

import random
import uuid
import time
from typing import Optional

# -- Build Spec constants --
SLOTS_RTP_DEFAULT = 0.95
SLOTS_VOLATILITY_DEFAULT = 0.6
SLOTS_WIN_CEILING = 100.0
PROGRESSIVE_CONTRIBUTION_PCT = 0.02

# Reel/symbol config from canon.shell
REEL_COUNT = 5
PAYLINE_COUNT = 20
SYMBOL_COUNT = 12

# Symbol weights (lower index = higher value, lower frequency)
SYMBOL_WEIGHTS = [1, 1, 2, 2, 3, 4, 5, 7, 9, 12, 15, 20]
SYMBOL_MULTIPLIERS = {
    0: 50.0,   # jackpot
    1: 25.0,
    2: 15.0,
    3: 10.0,
    4: 8.0,
    5: 5.0,
    6: 3.0,
    7: 2.0,
    8: 1.5,
    9: 1.0,
    10: 0.5,
    11: 0.0,   # blank
}

VALID_THEMES = {"gold_rush", "ancient_egypt", "space_odyssey", "wild_west"}


class SlotsEngineV1:
    ENGINE_ID = "slots_engine_v1"
    ENGINE_TYPE = "arcade"
    VERSION = "1.0.0"

    def __init__(
        self,
        rtp: float = SLOTS_RTP_DEFAULT,
        volatility: float = SLOTS_VOLATILITY_DEFAULT,
        theme: str = "gold_rush",
    ):
        self.rtp = rtp
        self.volatility = volatility
        self.theme = theme if theme in VALID_THEMES else "gold_rush"

    def spin(
        self,
        tenant_id: str,
        player_id: str,
        bet_amount: float,
        session_id: Optional[str] = None,
    ) -> dict:
        """
        Execute a single spin on 5 reels.
        Returns reel symbols, win lines, payout, bonus triggers.
        """
        session_id = session_id or str(uuid.uuid4())

        # Spin all 5 reels
        reels = [self._spin_reel() for _ in range(REEL_COUNT)]

        # Evaluate paylines (simplified: check 3+ matching on center row)
        win_lines, base_multiplier = self._evaluate_paylines(reels)

        # Apply RTP correction
        adjusted_multiplier = base_multiplier * self.rtp
        adjusted_multiplier = min(adjusted_multiplier, SLOTS_WIN_CEILING)

        payout = round(bet_amount * adjusted_multiplier, 2)
        net = round(payout - bet_amount, 2)

        # Progressive contribution (Build Spec: 2% of bet)
        progressive_contribution = round(bet_amount * PROGRESSIVE_CONTRIBUTION_PCT, 4)

        # Bonus triggers
        bonus = self._check_bonus(reels)

        narrative_beat = "climactic" if base_multiplier >= 5.0 else (
            "endgame" if base_multiplier >= 20.0 else "ambient"
        )

        return {
            "engine": self.ENGINE_ID,
            "version": self.VERSION,
            "session_id": session_id,
            "tenant_id": tenant_id,
            "player_id": player_id,
            "theme": self.theme,
            "bet_amount": bet_amount,
            "reels": reels,
            "win_lines": win_lines,
            "multiplier": adjusted_multiplier,
            "payout": payout,
            "net": net,
            "progressive_contribution": progressive_contribution,
            "bonus": bonus,
            "narrative_beat": narrative_beat,
            "timestamp": int(time.time()),
        }

    def _spin_reel(self) -> list:
        """Spin a single reel, return 3 visible symbols (top, center, bottom)."""
        return random.choices(
            population=list(range(SYMBOL_COUNT)),
            weights=SYMBOL_WEIGHTS,
            k=3
        )

    def _evaluate_paylines(self, reels: list) -> tuple:
        """Evaluate center row payline across all 5 reels."""
        center_row = [reel[1] for reel in reels]
        win_lines = []
        best_multiplier = 0.0

        # Check consecutive matching from left
        first = center_row[0]
        match_count = 1
        for sym in center_row[1:]:
            if sym == first:
                match_count += 1
            else:
                break

        if match_count >= 3:
            sym_mult = SYMBOL_MULTIPLIERS.get(first, 0.0)
            line_multiplier = sym_mult * (match_count - 2)  # 3=1x, 4=2x, 5=3x
            if line_multiplier > 0:
                win_lines.append({
                    "line": "center",
                    "symbol": first,
                    "count": match_count,
                    "multiplier": line_multiplier,
                })
                best_multiplier = max(best_multiplier, line_multiplier)

        return win_lines, best_multiplier

    def _check_bonus(self, reels: list) -> dict:
        """Check for bonus feature triggers (Build Spec: free_spins, multiplier_bonus)."""
        # Count scatter symbols (symbol 1) across all positions
        all_symbols = [sym for reel in reels for sym in reel]
        scatter_count = all_symbols.count(1)

        free_spins = 0
        multiplier_active = False
        jackpot_trigger = False

        if scatter_count >= 3:
            free_spins = scatter_count * 5  # 3 scatters = 15 free spins

        # Jackpot: 5 symbol-0 in center row
        center_row = [reel[1] for reel in reels]
        if all(s == 0 for s in center_row):
            jackpot_trigger = True

        # Multiplier bonus: any 3+ symbol-2
        if all_symbols.count(2) >= 3:
            multiplier_active = True

        return {
            "free_spins_awarded": free_spins,
            "multiplier_bonus_active": multiplier_active,
            "progressive_jackpot_triggered": jackpot_trigger,
        }
