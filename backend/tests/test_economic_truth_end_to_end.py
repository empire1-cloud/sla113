import copy
import unittest

from economic_truth import DevelopmentHmacSigner, EconomicTruthService, MemoryEconomicTruthStore


class EconomicTruthEndToEndTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.store = MemoryEconomicTruthStore()
        self.service = EconomicTruthService(self.store, DevelopmentHmacSigner(b"x" * 32))
        await self.service.initialize()

    async def test_intent_to_stripe_ledger_vics_verification_and_reversal(self):
        proposed = await self.service.propose({
            "action_type": "creator.royalty_payout",
            "organization_id": "empire1",
            "actor_id": "sla113",
            "charter_id": "empire1-charter-v1",
            "policy_id": "lyrica-royalty-policy-v1",
            "intent_token_id": "it_123",
            "idempotency_key": "royalty_event_123",
            "target": {"creator_id": "creator_1", "track_id": "track_1"},
            "economic_value": {"amount": "1.25", "currency": "USD"},
            "evidence": {"source": "lyrica3", "vics_proof_id": "vics_1"},
        })
        action_id = proposed["action"]["action_id"]
        authorized = await self.service.authorize(action_id, {
            "allowed": True,
            "charter_verified": True,
            "policy_verified": True,
            "authorized_by": "fable-5",
            "intent_token_id": "it_123",
        })
        outcome = await self.service.record_outcome(action_id, {
            "source": "archisynapse",
            "external_id": "stripe_evt_123",
            "stripe_event_id": "stripe_evt_123",
            "ledger_transaction_id": "ledger_123",
            "vics_proof_id": "vics_1",
            "soulprint_hash": "sp_sha256_abc",
            "parent_receipt_ids": [authorized["receipt"]["receipt_id"]],
        })
        verified = await self.service.verify(action_id, {
            "independent": True,
            "verified_by": "empire1-evidence-auditor",
            "checks": {"stripe": True, "ledger_balanced": True, "vics": True},
        })
        reversed_result = await self.service.reverse(action_id, {
            "reason": "creator_requested_refund",
            "external_id": "refund_123",
            "ledger_reversal_id": "ledger_reverse_123",
        })

        self.assertEqual("REVERSED", reversed_result["action"]["state"])
        self.assertTrue(await self.service.verify_envelope(verified["receipt"]))
        graph = await self.service.graph("empire1")
        self.assertEqual(5, len(graph["nodes"]))
        self.assertGreaterEqual(len(graph["edges"]), 4)
        metrics = await self.service.metrics("empire1")
        self.assertEqual(5, metrics["receipts_issued"])
        self.assertEqual(1.25, metrics["economic_value_covered"]["USD"])
        self.assertTrue((await self.service.coverage())["claim_allowed"])

    async def test_duplicate_external_event_cannot_bind_two_actions(self):
        async def make(key):
            p = await self.service.propose({
                "action_type": "payment", "organization_id": "empire1", "actor_id": "sla113",
                "charter_id": "c", "policy_id": "p", "idempotency_key": key,
            })
            aid = p["action"]["action_id"]
            await self.service.authorize(aid, {"allowed": True, "charter_verified": True, "policy_verified": True, "authorized_by": "fable"})
            return aid

        first = await make("first")
        second = await make("second")
        await self.service.record_outcome(first, {"source": "stripe", "external_id": "evt_same"})
        with self.assertRaises(Exception):
            await self.service.record_outcome(second, {"source": "stripe", "external_id": "evt_same"})

    async def test_tamper_breaks_verification(self):
        p = await self.service.propose({
            "action_type": "discount", "organization_id": "empire1", "actor_id": "agent",
            "charter_id": "c", "policy_id": "p", "idempotency_key": "discount-1",
            "economic_value": {"amount": "10", "currency": "USD"},
        })
        altered = copy.deepcopy(p["receipt"])
        altered["economic_value"]["amount"] = "1000"
        self.assertFalse(await self.service.verify_envelope(altered))


if __name__ == "__main__":
    unittest.main()
