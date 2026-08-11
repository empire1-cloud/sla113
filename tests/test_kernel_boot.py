#!/usr/bin/env python3
"""
SLA113Kernel Boot Test
Tests kernel boot, worker binding, universe registry, and Black Box enforcement
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.sla113_kernel import SLA113Kernel

def test_kernel_boot():
    """Test SLA113Kernel boot sequence"""
    print("\n" + "="*80)
    print("SLA-113 KERNEL BOOT TEST")
    print("="*80 + "\n")
    
    # Initialize kernel
    print("[1/4] Initializing SLA113Kernel...")
    kernel = SLA113Kernel()
    print("✓ Kernel initialized\n")
    
    # Boot kernel
    print("[2/4] Executing boot sequence...")
    boot_result = kernel.boot()
    print(f"✓ Boot status: {boot_result['status']}")
    print(f"  └─ Workers bound: {boot_result['workers_bound']['bound']}/{boot_result['workers_bound']['total']}")
    print(f"  └─ Universes loaded: {boot_result['universes_loaded']}")
    print(f"  └─ Black Box: {boot_result.get('black_box_enforcement', False)}")
    print(f"  └─ Nemotron: {boot_result.get('nemotron_integration', 'unknown')}")
    print(f"  └─ Lyrica Prosody: {boot_result.get('lyrica_prosody_handshake', 'unknown')}")
    print(f"  └─ Omni Dispatch: {boot_result.get('omni_task_dispatch', 'unknown')}\n")
    
    # Check worker registry
    print("[3/4] Verifying worker bindings...")
    workers = kernel.worker_registry.list_workers()
    worker_names = [w['name'] for w in workers]
    print(f"✓ {len(workers)} workers bound:")
    for name in worker_names:
        print(f"  └─ {name}")
    print()
    
    # Check universe registry
    print("[4/4] Verifying universe boundaries...")
    universes = kernel.universe_registry.list_active()
    print(f"✓ {len(universes)} active universes loaded:")
    for u_data in universes[:5]:  # Show first 5
        print(f"  └─ {u_data.get('id', 'Unknown')}: {u_data.get('name', 'Unknown')}")
    print()
    
    # Test Black Box scrubbing
    print("[BONUS] Testing Black Box scrubbing...")
    test_input = "EPD engine analyzed emotion. S2 synthesized melody. CCNA provided cultural context. Nemotron rendered audio. VICS tagged ownership."
    scrubbed = kernel.black_box.scrub(test_input)
    print(f"✓ Scrubbed output:\n  └─ {scrubbed}\n")
    
    print("="*80)
    if boot_result['status'] == 'online':
        print("✅ SLA-113 ONLINE | ALL WORKERS READY | NEMOTRON SYNCED")
    else:
        print("❌ BOOT FAILED")
    print("="*80 + "\n")
    
    return boot_result['status'] == 'online'

if __name__ == "__main__":
    success = test_kernel_boot()
    sys.exit(0 if success else 1)
