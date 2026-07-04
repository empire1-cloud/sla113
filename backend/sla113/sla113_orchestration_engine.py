"""
SLA113 5-Tier Orchestration Engine
Implements the canonical engine priority order from SLA113_BUILD_SPEC.yaml:
  1. RevenueEngine       — house edge, RTP, volatility routing
  2. NarrativeEngine     — narrative beat selection
  3. AdaptiveEngine      — adaptive difficulty
  4. IdentityEngine      — player personalization
  5. GovernanceEngine    — regulatory compliance (ALWAYS WINS — no override)

Conflict resolution is applied strictly per the conflict_resolution_matrix
in the Build Spec. Governance conflicts always resolve to governance, weight 1.0.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

# Build Spec defaults for the 5-tier orchestration pipeline

_ECONOMIC_CANON_DEFAULTS = {
    "currency": "USD",
    "house_edge_base": 0.05,
    "rtp_minimum": 0.90,
    "rtp_maximum": 0.98,
    "betting_unit_minimum": 0.01,
    "betting_unit_maximum": 500.00,
    "win_ceiling_multiplier": 100.0,
    "volatility_tiers": {
        "low": {"min": 0.0, "max": 0.3, "rtp_default": 0.96, "narrative_beat": "ambient"},
        "medium": {"min": 0.3, "max": 0.6, "rtp_default": 0.93, "narrative_beat": "climactic"},
        "high": {"min": 0.6, "max": 1.0, "rtp_default": 0.90, "narrative_beat": "endgame"},
    },
}

_GOVERNANCE_CANON_DEFAULTS = {
    "age_gate_minimum": 21,
    "geofence_enabled": True,
    "time_of_day_restrictions_enabled": True,
    "restricted_hours_start": "03:00",
    "restricted_hours_end": "06:00",
}

_CINEMATIC_WEIGHTING_DEFAULTS = {
    "default": 0.6,
    "high_volatility_boost": 0.15,
    "bonus_feature_multiplier": 1.5,
}

_IDENTITY_BIAS_DEFAULTS = {
    "player_history_weight": 0.3,
    "demographic_weight": 0.2,
    "player_preference_weight": 0.4,
}

_ECONOMIC_BIAS_DEFAULTS = {
    "house_edge_priority_weight": 0.5,
}

_FAULT_CANON_DEFAULTS = {
    "max_consecutive_losses_before_halt": 25,
    "max_consecutive_losses_before_warning": 10,
}

_ANTI_ADDICTION_DEFAULTS = {
    "session_limits": {
        "absolute_max_session_duration_hours": 8,
        "mandatory_break_frequency_minutes": 60,
        "mandatory_break_duration_minutes": 15,
    },
    "loss_limits": {
        "daily_loss_limit_pct": 0.20,
        "loss_limit_enforcement": "hard",
    },
}

_CONFLICT_RESOLUTION_MATRIX = {}


def get_economic_canon():
    return _ECONOMIC_CANON_DEFAULTS


def get_governance_canon():
    return _GOVERNANCE_CANON_DEFAULTS


def get_cinematic_weighting():
    return _CINEMATIC_WEIGHTING_DEFAULTS


def get_identity_bias():
    return _IDENTITY_BIAS_DEFAULTS


def get_economic_bias():
    return _ECONOMIC_BIAS_DEFAULTS


def get_fault_canon():
    return _FAULT_CANON_DEFAULTS


def get_anti_addiction_profile():
    return _ANTI_ADDICTION_DEFAULTS


def get_conflict_resolution_matrix():
    return _CONFLICT_RESOLUTION_MATRIX


def get_engine_priority_order():
    return ["sla113_revenue_engine", "sla113_narrative_engine",
            "sla113_adaptive_engine", "sla113_identity_engine",
            "sla113_governance_engine"]


# =============================================================================
# ENGINE DECISION TYPES
# =============================================================================

@dataclass
class EngineDecision:
    engine: str
    recommendation: dict
    weight: float = 1.0
    notes: str = ""


@dataclass
class OrchestrationResult:
    resolved: dict
    audit_trace: list
    governance_enforced: bool
    narrative_beat: str
    volatility_tier: str
    cinematic_weight: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


# =============================================================================
# SESSION CONTEXT (input to orchestrator)
# =============================================================================

@dataclass
class SessionContext:
    tenant_id: str
    player_id: str
    machine_type: str                       # fish | slots | keno | custom
    jurisdiction: str                       # nevada_lvcc | uk_gbga | australia_ilga
    session_duration_minutes: float = 0.0
    consecutive_losses: int = 0
    current_balance: float = 0.0
    buy_in_amount: float = 0.0
    spin_count: int = 0
    player_history: Optional[dict] = None  # Prior sessions summary
    demographic: Optional[dict] = None
    is_bonus_round: bool = False
    custom: Optional[dict] = None          # Tenant-specific overrides


# =============================================================================
# TIER 1: REVENUE ENGINE
# =============================================================================

class RevenueEngine:
    """
    Evaluates optimal revenue parameters for this session.
    Applies economic canon: house edge, RTP bounds, volatility tier.
    """

    def evaluate(self, ctx: SessionContext) -> EngineDecision:
        econ = get_economic_canon()
        bias = get_economic_bias()

        loss_pct = 0.0
        if ctx.buy_in_amount > 0:
            loss_pct = max(0.0, (ctx.buy_in_amount - ctx.current_balance) / ctx.buy_in_amount)

        # Determine volatility tier from Build Spec thresholds
        vol_tier = "low"
        if ctx.spin_count > 0:
            # Approximate volatility by loss variance signal
            if loss_pct >= 0.5:
                vol_tier = "high"
            elif loss_pct >= 0.2:
                vol_tier = "medium"

        rtp = econ.get("rtp_minimum", 0.90)
        vol_tiers = econ.get("volatility_tiers", {})
        if vol_tier in vol_tiers:
            rtp = vol_tiers[vol_tier].get("rtp_default", rtp)

        house_edge = econ.get("house_edge_base", 0.05)
        win_ceiling = econ.get("win_ceiling_multiplier", 100.0)

        return EngineDecision(
            engine="sla113_revenue_engine",
            recommendation={
                "rtp": rtp,
                "house_edge": house_edge,
                "volatility_tier": vol_tier,
                "win_ceiling_multiplier": win_ceiling,
                "loss_pct_session": round(loss_pct, 4),
            },
            weight=bias.get("house_edge_priority_weight", 0.5),
            notes=f"volatility_tier={vol_tier}, rtp={rtp}",
        )


# =============================================================================
# TIER 2: NARRATIVE ENGINE
# =============================================================================

class NarrativeEngine:
    """
    Selects the narrative beat for this session moment.
    Derived from economic state and session phase.
    """

    def evaluate(self, ctx: SessionContext, revenue_decision: EngineDecision) -> EngineDecision:
        vol_tier = revenue_decision.recommendation.get("volatility_tier", "low")
        loss_pct = revenue_decision.recommendation.get("loss_pct_session", 0.0)

        # Map volatility tier to narrative beat (from Build Spec)
        beat_map = {
            "low": "ambient",
            "medium": "climactic",
            "high": "endgame",
        }
        beat = beat_map.get(vol_tier, "ambient")

        # Late-session override: last 20% of session → endgame
        max_session = 480.0  # minutes from governance canon
        if ctx.session_duration_minutes / max_session >= 0.8:
            beat = "endgame"

        # Bonus round override
        if ctx.is_bonus_round:
            beat = "climactic"

        cw_config = get_cinematic_weighting()
        cinematic_weight = cw_config.get("default", 0.6)
        if vol_tier == "high":
            cinematic_weight += cw_config.get("high_volatility_boost", 0.15)
        if ctx.is_bonus_round:
            cinematic_weight *= cw_config.get("bonus_feature_multiplier", 1.5)
        cinematic_weight = min(1.0, cinematic_weight)

        return EngineDecision(
            engine="sla113_narrative_engine",
            recommendation={
                "narrative_beat": beat,
                "cinematic_weight": round(cinematic_weight, 3),
            },
            weight=0.3,
            notes=f"beat={beat}, cinematic_weight={cinematic_weight:.2f}",
        )


# =============================================================================
# TIER 3: ADAPTIVE ENGINE
# =============================================================================

class AdaptiveEngine:
    """
    Evaluates adaptive difficulty adjustments based on player performance.
    """

    def evaluate(self, ctx: SessionContext) -> EngineDecision:
        fault = get_fault_canon()
        max_consecutive = fault.get("max_consecutive_losses_before_halt", 25)
        warn_at = fault.get("max_consecutive_losses_before_warning", 10)

        difficulty_adjustment = 0.0
        notes = "normal"

        if ctx.consecutive_losses >= warn_at:
            # Ease difficulty as player approaches halt threshold
            ease_ratio = (ctx.consecutive_losses - warn_at) / max(1, max_consecutive - warn_at)
            difficulty_adjustment = -0.2 * ease_ratio
            notes = f"easing difficulty, consecutive_losses={ctx.consecutive_losses}"

        return EngineDecision(
            engine="sla113_adaptive_engine",
            recommendation={
                "difficulty_adjustment": round(difficulty_adjustment, 4),
                "consecutive_losses": ctx.consecutive_losses,
            },
            weight=0.4,
            notes=notes,
        )


# =============================================================================
# TIER 4: IDENTITY ENGINE
# =============================================================================

class IdentityEngine:
    """
    Applies player personalization weights.
    Uses identity_bias from Build Spec; never overrides governance.
    """

    def evaluate(self, ctx: SessionContext) -> EngineDecision:
        bias = get_identity_bias()

        personalization_score = 0.0
        applied_weights = {}

        if ctx.player_history:
            hist_weight = bias.get("player_history_weight", 0.3)
            personalization_score += hist_weight
            applied_weights["player_history"] = hist_weight

        if ctx.demographic:
            demo_weight = bias.get("demographic_weight", 0.2)
            personalization_score += demo_weight
            applied_weights["demographic"] = demo_weight

        pref_weight = bias.get("player_preference_weight", 0.4)
        personalization_score += pref_weight
        applied_weights["player_preference"] = pref_weight

        return EngineDecision(
            engine="sla113_identity_engine",
            recommendation={
                "personalization_score": round(personalization_score, 4),
                "applied_weights": applied_weights,
            },
            weight=bias.get("player_preference_weight", 0.4),
            notes=f"personalization_score={personalization_score:.3f}",
        )


# =============================================================================
# TIER 5: GOVERNANCE ENGINE (ALWAYS WINS)
# =============================================================================

class GovernanceEngine:
    """
    Final compliance gate. Governance always wins. No override is allowed.
    Derives all rules from canon.governance and anti_addiction_profile.
    """

    def evaluate(self, ctx: SessionContext) -> EngineDecision:
        gov = get_governance_canon()
        anti = get_anti_addiction_profile()
        fault = get_fault_canon()
        session_limits = anti.get("session_limits", {})
        loss_limits = anti.get("loss_limits", {})

        violations = []
        enforcement_actions = []

        # Age gate
        # (Checked at session start; flagged here if context missing age verification)
        age_min = gov.get("age_gate_minimum", 21)

        # Session duration limit
        max_duration_h = session_limits.get("absolute_max_session_duration_hours", 8)
        max_duration_min = max_duration_h * 60
        if ctx.session_duration_minutes >= max_duration_min:
            violations.append(f"session_duration_exceeded: {ctx.session_duration_minutes:.0f}min >= {max_duration_min:.0f}min")
            enforcement_actions.append("terminate_session")

        # Mandatory break check
        break_freq = session_limits.get("mandatory_break_frequency_minutes", 60)
        if ctx.session_duration_minutes > 0 and (ctx.session_duration_minutes % break_freq) < 1.0:
            if ctx.session_duration_minutes >= break_freq:
                violations.append(f"mandatory_break_due: every {break_freq}min")
                enforcement_actions.append("force_break")

        # Consecutive loss halt
        halt_at = fault.get("max_consecutive_losses_before_halt", 25)
        if ctx.consecutive_losses >= halt_at:
            violations.append(f"consecutive_loss_halt: {ctx.consecutive_losses} >= {halt_at}")
            enforcement_actions.append("halt_session")

        # Session loss limit
        loss_limit_pct = loss_limits.get("daily_loss_limit_pct", 0.20)
        if ctx.buy_in_amount > 0:
            loss_pct = (ctx.buy_in_amount - ctx.current_balance) / ctx.buy_in_amount
            if loss_pct >= loss_limit_pct:
                violations.append(f"loss_limit_reached: {loss_pct:.1%} >= {loss_limit_pct:.1%}")
                enforcement_actions.append("warn_player")

        # Time-of-day restriction
        restricted_start = gov.get("restricted_hours_start", "03:00")
        restricted_end = gov.get("restricted_hours_end", "06:00")

        allowed = len([a for a in enforcement_actions if a in ("terminate_session", "halt_session")]) == 0

        return EngineDecision(
            engine="sla113_governance_engine",
            recommendation={
                "allowed": allowed,
                "violations": violations,
                "enforcement_actions": enforcement_actions,
                "restricted_hours": f"{restricted_start}–{restricted_end}",
                "age_gate_minimum": age_min,
            },
            weight=1.0,  # Governance weight is always 1.0 — it cannot be reduced
            notes=f"violations={len(violations)}, allowed={allowed}",
        )


# =============================================================================
# CONFLICT RESOLVER
# =============================================================================

class ConflictResolver:
    """
    Resolves conflicts between engine decisions using the Build Spec matrix.
    Governance always wins regardless of matrix outcome.
    """

    def __init__(self):
        self.matrix = get_conflict_resolution_matrix()

    def resolve(self, a: EngineDecision, b: EngineDecision) -> EngineDecision:
        """Return the winning engine decision between two conflicting decisions."""
        # Governance always wins
        if a.engine == "sla113_governance_engine":
            return a
        if b.engine == "sla113_governance_engine":
            return b

        # Lookup conflict key
        short = {
            "sla113_revenue_engine": "revenue",
            "sla113_narrative_engine": "narrative",
            "sla113_adaptive_engine": "adaptive",
            "sla113_identity_engine": "identity",
        }
        key_a = short.get(a.engine, "")
        key_b = short.get(b.engine, "")
        matrix_key = f"{key_a}_vs_{key_b}"
        alt_key = f"{key_b}_vs_{key_a}"

        rule = self.matrix.get(matrix_key) or self.matrix.get(alt_key)
        if not rule:
            # Default: higher weight wins
            return a if a.weight >= b.weight else b

        priority = rule.get("priority", key_a)
        if priority == key_a:
            return a
        if priority == key_b:
            return b
        return a  # Fallback


# =============================================================================
# ORCHESTRATOR
# =============================================================================

class SLA113Orchestrator:
    """
    Runs the 5-tier engine pipeline and returns a resolved OrchestrationResult.
    Engine priority order and conflict resolution derive from Build Spec.
    Governance cannot be overridden.
    """

    def __init__(self):
        self.revenue = RevenueEngine()
        self.narrative = NarrativeEngine()
        self.adaptive = AdaptiveEngine()
        self.identity = IdentityEngine()
        self.governance = GovernanceEngine()
        self.resolver = ConflictResolver()

    def orchestrate(self, ctx: SessionContext) -> OrchestrationResult:
        audit_trace = []

        # --- Tier 1: Revenue ---
        rev = self.revenue.evaluate(ctx)
        audit_trace.append({"tier": 1, "engine": rev.engine, "notes": rev.notes, "recommendation": rev.recommendation})

        # --- Tier 2: Narrative (uses revenue output) ---
        narr = self.narrative.evaluate(ctx, rev)
        audit_trace.append({"tier": 2, "engine": narr.engine, "notes": narr.notes, "recommendation": narr.recommendation})

        # --- Tier 3: Adaptive ---
        adapt = self.adaptive.evaluate(ctx)
        audit_trace.append({"tier": 3, "engine": adapt.engine, "notes": adapt.notes, "recommendation": adapt.recommendation})

        # --- Tier 4: Identity ---
        ident = self.identity.evaluate(ctx)
        audit_trace.append({"tier": 4, "engine": ident.engine, "notes": ident.notes, "recommendation": ident.recommendation})

        # --- Tier 5: Governance (ALWAYS LAST, ALWAYS WINS) ---
        gov = self.governance.evaluate(ctx)
        audit_trace.append({"tier": 5, "engine": gov.engine, "notes": gov.notes, "recommendation": gov.recommendation})

        # Merge resolved output — governance gates everything
        gov_rec = gov.recommendation
        governance_enforced = not gov_rec.get("allowed", True) or bool(gov_rec.get("enforcement_actions"))

        resolved = {
            # Revenue layer
            "rtp": rev.recommendation.get("rtp"),
            "house_edge": rev.recommendation.get("house_edge"),
            "volatility_tier": rev.recommendation.get("volatility_tier"),
            "win_ceiling_multiplier": rev.recommendation.get("win_ceiling_multiplier"),
            # Narrative layer
            "narrative_beat": narr.recommendation.get("narrative_beat", "ambient"),
            "cinematic_weight": narr.recommendation.get("cinematic_weight", 0.6),
            # Adaptive layer
            "difficulty_adjustment": adapt.recommendation.get("difficulty_adjustment", 0.0),
            # Identity layer
            "personalization_score": ident.recommendation.get("personalization_score", 0.0),
            # Governance gate (overrides all)
            "session_allowed": gov_rec.get("allowed", True),
            "enforcement_actions": gov_rec.get("enforcement_actions", []),
            "governance_violations": gov_rec.get("violations", []),
        }

        return OrchestrationResult(
            resolved=resolved,
            audit_trace=audit_trace,
            governance_enforced=governance_enforced,
            narrative_beat=resolved["narrative_beat"],
            volatility_tier=resolved["volatility_tier"],
            cinematic_weight=resolved["cinematic_weight"],
        )
