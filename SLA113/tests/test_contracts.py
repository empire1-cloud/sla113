"""Contract tests for every capability pack.

Each capability pack (AI, Identity, Storage) must follow the same contract:
  1. Has a CAPABILITY class attribute (string)
  2. Has a register_providers(runtime) method
  3. Can be constructed with no arguments or with a runtime
  4. Public API methods return the expected types
"""

from __future__ import annotations

import unittest
from pathlib import Path

from SLA113.runtime import CapabilityRuntime


class ContractBase:
    """Base mixin that verifies the capability pack contract."""

    PACK_MODULE = None  # Override in subclass

    def test_capability_attribute(self):
        self.assertTrue(hasattr(self.PACK, "CAPABILITY"))
        self.assertIsInstance(self.PACK.CAPABILITY, str)

    def test_register_providers_method(self):
        self.assertTrue(hasattr(self.PACK, "register_providers"))
        self.assertTrue(callable(self.PACK.register_providers))

    def test_construct_no_args(self):
        if self.PACK_MODULE:
            instance = self.PACK_MODULE()
            self.assertIsNotNone(instance)

    def test_register_with_runtime(self):
        rt = CapabilityRuntime()
        instance = self.PACK_MODULE(runtime=rt) if hasattr(self.PACK_MODULE, "__init__") else self.PACK
        if hasattr(instance, "register_providers"):
            instance.register_providers(rt)
            health = rt.health()
            self.assertGreaterEqual(len(health), 1)

    def test_runtime_routes_to_provider(self):
        rt = CapabilityRuntime()
        instance = self.PACK_MODULE(runtime=rt) if hasattr(self.PACK_MODULE, "__init__") else self.PACK
        if hasattr(instance, "register_providers"):
            instance.register_providers(rt)
            provider = rt.router.select(instance.CAPABILITY)
            if provider:
                self.assertEqual(provider.lifecycle, "active")


class TestAIContract(unittest.TestCase, ContractBase):
    PACK_MODULE = None

    @classmethod
    def setUpClass(cls):
        from SLA113.capabilities.ai import AIRouter
        cls.PACK = cls.PACK_MODULE = AIRouter

    def setUp(self):
        from SLA113.runtime import CapabilityRuntime
        rt = CapabilityRuntime()
        self.instance = self.PACK_MODULE(runtime=rt)
        self.instance.register_providers()

    def test_complete_method(self):
        self.assertTrue(hasattr(self.instance, "complete"))
        result = self.instance.complete([{"role": "user", "content": "test"}])
        self.assertIn("content", result.__dict__ if hasattr(result, "__dict__") else {})

    def test_generate_method(self):
        self.assertTrue(hasattr(self.instance, "generate"))


class TestIdentityContract(unittest.TestCase, ContractBase):
    PACK_MODULE = None

    @classmethod
    def setUpClass(cls):
        from SLA113.capabilities.identity import IdentityProvider
        cls.PACK = cls.PACK_MODULE = IdentityProvider

    def test_create_user(self):
        self.assertTrue(hasattr(self.PACK, "create_user"))

    def test_authenticate(self):
        self.assertTrue(hasattr(self.PACK, "authenticate"))

    def test_authorize(self):
        self.assertTrue(hasattr(self.PACK, "authorize"))

    def test_get_profile(self):
        self.assertTrue(hasattr(self.PACK, "get_profile"))


class TestStorageContract(unittest.TestCase, ContractBase):
    PACK_MODULE = None

    @classmethod
    def setUpClass(cls):
        from SLA113.capabilities.storage import StorageProvider
        cls.PACK = cls.PACK_MODULE = StorageProvider

    def test_store_method(self):
        self.assertTrue(hasattr(self.PACK, "store"))

    def test_retrieve_method(self):
        self.assertTrue(hasattr(self.PACK, "retrieve"))

    def test_presign_method(self):
        self.assertTrue(hasattr(self.PACK, "presign"))

    def test_exists_method(self):
        self.assertTrue(hasattr(self.PACK, "exists"))

    def test_delete_method(self):
        self.assertTrue(hasattr(self.PACK, "delete"))


class TestRuntimeContract(unittest.TestCase):
    """The Runtime itself must follow a contract."""

    def test_runtime_constructs(self):
        rt = CapabilityRuntime()
        self.assertIsNotNone(rt)

    def test_register_provider(self):
        rt = CapabilityRuntime()
        from SLA113.execution_engine.provider import ProviderDef, ProviderType
        rt.register_provider(
            ProviderDef(id="test", name="Test", provider_type=ProviderType.LOCAL_DSP,
                         lifecycle="testing", priority=50, cost_per_call=0.0, latency_ms=0,
                         config={}),
            lambda c, i, p, cr: {"ok": True},
        )
        provider = rt.router.select("test")
        self.assertIsNone(provider)  # 'test' is not a capability name

    def test_request_returns_dict(self):
        rt = CapabilityRuntime()
        from SLA113.execution_engine.provider import ProviderDef, ProviderType
        rt.register_provider(
            ProviderDef(id="test-provider", name="Test", provider_type=ProviderType.LOCAL_DSP,
                         lifecycle="active", priority=50, cost_per_call=0.0, latency_ms=0,
                         config={"capability": "test-cap"}),
            lambda c, i, p, cr: {"ok": True},
        )
        result = rt.request("test-cap", {"action": "ping"})
        self.assertIsInstance(result, dict)

    def test_health_returns_dict(self):
        rt = CapabilityRuntime()
        health = rt.health()
        self.assertIsInstance(health, dict)

    def test_metrics_report(self):
        rt = CapabilityRuntime()
        metrics = rt.get_metrics_report()
        self.assertIsInstance(metrics, dict)


if __name__ == "__main__":
    unittest.main()
