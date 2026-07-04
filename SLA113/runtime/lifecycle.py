"""Capability pack lifecycle manager.

Lifecycle states:
  scaffold     → Initial skeleton, not functional
  development → Active development, may be unstable
  testing     → Under test, stability improving
  active      → Production-ready, available for use
  deprecated  → No longer maintained, may be removed
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


LIFECYCLE_ORDER = ["scaffold", "development", "testing", "active", "deprecated"]


def is_valid_transition(current: str, target: str) -> bool:
    if current not in LIFECYCLE_ORDER or target not in LIFECYCLE_ORDER:
        return False
    if current == "deprecated":
        return False
    return LIFECYCLE_ORDER.index(target) >= LIFECYCLE_ORDER.index(current)


@dataclass
class LifecycleState:
    state: str = "scaffold"
    transitions: List[Dict[str, str]] = field(default_factory=list)
    version: str = "0.1.0"

    def transition_to(self, target: str, reason: str = "") -> bool:
        if not is_valid_transition(self.state, target):
            return False
        self.transitions.append({
            "from": self.state,
            "to": target,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        self.state = target
        return True

    def can_be_used(self) -> bool:
        return self.state in ("active", "testing")

    def summary(self) -> Dict[str, Any]:
        return {
            "current_state": self.state,
            "version": self.version,
            "transition_count": len(self.transitions),
            "last_transition": self.transitions[-1] if self.transitions else None,
        }


class LifecycleManager:
    """Manages lifecycle for all capability packs."""

    def __init__(self):
        self._states: Dict[str, LifecycleState] = {}

    def register(self, pack_name: str, initial_state: str = "scaffold", version: str = "0.1.0"):
        self._states[pack_name] = LifecycleState(
            state=initial_state,
            version=version,
        )

    def promote(self, pack_name: str, target: str, reason: str = "") -> bool:
        state = self._states.get(pack_name)
        if not state:
            return False
        return state.transition_to(target, reason)

    def can_use(self, pack_name: str) -> bool:
        state = self._states.get(pack_name)
        if not state:
            return False
        return state.can_be_used()

    def get_state(self, pack_name: str) -> Optional[LifecycleState]:
        return self._states.get(pack_name)

    def all_states(self) -> Dict[str, LifecycleState]:
        return dict(self._states)

    def summary(self) -> Dict[str, str]:
        return {name: s.state for name, s in self._states.items()}
