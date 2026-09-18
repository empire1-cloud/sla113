#!/usr/bin/env python3
"""Verify the Execution Engine works end-to-end with registries and a real workflow."""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from SLA113.execution_engine import Engine
from SLA113.execution_engine.handlers import (
    load_procedural_instrumental,
    load_soulfire_mastering,
    load_dna_watermark,
    load_render_engine,
)
from SLA113.execution_engine.register import RegistryLoader


def main():
    print("=" * 60)
    print("SLA113 Execution Engine — Phase 1 Verification")
    print("=" * 60)

    engine = Engine()
    engine.load_registries()

    print("\n[1/6] Loading registries...")
    loader = RegistryLoader()

    universes = loader.load_universes()
    print(f"  Universes: {len(universes)} — {[u['name'] for u in universes]}")

    products = loader.load_products()
    print(f"  Products: {len(products)}")

    capabilities = loader.load_capabilities()
    print(f"  Capabilities: {len(capabilities)} — {list(capabilities.keys())}")

    services = loader.load_services()
    print(f"  Services: {len(services)}")

    workflows = loader.load_workflows()
    print(f"  Workflows: {len(workflows)} — {list(workflows.keys())}")

    agents = loader.load_agents()
    print(f"  Agents: {len(agents)}")

    print("\n[2/6] Validating workflow graphs...")
    from SLA113.execution_engine.graph import Graph
    for wid, wf in workflows.items():
        g = Graph(wf)
        errors = g.validate()
        if errors:
            print(f"  ❌ {wid}: {errors}")
        else:
            order = g.execution_order()
            print(f"  ✅ {wid}: execution order → {' → '.join(order)}")

    print("\n[3/6] Resolving services...")
    resolver = loader.build_resolver()
    for cap_id in capabilities:
        svc = resolver.resolve(cap_id)
        if svc:
            print(f"  ✅ {cap_id} → {svc.name} (priority {svc.priority}, cost ${svc.cost_per_call})")
        else:
            print(f"  ⚠️  {cap_id} → no active service")

    print("\n[4/6] Registering handlers...")
    engine.register_handler("procedural-instrumental", load_procedural_instrumental)
    engine.register_handler("soulfire-mastering", load_soulfire_mastering)
    engine.register_handler("dna-watermark", load_dna_watermark)
    engine.register_handler("sonic-forge", load_render_engine)
    engine.register_handler("render-engine-preview", load_render_engine)
    print("  ✅ 5 handlers registered")

    print("\n[5/6] Running 'instrumental_generation' workflow...")
    result = engine.run("instrumental_generation", {
        "prompt": "Chicano soul at 92 BPM in C minor",
        "bpm": 92,
        "key": "C",
        "cultural_matrix": "LA SGV Chicano Heritage",
        "creator_id": "verification-test",
    })

    if result.success:
        print(f"  ✅ Workflow succeeded!")
        for nid, nr in result.node_results.items():
            status = "✅" if nr.success else "❌"
            print(f"     {status} {nid} ({nr.service_used}, {nr.latency_ms}ms)")
        audio_size = len(result.final_outputs.get("rendered", b""))
        url = result.final_outputs.get("url", "unknown")
        print(f"     Final audio: {audio_size} bytes")
        print(f"     Output location: {url}")
    else:
        print(f"  ❌ Workflow failed: {result.error}")
        for nid, nr in result.node_results.items():
            status = "✅" if nr.success else "❌"
            print(f"     {status} {nid}: {nr.error or 'ok'} ({nr.latency_ms}ms)")

    print("\n[6/6] Verifying engine API...")
    print(f"  🔹 Workflows: {list(engine.list_workflows().keys())}")
    print(f"  🔹 Universes:  {[u['name'] for u in engine.list_universes()]}")
    print(f"  🔹 Products:   {len(engine.list_products())}")
    print(f"  🔹 Agents:     {len(engine.list_agents())}")

    print("\n" + "=" * 60)
    status = "✅ PASS" if result.success else "❌ FAIL"
    print(f"Phase 1 Verification: {status}")
    print("=" * 60)

    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
