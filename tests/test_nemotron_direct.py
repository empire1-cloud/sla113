#!/usr/bin/env python3
"""
Nemotron Flow Engine Direct Test
Tests prosody → timing → orchestration → combinator pipeline
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.nemotron.nemotron_flow import NemotronFlowEngine

def test_nemotron():
    """Test Nemotron Flow Engine execution"""
    print("\n" + "="*80)
    print("NEMOTRON FLOW ENGINE TEST")
    print("="*80 + "\n")
    
    # Initialize engine
    print("[1/4] Initializing Nemotron Flow Engine...")
    engine = NemotronFlowEngine()
    print("✓ Engine initialized\n")
    
    # Create test blueprint
    print("[2/4] Creating test lyrics...")
    lyrics = [
        "Under the jacaranda tree",
        "Where abuela used to sing",
        "Xochitl bloom in purple rain"
    ]
    bpm = 98
    genre = "cumbia-soul"
    print(f"✓ Lyrics: {len(lyrics)} lines, {bpm} BPM, {genre}\n")
    
    # Execute render pipeline
    print("[3/4] Executing Nemotron render pipeline...")
    print("  ├─ Stage 1: Prosody Map Generation")
    print("  ├─ Stage 2: Stem Orchestration")
    print("  └─ Stage 3: Combinator (Final Mix)")
    result = engine.execute_sync(
        lyrics=lyrics,
        bpm=bpm,
        swing=0.15,
        style="cumbia_soul",
        voice_profile="tender_whisper",
        vulnerability=0.7,
        groove="late_pocket_cumbia",
        texture="warm_analog_room",
        genre=genre
    )
    print(f"✓ Pipeline status: {result['status']}\n")
    
    # Verify outputs
    print("[4/4] Verifying render outputs...")
    
    # Check stages
    stages = result.get("stages", {})
    
    # Check prosody
    prosody_stage = stages.get("1_prosody_engine", {})
    if prosody_stage.get("status") == "complete":
        print(f"✓ Prosody map generated")
        print(f"  ├─ BPM: {prosody_stage.get('bpm', 'N/A')}")
        print(f"  ├─ Events: {prosody_stage.get('events', 0)}")
        print(f"  └─ Stem ID: {prosody_stage.get('stem_id', 'N/A')}")
    else:
        print("✗ Prosody map missing")
    
    # Check orchestration
    orch_stage = stages.get("2_stem_orchestration", {})
    if orch_stage.get("status") == "complete":
        print(f"✓ Stem orchestration complete")
        print(f"  ├─ Stems generated: {orch_stage.get('stems_generated', 0)}")
        print(f"  └─ Orchestration ID: {orch_stage.get('orchestration_id', 'N/A')}")
    else:
        print("✗ Stem orchestration missing")
    
    # Check combinator
    comb_stage = stages.get("3_combinator", {})
    if comb_stage.get("status") == "complete":
        print(f"✓ Final mix rendered")
        print(f"  ├─ Path: {comb_stage.get('output_path', 'N/A')}")
        print(f"  └─ Combinator ID: {comb_stage.get('combinator_id', 'N/A')}")
    else:
        print("✗ Final mix missing")
    
    print()
    
    print("="*80)
    if result['status'] == 'complete':
        print("✅ NEMOTRON FLOW ENGINE ONLINE")
    else:
        print("❌ RENDER FAILED")
    print("="*80 + "\n")
    
    return result['status'] == 'complete'

if __name__ == "__main__":
    success = test_nemotron()
    sys.exit(0 if success else 1)
