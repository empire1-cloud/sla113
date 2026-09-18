"""Fail-closed economic action state machine and verifiable receipt primitives."""

from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any, Mapping, Optional


class EconomicTruthError(ValueError):
    pass


class ActionState(str, Enum):
    PROPOSED = "PROPOSED"
    AUTHORIZED = "AUTHORIZED"
    EXECUTED = "EXECUTED"
    REFUSED = "REFUSED"
    RECEIPTED = "RECEIPTED"
    VERIFIED = "VERIFIED"
    REVERSED = "REVERSED"


ALLOWED_TRANSITIONS = {
    ActionState.PROPOSED: {ActionState.AUTHORIZED, ActionState.REFUSED},
    ActionState.AUTHORIZED: {ActionState.EXECUTED, ActionState.REFUSED},
    ActionState.EXECUTED: {ActionState.RECEIPTED},
    ActionState.REFUSED: {ActionState.RECEIPTED},
    ActionState.RECEIPTED: {ActionState.VERIFIED, ActionState.REVERSED},
    ActionState.VERIFIED: {ActionState.REVERSED},
    ActionState.REVERSED: set(),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json_default(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, Enum):
        return value.value
    raise TypeError(f"Unsupported canonical value: {type(value)!r}")


def canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=_json_default)


def digest(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def sign(payload_hash: str, signing_key: bytes) -> str:
    if not signing_key:
        raise EconomicTruthError("A signing key is required; unsigned receipts are refused")
    return hmac.new(signing_key, payload_hash.encode("ascii"), hashlib.sha256).hexdigest()


@dataclass
class EconomicAction:
    action_type: str
    organization_id: str
    actor_id: str
    charter_id: str
    policy_id: str
    idempotency_key: str
    target: Mapping[str, Any]
    economic_value: Mapping[str, Any]
    inputs: Mapping[str, Any] = field(default_factory=dict)
    parent_receipt_ids: tuple[str, ...] = ()
    action_id: str = field(default_factory=lambda: f"eact_{uuid.uuid4().hex}")
    state: ActionState = ActionState.PROPOSED
    created_at: str = field(default_factory=utc_now)
    history: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        required = {
            "action_type": self.action_type,
            "organization_id": self.organization_id,
            "actor_id": self.actor_id,
            "charter_id": self.charter_id,
            "policy_id": self.policy_id,
            "idempotency_key": self.idempotency_key,
        }
        missing = [name for name, value in required.items() if not str(value).strip()]
        if missing:
            raise EconomicTruthError(f"Missing economic action authority: {', '.join(missing)}")
        if not self.history:
            self.history.append({"state": self.state.value, "at": self.created_at})

    def transition(self, next_state: ActionState, evidence: Optional[Mapping[str, Any]] = None) -> None:
        if next_state not in ALLOWED_TRANSITIONS[self.state]:
            raise EconomicTruthError(f"Illegal transition {self.state.value} -> {next_state.value}")
        if next_state in {ActionState.EXECUTED, ActionState.REFUSED, ActionState.REVERSED} and not evidence:
            raise EconomicTruthError(f"{next_state.value} requires evidence")
        self.state = next_state
        event = {"state": next_state.value, "at": utc_now()}
        if evidence:
            event["evidence"] = dict(evidence)
            event["evidence_hash"] = digest(dict(evidence))
        self.history.append(event)

    def receipt(self, signing_key: bytes, previous_receipt_hash: Optional[str] = None) -> dict[str, Any]:
        if self.state not in {ActionState.EXECUTED, ActionState.REFUSED}:
            raise EconomicTruthError("Only an executed or refused action can be receipted")
        outcome_state = self.state.value
        payload = {
            "schema": "empire1.economic-receipt.v1",
            "receipt_id": f"er_{uuid.uuid4().hex}",
            "action_id": self.action_id,
            "action_type": self.action_type,
            "organization_id": self.organization_id,
            "actor_id": self.actor_id,
            "charter_id": self.charter_id,
            "policy_id": self.policy_id,
            "idempotency_key": self.idempotency_key,
            "target_hash": digest(dict(self.target)),
            "economic_value": dict(self.economic_value),
            "inputs_hash": digest(dict(self.inputs)),
            "outcome": outcome_state,
            "history": list(self.history),
            "previous_receipt_hash": previous_receipt_hash,
            "parent_receipt_ids": sorted(set(self.parent_receipt_ids)),
            "issued_at": utc_now(),
        }
        payload_hash = digest(payload)
        envelope = {**payload, "payload_hash": payload_hash, "signature": sign(payload_hash, signing_key)}
        self.transition(ActionState.RECEIPTED)
        return envelope


def verify_receipt(receipt: Mapping[str, Any], signing_key: bytes) -> bool:
    payload = {key: value for key, value in receipt.items() if key not in {"payload_hash", "signature"}}
    expected_hash = digest(payload)
    return hmac.compare_digest(expected_hash, str(receipt.get("payload_hash", ""))) and hmac.compare_digest(
        sign(expected_hash, signing_key), str(receipt.get("signature", ""))
    )
