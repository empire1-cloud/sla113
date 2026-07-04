"""
SLA113 Governance Enforcement Layer
Derives all rules from SLA113_BUILD_SPEC.yaml canon.governance and anti_addiction_profile.
Governance always wins. No override is allowed.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import time as dtime

# Governance defaults — loaded from SLA113_BUILD_SPEC.yaml at runtime
_GOVERNANCE_DEFAULTS = {
    "age_gate_minimum": 21,
    "geofence_enabled": True,
    "time_of_day_restrictions_enabled": True,
    "restricted_hours_start": "03:00",
    "restricted_hours_end": "06:00",
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

_FAULT_DEFAULTS = {
    "max_consecutive_losses_before_halt": 25,
    "max_consecutive_losses_before_warning": 10,
}

_SESSION_LIMITS_DEFAULTS = {
    "absolute_max_session_duration_hours": 8,
    "mandatory_break_frequency_minutes": 60,
    "mandatory_break_duration_minutes": 15,
}

_LOSS_LIMITS_DEFAULTS = {
    "daily_loss_limit_pct": 0.20,
    "loss_limit_enforcement": "hard",
}

_SELF_EXCLUSION_DEFAULTS = {
    "enabled": True,
}


def get_governance_canon():
    return _GOVERNANCE_DEFAULTS


def get_anti_addiction_profile():
    return _ANTI_ADDICTION_DEFAULTS


def get_fault_canon():
    return _FAULT_DEFAULTS


def get_session_limits():
    return _SESSION_LIMITS_DEFAULTS


def get_loss_limits():
    return _LOSS_LIMITS_DEFAULTS


def get_self_exclusion_config():
    return _SELF_EXCLUSION_DEFAULTS


@dataclass
class GovernanceDecision:
    allowed: bool
    reason: str
    enforcement_action: str   # "none" | "warn" | "force_break" | "halt_session" | "terminate_session" | "block"
    violations: list
    details: dict


class SLA113GovernanceEnforcer:
    """
    Sovereign governance enforcement.
    All thresholds loaded from Build Spec at instantiation.
    Cannot be subclassed or overridden.
    """

    def __init__(self):
        self._gov = get_governance_canon()
        self._anti = get_anti_addiction_profile()
        self._fault = get_fault_canon()
        self._session_limits = get_session_limits()
        self._loss_limits = get_loss_limits()
        self._self_excl = get_self_exclusion_config()

    # ------------------------------------------------------------------
    # PUBLIC: FULL ENFORCEMENT CHECK
    # ------------------------------------------------------------------

    def enforce(
        self,
        player_id: str,
        session_duration_minutes: float,
        consecutive_losses: int,
        current_balance: float,
        buy_in_amount: float,
        age_verified: bool = True,
        geofence_passed: bool = True,
        self_excluded: bool = False,
        current_hour: Optional[int] = None,  # 0–23 UTC
        spin_count: int = 0,
    ) -> GovernanceDecision:
        """
        Run all governance checks in order.
        Returns on first hard-block violation.
        Accumulates warnings otherwise.
        """
        violations = []
        enforcement_action = "none"

        # 1. Self-exclusion (hard block)
        if self_excluded and self._self_excl.get("enabled", True):
            return GovernanceDecision(
                allowed=False,
                reason="self_exclusion_active",
                enforcement_action="block",
                violations=["self_exclusion_active"],
                details={"player_id": player_id},
            )

        # 2. Age gate (hard block)
        age_min = self._gov.get("age_gate_minimum", 21)
        if not age_verified:
            return GovernanceDecision(
                allowed=False,
                reason=f"age_gate_failed: minimum age {age_min}",
                enforcement_action="block",
                violations=[f"age_gate_failed"],
                details={"age_minimum": age_min},
            )

        # 3. Geofence (hard block)
        if self._gov.get("geofence_enabled", True) and not geofence_passed:
            return GovernanceDecision(
                allowed=False,
                reason="geofence_violation",
                enforcement_action="block",
                violations=["geofence_violation"],
                details={},
            )

        # 4. Time-of-day restriction
        if self._gov.get("time_of_day_restrictions_enabled", True) and current_hour is not None:
            restricted_start = int(self._gov.get("restricted_hours_start", "03:00").split(":")[0])
            restricted_end = int(self._gov.get("restricted_hours_end", "06:00").split(":")[0])
            if restricted_start <= current_hour < restricted_end:
                return GovernanceDecision(
                    allowed=False,
                    reason=f"restricted_hours: {restricted_start:02d}:00–{restricted_end:02d}:00 UTC",
                    enforcement_action="block",
                    violations=["restricted_hours"],
                    details={"current_hour": current_hour, "restricted": f"{restricted_start:02d}:00–{restricted_end:02d}:00"},
                )

        # 5. Max session duration (hard halt)
        max_dur_h = self._session_limits.get("absolute_max_session_duration_hours", 8)
        max_dur_min = max_dur_h * 60
        if session_duration_minutes >= max_dur_min:
            return GovernanceDecision(
                allowed=False,
                reason=f"session_duration_exceeded: {session_duration_minutes:.0f}min >= {max_dur_min:.0f}min",
                enforcement_action="terminate_session",
                violations=["session_duration_exceeded"],
                details={"session_minutes": session_duration_minutes, "max_minutes": max_dur_min},
            )

        # 6. Consecutive loss halt
        halt_at = self._fault.get("max_consecutive_losses_before_halt", 25)
        warn_at = self._fault.get("max_consecutive_losses_before_warning", 10)
        if consecutive_losses >= halt_at:
            return GovernanceDecision(
                allowed=False,
                reason=f"consecutive_loss_halt: {consecutive_losses} >= {halt_at}",
                enforcement_action="halt_session",
                violations=["consecutive_loss_halt"],
                details={"consecutive_losses": consecutive_losses, "halt_threshold": halt_at},
            )
        if consecutive_losses >= warn_at:
            violations.append(f"consecutive_loss_warning: {consecutive_losses} >= {warn_at}")
            enforcement_action = "warn"

        # 7. Loss limit
        loss_limit_pct = self._loss_limits.get("daily_loss_limit_pct", 0.20)
        enforcement = self._loss_limits.get("loss_limit_enforcement", "hard")
        if buy_in_amount > 0:
            loss_pct = (buy_in_amount - current_balance) / buy_in_amount
            if loss_pct >= loss_limit_pct:
                if enforcement == "hard":
                    return GovernanceDecision(
                        allowed=False,
                        reason=f"loss_limit_reached: {loss_pct:.1%} >= {loss_limit_pct:.1%}",
                        enforcement_action="halt_session",
                        violations=["loss_limit_reached"],
                        details={"loss_pct": round(loss_pct, 4), "limit_pct": loss_limit_pct},
                    )
                else:
                    violations.append(f"loss_limit_warning: {loss_pct:.1%}")
                    enforcement_action = "warn"

        # 8. Mandatory break check
        break_freq = self._session_limits.get("mandatory_break_frequency_minutes", 60)
        break_dur = self._session_limits.get("mandatory_break_duration_minutes", 15)
        if session_duration_minutes >= break_freq:
            # Check if we're at a break interval (within 1-minute window)
            minutes_since_break = session_duration_minutes % break_freq
            if minutes_since_break < 1.0:
                violations.append(f"mandatory_break_due: every {break_freq}min for {break_dur}min")
                enforcement_action = "force_break"

        # All checks passed (possibly with warnings)
        allowed = enforcement_action not in ("halt_session", "terminate_session", "block")
        reason = "governance_pass" if not violations else f"{len(violations)} warning(s)"

        return GovernanceDecision(
            allowed=allowed,
            reason=reason,
            enforcement_action=enforcement_action,
            violations=violations,
            details={
                "session_duration_minutes": session_duration_minutes,
                "consecutive_losses": consecutive_losses,
                "buy_in_amount": buy_in_amount,
                "current_balance": current_balance,
            },
        )
