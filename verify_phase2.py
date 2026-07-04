#!/usr/bin/env python3
"""Phase 2 end-to-end verification — Runtime + AI Router + Identity + Storage."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from SLA113.runtime.runtime import CapabilityRuntime
from SLA113.capabilities.ai import AIRouter
from SLA113.capabilities.identity import IdentityProvider
from SLA113.capabilities.storage import StorageProvider


def test_ai_router():
    print("\n[1/5] AI Router...")
    rt = CapabilityRuntime()
    ai = AIRouter(rt)
    ai.register_providers()

    resp = ai.complete([
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say exactly: AI Router works"},
    ])
    assert resp.content is not None
    assert resp.provider is not None
    print(f"  ✅ AI.complete() → provider={resp.provider}, content='{resp.content[:60]}...'")

    gen = ai.generate("Say exactly: Generation works")
    assert gen is not None
    print(f"  ✅ AI.generate() → '{gen[:60]}...'")

    report = rt.get_metrics_report()
    assert len(report) >= 1
    print(f"  ✅ Runtime metrics: {report}")

    health = rt.health()
    assert len(health) >= 1
    print(f"  ✅ Health checks: {len(health)} providers")

    return ai, rt


def test_identity():
    print("\n[2/5] Identity Provider...")
    rt = CapabilityRuntime()
    identity = IdentityProvider(rt)
    identity.register_providers()

    created = identity.create_user("creator@lyrica3.com", "Test Creator", "lyrica3")
    assert created.get("created")
    token = created.get("token", "")
    print(f"  ✅ User created: {created['user_id']}")

    user = identity.authenticate(token, "lyrica3")
    assert user is not None
    assert user.email == "creator@lyrica3.com"
    print(f"  ✅ Authentication: {user.email} (roles: {user.roles})")

    authorized = identity.authorize(user.id, "audio.generate")
    assert authorized
    print(f"  ✅ Authorization: audio.generate = {authorized}")

    denied = identity.authorize(user.id, "admin.billing")
    assert not denied
    print(f"  ✅ Authorization denied for admin.billing = {denied}")

    profile = identity.get_profile(user.id)
    assert profile is not None
    assert profile.universe == "lyrica3"
    print(f"  ✅ Profile: {profile.display_name} in {profile.universe}")

    return identity, rt


def test_storage():
    print("\n[3/5] Storage Provider...")
    rt = CapabilityRuntime()
    storage = StorageProvider(rt, base_path="/tmp/sla113/test_storage")
    storage.register_providers()

    test_data = b"Hello from SLA113 Storage Pack!"
    url = storage.store("test/hello.txt", test_data, "text/plain")
    assert url.startswith("storage://")
    print(f"  ✅ Store: {url}")

    retrieved = storage.retrieve(url)
    assert retrieved == test_data
    print(f"  ✅ Retrieve: {len(retrieved)} bytes match")

    exists = storage.exists("test/hello.txt")
    assert exists
    not_exists = storage.exists("test/nonexistent.txt")
    assert not not_exists
    print(f"  ✅ Exists check: hello.txt={exists}, nonexistent={not_exists}")

    signed_url = storage.presign("test/hello.txt", expiry=3600)
    assert signed_url is not None
    assert "signature=" in signed_url
    print(f"  ✅ Presigned URL: {signed_url[:60]}...")

    files = storage.list_files("test/")
    assert len(files) >= 1
    print(f"  ✅ List files: {len(files)} files in test/")

    deleted = storage.delete("test/hello.txt")
    assert deleted
    assert not storage.exists("test/hello.txt")
    print(f"  ✅ Delete: confirmed file removed")

    return storage, rt


def test_unified_flow():
    print("\n[4/5] Unified cross-pack flow...")
    rt = CapabilityRuntime()

    ai = AIRouter(rt)
    ai.register_providers()

    identity = IdentityProvider(rt)
    identity.register_providers()

    storage = StorageProvider(rt, base_path="/tmp/sla113/test_unified")
    storage.register_providers()

    created = identity.create_user("artist@soulfire.io", "Soulfire Artist", "lyrica3")
    token = created["token"]
    user = identity.authenticate(token, "lyrica3")

    assert identity.authorize(user.id, "audio.generate")

    blueprint = ai.generate(
        f"Generate a music production blueprint for {user.display_name}: "
        f"genre=Chicano Soul, bpm=92, key=C minor, duration=16 bars. "
        f"Return only: BLUEPRINT: [brief description]"
    )
    assert blueprint is not None
    print(f"  ✅ AI generates blueprint: {blueprint[:80]}...")

    wav_data = b"\x00\x01\x02\x03" * 1024
    url = storage.store(f"tracks/{user.id}/blueprint_demo.wav", wav_data, "audio/wav")
    assert url.startswith("storage://")
    print(f"  ✅ Track stored: {url}")

    retrieved = storage.retrieve(url)
    assert retrieved == wav_data
    assert len(retrieved) == 4096
    print(f"  ✅ Track retrieved: {len(retrieved)} bytes")

    report = rt.get_metrics_report()
    print(f"  ✅ Runtime metrics: {len(report)} provider stats recorded")

    print(f"  ✅ Unified flow complete — AI → Identity → Storage")


def test_registry_integration():
    print("\n[5/5] Registry + Runtime integration...")
    from SLA113.execution_engine import Engine

    engine = Engine()
    engine.load_registries()

    universes = engine.list_universes()
    assert len(universes) >= 5
    print(f"  ✅ {len(universes)} universes registered")

    products = engine.list_products()
    assert len(products) >= 15
    print(f"  ✅ {len(products)} products registered")

    agents = engine.list_agents()
    assert len(agents) >= 15
    print(f"  ✅ {len(agents)} agents registered")

    workflows = list(engine.list_workflows().keys())
    assert "instrumental_generation" in workflows
    print(f"  ✅ {len(workflows)} workflows: {workflows}")

    caps = services = None
    from SLA113.execution_engine.register import RegistryLoader
    loader = RegistryLoader()
    caps = loader.load_capabilities()
    svcs = loader.load_services()
    print(f"  ✅ {len(caps)} capabilities, {len(svcs)} services")

    rt = CapabilityRuntime()
    ai = AIRouter(rt)
    ai.register_providers()

    identity = IdentityProvider(rt)
    identity.register_providers()

    storage = StorageProvider(rt)
    storage.register_providers()

    health = rt.health()
    print(f"  ✅ Runtime health: {len(health)} providers checked ({sum(1 for h in health.values() if h.healthy)} healthy)")


def main():
    print("=" * 60)
    print("SLA113 Phase 2 — End-to-End Verification")
    print("=" * 60)

    test_ai_router()
    test_identity()
    test_storage()
    test_unified_flow()
    test_registry_integration()

    print("\n" + "=" * 60)
    print("Phase 2 — ✅ ALL TESTS PASSED")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
