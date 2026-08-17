"""End-to-end Economic Truth lifecycle and Receipt Graph service."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Mapping, Optional

from .domain import ActionState, ALLOWED_TRANSITIONS, EconomicTruthError, canonical_json, digest


REQUIRED_SURFACES = (
    ("fable.intent.authorization", "FABLE-5", "authorization"),
    ("sla113.execution", "SLA113", "execution"),
    ("archisynapse.payment", "Archisynapse", "payment"),
    ("archisynapse.ledger", "Archisynapse", "ledger"),
    ("archisynapse.stripe", "Archisynapse", "settlement"),
    ("archisynapse.reversal", "Archisynapse", "reversal"),
    ("lyrica.vics", "Lyrica 3", "provenance"),
    ("lyrica.royalty", "Lyrica 3", "royalty"),
    ("trust.key-rotation", "SLA113", "key_rotation"),
    ("trust.key-revocation", "SLA113", "key_revocation"),
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class EconomicTruthService:
    def __init__(self, store, signer) -> None:
        self.store = store
        self.signer = signer

    async def initialize(self) -> None:
        await self.store.initialize()
        for surface_id, owner, event_type in REQUIRED_SURFACES:
            await self.store.upsert_surface({
                "surface_id": surface_id,
                "owner": owner,
                "event_type": event_type,
                "contract_version": "empire1.economic-event.v1",
                "implemented": True,
                "enabled": True,
                "updated_at": now_iso(),
            })

    async def _issue_receipt(
        self,
        action: dict[str, Any],
        receipt_type: str,
        evidence: Mapping[str, Any],
        parent_receipt_ids: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        latest = await self.store.latest_receipt(action["organization_id"])
        parents = sorted(set((parent_receipt_ids or []) + action.get("receipt_ids", [])[-1:]))
        payload = {
            "schema": "empire1.economic-receipt.v1",
            "receipt_id": f"er_{uuid.uuid4().hex}",
            "receipt_type": receipt_type,
            "action_id": action["action_id"],
            "action_type": action["action_type"],
            "organization_id": action["organization_id"],
            "actor_id": action["actor_id"],
            "charter_id": action["charter_id"],
            "policy_id": action["policy_id"],
            "intent_token_id": action.get("intent_token_id"),
            "idempotency_key": action["idempotency_key"],
            "state": action["state"],
            "target_hash": digest(action.get("target", {})),
            "economic_value": action.get("economic_value", {}),
            "evidence": dict(evidence),
            "evidence_hash": digest(dict(evidence)),
            "parent_receipt_ids": parents,
            "previous_receipt_hash": latest.get("payload_hash") if latest else None,
            "issued_at": now_iso(),
            "key_id": self.signer.key_id,
            "signature_algorithm": self.signer.algorithm,
        }
        payload_hash = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
        receipt = {**payload, "payload_hash": payload_hash, "signature": await self.signer.sign_digest(payload_hash)}
        await self.store.save_receipt(receipt)
        action.setdefault("receipt_ids", []).append(receipt["receipt_id"])
        return receipt

    async def propose(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        required = ("action_type", "organization_id", "actor_id", "charter_id", "policy_id", "idempotency_key")
        missing = [key for key in required if not str(payload.get(key, "")).strip()]
        if missing:
            raise EconomicTruthError(f"Missing economic authority: {', '.join(missing)}")
        action = {
            "action_id": str(payload.get("action_id") or f"eact_{uuid.uuid4().hex}"),
            "action_type": str(payload["action_type"]),
            "organization_id": str(payload["organization_id"]),
            "actor_id": str(payload["actor_id"]),
            "charter_id": str(payload["charter_id"]),
            "policy_id": str(payload["policy_id"]),
            "intent_token_id": payload.get("intent_token_id"),
            "idempotency_key": str(payload["idempotency_key"]),
            "target": dict(payload.get("target") or {}),
            "economic_value": dict(payload.get("economic_value") or {}),
            "state": ActionState.PROPOSED.value,
            "receipt_ids": [],
            "created_at": now_iso(),
            "updated_at": now_iso(),
        }
        stored = await self.store.create_action(action)
        if stored.get("receipt_ids"):
            return {"action": stored, "receipt": await self.store.get_receipt(stored["receipt_ids"][0]), "replayed": True}
        receipt = await self._issue_receipt(stored, "proposal", payload.get("evidence") or {"proposal_recorded": True})
        await self.store.save_action(stored)
        return {"action": stored, "receipt": receipt, "replayed": False}

    async def authorize(self, action_id: str, authorization: Mapping[str, Any]) -> dict[str, Any]:
        action = await self._require_action(action_id)
        if action["state"] != ActionState.PROPOSED.value:
            if action["state"] == ActionState.AUTHORIZED.value:
                return {"action": action, "receipt": await self.store.get_receipt(action["receipt_ids"][-1]), "replayed": True}
            raise EconomicTruthError(f"Cannot authorize action in {action['state']}")
        if not authorization.get("allowed"):
            return await self.refuse(action_id, authorization)
        required = ("charter_verified", "policy_verified", "authorized_by")
        if any(not authorization.get(key) for key in required):
            raise EconomicTruthError("Authorization requires verified charter, policy, and authorizing actor")
        action["state"] = ActionState.AUTHORIZED.value
        action["updated_at"] = now_iso()
        receipt = await self._issue_receipt(action, "authorization", authorization)
        await self.store.save_action(action)
        return {"action": action, "receipt": receipt, "replayed": False}

    async def record_outcome(self, action_id: str, evidence: Mapping[str, Any], *, refused: bool = False) -> dict[str, Any]:
        action = await self._require_action(action_id)
        allowed = {ActionState.PROPOSED.value, ActionState.AUTHORIZED.value} if refused else {ActionState.AUTHORIZED.value}
        if action["state"] not in allowed:
            if action["state"] == ActionState.RECEIPTED.value:
                return {"action": action, "receipt": await self.store.get_receipt(action["receipt_ids"][-1]), "replayed": True}
            raise EconomicTruthError(f"Outcome refused from state {action['state']}")
        if not evidence or not evidence.get("source") or not evidence.get("external_id"):
            raise EconomicTruthError("Outcome requires source and external_id evidence")
        existing_action_id = await self.store.claim_external_event(
            str(evidence["source"]), str(evidence["external_id"]), action_id
        )
        if existing_action_id and existing_action_id != action_id:
            raise EconomicTruthError("External event is already bound to another action")
        action["state"] = ActionState.REFUSED.value if refused else ActionState.EXECUTED.value
        action["updated_at"] = now_iso()
        receipt = await self._issue_receipt(
            action,
            "refusal" if refused else "execution",
            evidence,
            list(evidence.get("parent_receipt_ids") or []),
        )
        action["state"] = ActionState.RECEIPTED.value
        action["updated_at"] = now_iso()
        await self.store.save_action(action)
        return {"action": action, "receipt": receipt, "replayed": bool(existing_action_id)}

    async def refuse(self, action_id: str, evidence: Mapping[str, Any]) -> dict[str, Any]:
        enriched = {"source": "fable-5", "external_id": f"refusal:{action_id}", **dict(evidence)}
        return await self.record_outcome(action_id, enriched, refused=True)

    async def verify(self, action_id: str, verification: Mapping[str, Any]) -> dict[str, Any]:
        action = await self._require_action(action_id)
        if action["state"] == ActionState.VERIFIED.value:
            return {"action": action, "receipt": await self.store.get_receipt(action["receipt_ids"][-1]), "replayed": True}
        if action["state"] != ActionState.RECEIPTED.value:
            raise EconomicTruthError("Verification requires a receipted outcome")
        if not verification.get("independent") or not verification.get("verified_by"):
            raise EconomicTruthError("Independent verifier identity is required")
        for receipt_id in action["receipt_ids"]:
            receipt = await self.store.get_receipt(receipt_id)
            if not receipt or not await self.verify_envelope(receipt):
                raise EconomicTruthError(f"Receipt signature verification failed: {receipt_id}")
        action["state"] = ActionState.VERIFIED.value
        action["updated_at"] = now_iso()
        receipt = await self._issue_receipt(action, "verification", verification)
        await self.store.save_action(action)
        return {"action": action, "receipt": receipt, "replayed": False}

    async def reverse(self, action_id: str, reversal: Mapping[str, Any]) -> dict[str, Any]:
        action = await self._require_action(action_id)
        if action["state"] == ActionState.REVERSED.value:
            return {"action": action, "receipt": await self.store.get_receipt(action["receipt_ids"][-1]), "replayed": True}
        if action["state"] not in {ActionState.RECEIPTED.value, ActionState.VERIFIED.value}:
            raise EconomicTruthError("Only a receipted or verified action can be reversed")
        if not reversal.get("reason") or not reversal.get("external_id"):
            raise EconomicTruthError("Reversal requires reason and external_id")
        prior = action["state"]
        action["state"] = ActionState.REVERSED.value
        action["updated_at"] = now_iso()
        receipt = await self._issue_receipt(action, "reversal", {"source_state": prior, **dict(reversal)})
        await self.store.save_action(action)
        return {"action": action, "receipt": receipt, "replayed": False}

    async def verify_envelope(self, receipt: Mapping[str, Any]) -> bool:
        payload = {k: v for k, v in receipt.items() if k not in {"payload_hash", "signature"}}
        expected = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
        if expected != receipt.get("payload_hash"):
            return False
        return await self.signer.verify_digest(expected, str(receipt.get("signature", "")))

    async def graph(self, organization_id: str) -> dict[str, Any]:
        receipts = await self.store.list_receipts(organization_id)
        nodes = [{"id": r["receipt_id"], "type": r["receipt_type"], "state": r["state"], "action_id": r["action_id"], "issued_at": r["issued_at"]} for r in receipts]
        edges = []
        by_hash = {r["payload_hash"]: r["receipt_id"] for r in receipts}
        for receipt in receipts:
            for parent in receipt.get("parent_receipt_ids", []):
                edges.append({"from": parent, "to": receipt["receipt_id"], "kind": "caused"})
            previous = by_hash.get(receipt.get("previous_receipt_hash"))
            if previous:
                edges.append({"from": previous, "to": receipt["receipt_id"], "kind": "chained"})
        return {"organization_id": organization_id, "nodes": nodes, "edges": edges}

    async def metrics(self, organization_id: str) -> dict[str, Any]:
        receipts = await self.store.list_receipts(organization_id)
        counts: dict[str, int] = {}
        value_by_currency: dict[str, float] = {}
        for receipt in receipts:
            counts[receipt["receipt_type"]] = counts.get(receipt["receipt_type"], 0) + 1
            value = receipt.get("economic_value") or {}
            if receipt["receipt_type"] == "execution" and value.get("amount") is not None:
                currency = str(value.get("currency", "UNKNOWN"))
                value_by_currency[currency] = value_by_currency.get(currency, 0.0) + float(value["amount"])
        return {"receipts_issued": len(receipts), "by_type": counts, "economic_value_covered": value_by_currency}

    async def coverage(self) -> dict[str, Any]:
        surfaces = await self.store.list_surfaces()
        uncovered = [s["surface_id"] for s in surfaces if not (s.get("implemented") and s.get("enabled"))]
        required_ids = {item[0] for item in REQUIRED_SURFACES}
        present = {s["surface_id"] for s in surfaces}
        uncovered.extend(sorted(required_ids - present))
        total = len(required_ids)
        covered = total - len(set(uncovered))
        return {
            "total_surfaces": total,
            "governed_surfaces": covered,
            "coverage_percent": round(100 * covered / total, 2),
            "uncovered_surfaces": sorted(set(uncovered)),
            "claim_allowed": covered == total,
            "contract_version": "empire1.economic-event.v1",
        }

    async def _require_action(self, action_id: str) -> dict[str, Any]:
        action = await self.store.get_action(action_id)
        if not action:
            raise EconomicTruthError("Economic action not found")
        return action
