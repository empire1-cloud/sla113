import copy
import unittest

from economic_truth import (
    ActionState,
    CoverageRegistry,
    EconomicAction,
    EconomicSurface,
    EconomicTruthError,
    verify_receipt,
)


def action(**changes):
    values = {
        "action_type": "payment.creator_payout",
        "organization_id": "empire1",
        "actor_id": "sla113",
        "charter_id": "charter_v1",
        "policy_id": "royalty_policy_v1",
        "idempotency_key": "payout_track_123",
        "target": {"creator_id": "creator_1"},
        "economic_value": {"amount": "1.25", "currency": "USD"},
        "inputs": {"soulprint_match": 0.9844},
    }
    values.update(changes)
    return EconomicAction(**values)


class EconomicTruthTests(unittest.TestCase):
    def test_skipped_gate_is_refused(self):
        with self.assertRaises(EconomicTruthError):
            action().transition(ActionState.EXECUTED, {"provider_id": "x"})

    def test_missing_authority_is_refused(self):
        with self.assertRaises(EconomicTruthError):
            action(charter_id="")

    def test_executed_receipt_verifies_and_tampering_fails(self):
        governed = action()
        governed.transition(ActionState.AUTHORIZED)
        governed.transition(ActionState.EXECUTED, {"provider_id": "po_123", "status": "paid"})
        receipt = governed.receipt(b"test-signing-key")
        self.assertTrue(verify_receipt(receipt, b"test-signing-key"))
        altered = copy.deepcopy(receipt)
        altered["economic_value"]["amount"] = "1250.00"
        self.assertFalse(verify_receipt(altered, b"test-signing-key"))

    def test_refusal_is_preserved_as_receipt(self):
        governed = action()
        governed.transition(ActionState.REFUSED, {"reason": "fraud_threshold", "fraud_score": 100})
        receipt = governed.receipt(b"test-signing-key")
        self.assertEqual("REFUSED", receipt["outcome"])
        self.assertTrue(verify_receipt(receipt, b"test-signing-key"))

    def test_receipt_chain_detects_reordering(self):
        first = action(idempotency_key="first")
        first.transition(ActionState.AUTHORIZED)
        first.transition(ActionState.EXECUTED, {"provider_id": "one"})
        first_receipt = first.receipt(b"key")
        second = action(idempotency_key="second")
        second.transition(ActionState.AUTHORIZED)
        second.transition(ActionState.EXECUTED, {"provider_id": "two"})
        second_receipt = second.receipt(b"key", first_receipt["payload_hash"])
        self.assertEqual(first_receipt["payload_hash"], second_receipt["previous_receipt_hash"])

    def test_receipt_records_causal_parents(self):
        governed = action(parent_receipt_ids=("er_authorization", "er_proposal", "er_authorization"))
        governed.transition(ActionState.AUTHORIZED)
        governed.transition(ActionState.EXECUTED, {"provider_id": "three"})
        receipt = governed.receipt(b"key")
        self.assertEqual(["er_authorization", "er_proposal"], receipt["parent_receipt_ids"])

    def test_marketing_claim_requires_complete_registered_coverage(self):
        registry = CoverageRegistry([
            EconomicSurface("stripe.checkout", "payment.checkout", True, "billing"),
            EconomicSurface("crm.discount", "contract.discount", False, "crm"),
        ])
        self.assertFalse(registry.report()["claim_allowed"])
        with self.assertRaises(RuntimeError):
            registry.assert_complete()
        registry.register(EconomicSurface("crm.discount", "contract.discount", True, "crm"))
        self.assertTrue(registry.report()["claim_allowed"])


if __name__ == "__main__":
    unittest.main()
