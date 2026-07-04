"""
SLA113 Regulatory Profile Enforcer
Applies jurisdiction-specific rules from SLA113_BUILD_SPEC.yaml regulatory_profiles.
Supported jurisdictions: nevada_lvcc | uk_gbga | australia_ilga
"""

from dataclasses import dataclass
from typing import Optional

# Regulatory profiles — defaults from SLA113_BUILD_SPEC.yaml
_REGULATORY_PROFILES = {
    "nevada_lvcc": {
        "jurisdiction": "nevada_lvcc",
        "min_rtp": 0.85,
        "max_rtp": 0.99,
        "age_gate_minimum": 21,
        "betting_limits": {"min_bet": 0.01, "max_bet": 500.00},
        "session_time_limit_minutes": 480,
        "responsible_gaming": {
            "loss_limit_per_session_pct": 0.50,
            "session_break_frequency_minutes": 120,
        },
        "tax_rate_pct": 6.75,
    },
    "uk_gbga": {
        "jurisdiction": "uk_gbga",
        "min_rtp": 0.85,
        "max_rtp": 0.99,
        "age_gate_minimum": 18,
        "betting_limits": {"min_bet": 0.01, "max_bet": 250.00},
        "session_time_limit_minutes": 360,
        "responsible_gaming": {
            "loss_limit_per_session_pct": 0.40,
            "loss_limit_daily_pct": 0.50,
            "session_break_frequency_minutes": 90,
        },
        "tax_rate_pct": 15.0,
    },
    "australia_ilga": {
        "jurisdiction": "australia_ilga",
        "min_rtp": 0.87,
        "max_rtp": 0.99,
        "age_gate_minimum": 18,
        "betting_limits": {"min_bet": 0.01, "max_bet": 1000.00},
        "session_time_limit_minutes": 240,
        "responsible_gaming": {
            "loss_limit_per_session_pct": 0.30,
            "loss_limit_weekly_pct": 0.40,
            "session_break_frequency_minutes": 60,
        },
        "tax_rate_pct": 10.0,
    },
}


def get_regulatory_profile(jurisdiction: str) -> dict:
    return _REGULATORY_PROFILES.get(jurisdiction, {})


def get_all_regulatory_profiles() -> dict:
    return _REGULATORY_PROFILES


@dataclass
class RegulatoryValidationResult:
    jurisdiction: str
    compliant: bool
    violations: list
    warnings: list
    profile_summary: dict


class SLA113RegulatoryEnforcer:
    """
    Validates a session context against the regulatory profile for a given jurisdiction.
    All rules derived strictly from Build Spec regulatory_profiles section.
    """

    def get_profile(self, jurisdiction: str) -> Optional[dict]:
        """Return regulatory profile for jurisdiction. Returns None if unknown."""
        return get_regulatory_profile(jurisdiction)

    def validate(
        self,
        jurisdiction: str,
        rtp: float,
        bet_amount: float,
        session_duration_minutes: float,
        player_age: Optional[int] = None,
        session_loss_pct: float = 0.0,
        daily_loss_pct: float = 0.0,
    ) -> RegulatoryValidationResult:
        """
        Validate session parameters against jurisdiction regulatory profile.

        Args:
            jurisdiction: 'nevada_lvcc' | 'uk_gbga' | 'australia_ilga'
            rtp: Current configured RTP (e.g. 0.95)
            bet_amount: Current bet amount in currency units
            session_duration_minutes: Current session duration in minutes
            player_age: Player age (None if not provided)
            session_loss_pct: Fraction of buy-in lost this session (0.0–1.0)
            daily_loss_pct: Fraction of balance lost today (0.0–1.0)

        Returns:
            RegulatoryValidationResult with compliant status and violation list
        """
        profile = get_regulatory_profile(jurisdiction)
        if not profile:
            return RegulatoryValidationResult(
                jurisdiction=jurisdiction,
                compliant=False,
                violations=[f"unknown_jurisdiction: {jurisdiction}"],
                warnings=[],
                profile_summary={},
            )

        violations = []
        warnings = []

        # RTP bounds
        min_rtp = profile.get("min_rtp", 0.85)
        max_rtp = profile.get("max_rtp", 0.99)
        if rtp < min_rtp:
            violations.append(f"rtp_below_minimum: {rtp:.3f} < {min_rtp:.3f}")
        if rtp > max_rtp:
            violations.append(f"rtp_above_maximum: {rtp:.3f} > {max_rtp:.3f}")

        # Age gate
        age_min = profile.get("age_gate_minimum", 21)
        if player_age is not None and player_age < age_min:
            violations.append(f"age_below_minimum: {player_age} < {age_min}")

        # Betting limits
        betting = profile.get("betting_limits", {})
        min_bet = betting.get("min_bet", 0.01)
        max_bet = betting.get("max_bet", 500.00)
        if bet_amount < min_bet:
            violations.append(f"bet_below_minimum: {bet_amount} < {min_bet}")
        if bet_amount > max_bet:
            violations.append(f"bet_above_maximum: {bet_amount} > {max_bet}")

        # Session time limit
        session_limit_min = profile.get("session_time_limit_minutes", 480)
        if session_duration_minutes > session_limit_min:
            violations.append(f"session_duration_exceeded: {session_duration_minutes:.0f}min > {session_limit_min}min")

        # Responsible gaming: session loss limit
        rg = profile.get("responsible_gaming", {})
        session_loss_limit = rg.get("loss_limit_per_session_pct", 0.50)
        if session_loss_pct >= session_loss_limit:
            violations.append(f"session_loss_limit_reached: {session_loss_pct:.1%} >= {session_loss_limit:.1%}")

        # Responsible gaming: daily loss limit
        daily_loss_limit = rg.get("loss_limit_daily_pct") or rg.get("loss_limit_weekly_pct")
        if daily_loss_limit and daily_loss_pct >= daily_loss_limit:
            warnings.append(f"daily_loss_limit_approaching: {daily_loss_pct:.1%} >= {daily_loss_limit:.1%}")

        # Break frequency warning
        break_freq = rg.get("session_break_frequency_minutes", 120)
        if session_duration_minutes >= break_freq:
            minutes_since_break = session_duration_minutes % break_freq
            if minutes_since_break < 2.0:
                warnings.append(f"mandatory_break_due: every {break_freq}min")

        return RegulatoryValidationResult(
            jurisdiction=jurisdiction,
            compliant=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            profile_summary={
                "jurisdiction": profile.get("jurisdiction"),
                "min_rtp": min_rtp,
                "max_rtp": max_rtp,
                "age_gate_minimum": age_min,
                "min_bet": min_bet,
                "max_bet": max_bet,
                "session_time_limit_minutes": session_limit_min,
                "tax_rate_pct": profile.get("tax_rate_pct"),
            },
        )
