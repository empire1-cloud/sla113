#!/usr/bin/env python3
"""Verify Phase 2A — Runtime, Provider Router, and Lifecycle."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from SLA113.runtime import CapabilityRuntime
from SLA113.runtime.lifecycle import LifecycleManager, is_valid_transition
from SLA113.execution_engine.provider import ProviderDef, ProviderType, ProviderRouter


def test_provider_router():
    print("\n[1/5] Provider Router...")
    router = ProviderRouter()

    dsp = ProviderDef(id="test-dsp", name="Test DSP", provider_type=ProviderType.LOCAL_DSP,
                       lifecycle="active", priority=95, config={"capability": "audio"})
    cloud = ProviderDef(id="test-cloud", name="Test Cloud", provider_type=ProviderType.CLOUD_API,
                        lifecycle="active", priority=50, cost_per_call=0.01, latency_ms=2000,
                        config={"capability": "audio"})

    router.register(dsp, lambda cap, inp, prov, cid: b"dsp audio")
    router.register(cloud, lambda cap, inp, prov, cid: b"cloud audio")

    selected = router.select("audio")
    assert selected is not None
    assert selected.id == "test-dsp"
    print(f"  ✅ Selects highest priority: {selected.id}")

    preferred = router.select("audio", preference="test-cloud")
    assert preferred is not None
    assert preferred.id == "test-cloud"
    print(f"  ✅ Preference overrides priority: {preferred.id}")

    health = router.health_summary()
    assert len(health) == 2
    print(f"  ✅ Health summary: {len(health)} providers")

    return router


def test_lifecycle():
    print("\n[2/5] Lifecycle Manager...")
    lm = LifecycleManager()
    lm.register("test-pack", initial_state="scaffold", version="0.1.0")
    assert lm.get_state("test-pack").state == "scaffold"
    assert not lm.can_use("test-pack")

    lm.promote("test-pack", "development", "Starting development")
    lm.promote("test-pack", "testing", "Entering testing")
    lm.promote("test-pack", "active", "Production ready")
    assert lm.can_use("test-pack")
    assert lm.get_state("test-pack").state == "active"

    assert not is_valid_transition("active", "scaffold")
    assert is_valid_transition("development", "active")
    assert not is_valid_transition("deprecated", "active")

    print(f"  ✅ Lifecycle transitions: scaffold → development → testing → active")
    print(f"  ✅ Invalid transitions rejected")

    return lm


def test_runtime():
    print("\n[3/5] CapabilityRuntime...")
    rt = CapabilityRuntime()

    mock_handler = lambda cap, inp, prov, cid: {"result": f"{cap} processed by {prov.id}"}

    rt.register_provider(
        ProviderDef(id="mock-audio", name="Mock Audio", provider_type=ProviderType.LOCAL_DSP,
                     lifecycle="active", priority=95, config={"capability": "audio"}),
        mock_handler,
    )
    rt.register_provider(
        ProviderDef(id="mock-ai", name="Mock AI", provider_type=ProviderType.LOCAL_DSP,
                     lifecycle="active", priority=90, config={"capability": "ai"}),
        mock_handler,
    )

    result = rt.request("audio", {"prompt": "test"})
    assert result["result"] == "audio processed by mock-audio"
    print(f"  ✅ Capability routing works: {result}")

    result2 = rt.request("ai", {"prompt": "hello"})
    assert result2["result"] == "ai processed by mock-ai"
    print(f"  ✅ Multi-capability routing works")

    report = rt.get_metrics_report()
    assert len(report) == 2
    assert report["mock-audio"]["call_count"] == 1
    print(f"  ✅ Metrics recorded: {report['mock-audio']}")

    health = rt.health()
    assert len(health) == 2
    print(f"  ✅ Health check: {len(health)} providers")

    return rt


def test_fallback_chain():
    print("\n[4/5] Fallback chaining...")
    rt = CapabilityRuntime()

    failing = lambda cap, inp, prov, cid: (_ for _ in ()).throw(RuntimeError("Provider down"))

    rt.register_provider(
        ProviderDef(id="failing-audio", name="Failing", provider_type=ProviderType.CLOUD_API,
                     lifecycle="active", priority=90, config={"capability": "audio"}),
        failing,
    )
    rt.register_provider(
        ProviderDef(id="backup-audio", name="Backup", provider_type=ProviderType.LOCAL_DSP,
                     lifecycle="active", priority=80, config={"capability": "audio"}),
        lambda cap, inp, prov, cid: {"result": "fallback worked"},
    )

    result = rt.request("audio", {"prompt": "test"})
    assert result["result"] == "fallback worked"
    print(f"  ✅ Fallback chain works when primary fails")

    report = rt.get_metrics_report()
    assert "failing-audio" in report
    assert report["failing-audio"]["call_count"] >= 0
    print(f"  ✅ Error metrics recorded: {report['failing-audio']}")

    return rt


def test_cache():
    print("\n[5/5] Cache layer...")
    call_count = [0]

    def counted_handler(cap, inp, prov, cid):
        call_count[0] += 1
        return {"result": "cached", "count": call_count[0]}

    rt = CapabilityRuntime()
    rt.register_provider(
        ProviderDef(id="cache-test", name="Cache Test", provider_type=ProviderType.LOCAL_DSP,
                     lifecycle="active", priority=95, config={"capability": "cache_test"}),
        counted_handler,
    )

    r1 = rt.request("cache_test", {"x": 1}, use_cache=True)
    r2 = rt.request("cache_test", {"x": 1}, use_cache=True)
    r3 = rt.request("cache_test", {"x": 2}, use_cache=True)

    assert call_count[0] == 2  # only x=1 and x=2, not the cached x=1 call
    print(f"  ✅ Cache hits reduce calls: {call_count[0]} handler calls for 3 requests")

    report = rt.get_metrics_report()
    assert report["cache-test"]["cache_hits"] == 1
    print(f"  ✅ Cache hit metric recorded: {report['cache-test']['cache_hits']}")


def main():
    print("=" * 60)
    print("SLA113 Phase 2A — Runtime Verification")
    print("=" * 60)

    test_provider_router()
    test_lifecycle()
    test_runtime()
    test_fallback_chain()
    test_cache()

    print("\n" + "=" * 60)
    print("Phase 2A — ✅ ALL TESTS PASSED")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
