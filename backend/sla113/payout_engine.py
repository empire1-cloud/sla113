"""
payout_engine.py
SLA113 Arcade — Payout Engine
Wired to SLA113SettlementEngine for reconciliation.

Responsibilities:
- Accept game result from fishing/slots/keno engines
- Apply governance limits (win ceiling, loss limit per session)
- Pass final amount to SLA113SettlementEngine.settle()
- Return settled payout with audit trace

Economic canon (from Build Spec):
  win_ceiling_multiplier: 100.0
  loss_limit_per_session_pct: 0.50
  betting_unit_minimum: 0.01
  betting_unit_maximum: 500.00
"""

import uuid
import time

from sla113.sla113_settlement_engine import SLA113SettlementEngine

# -- Build Spec economic canon --
WIN_CEILING_MULTIPLIER = 100.0
LOSS_LIMIT_SESSION_PCT = 0.50
BET_MIN = 0.01
BET_MAX = 500.00


class PayoutEngine:
    ENGINE_ID = "payout_engine"
    ENGINE_TYPE = "arcade"
    VERSION = "1.0.0"

    def __init__(self):
        self._settlement = SLA113SettlementEngine()

    def settle(
        self,
        tenant_id: str,
        player_id: str,
        game_result: dict,
        session_buy_in: float = 0.0,
        payout_id: str = None,
    ) -> dict:
        """
        Finalize payout for a completed game result.

        game_result must contain:
          - bet_amount: float
          - payout: float (pre-settlement gross payout)
          - multiplier: float
          - engine: str  (source engine id)

        Returns settled payout with audit trace.
        """
        payout_id = payout_id or str(uuid.uuid4())

        bet_amount = float(game_result.get("bet_amount", 0.0))
        gross_payout = float(game_result.get("payout", 0.0))
        multiplier = float(game_result.get("multiplier", 0.0))
        source_engine = game_result.get("engine", "unknown")

        # Enforce win ceiling (Build Spec: 100x bet)
        ceiling_payout = bet_amount * WIN_CEILING_MULTIPLIER
        capped = gross_payout > ceiling_payout
        gross_payout = min(gross_payout, ceiling_payout)

        # Enforce session loss limit (Build Spec: 50% of buy-in)
        loss_limit_note = None
        if session_buy_in > 0.0:
            max_loss = session_buy_in * LOSS_LIMIT_SESSION_PCT
            net = gross_payout - bet_amount
            if net < 0 and abs(net) > max_loss:
                # Player has hit loss limit; cap their loss at the limit
                gross_payout = bet_amount - max_loss
                gross_payout = max(0.0, gross_payout)
                loss_limit_note = f"Loss capped at {LOSS_LIMIT_SESSION_PCT*100:.0f}% of buy-in (${max_loss:.2f})"

        # Pass through SLA113SettlementEngine for reconciliation
        settlement_result = self._settlement.settle({
            "amount": gross_payout,
            "multiplier": 1.0,  # multiplier already applied by game engine
        })

        final_payout = round(settlement_result.get("final_value", gross_payout), 2)
        net = round(final_payout - bet_amount, 2)

        return {
            "engine": self.ENGINE_ID,
            "version": self.VERSION,
            "payout_id": payout_id,
            "tenant_id": tenant_id,
            "player_id": player_id,
            "source_engine": source_engine,
            "bet_amount": bet_amount,
            "gross_payout": gross_payout,
            "final_payout": final_payout,
            "net": net,
            "multiplier": multiplier,
            "win_ceiling_applied": capped,
            "loss_limit_note": loss_limit_note,
            "settlement_status": settlement_result.get("status", "ok"),
            "timestamp": int(time.time()),
        }
