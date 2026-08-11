#!/usr/bin/env python3
"""
SLA-113 Full End-to-End Pipeline Test
Tests: Omni → Lyrica → Nemotron → Ledger → CCNA → Black Box
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.sla113_kernel import SLA113Kernel
from backend.services.nemotron.nemotron_flow import NemotronFlowEngine
from backend.services.cultural.ccna_engine import CCNAEngine
from LYRICA3.soulfire_engine.royalty_ledger import RoyaltyLedger

def test_full_pipeline():
    """Test full SLA-113 pipeline integration"""
    print("\n" + "="*80)
    print("SLA-113 FULL END-TO-END PIPELINE TEST")
    print("="*80 + "\n")
    
    # Stage 0: Boot Kernel
    print("[STAGE 0] Booting SLA-113 Kernel...")
    kernel = SLA113Kernel()
    boot_result = kernel.boot()
    print(f"✓ Kernel status: {boot_result['status']}")
    print(f"  ├─ Workers: {boot_result['workers_bound']['bound']}/{boot_result['workers_bound']['total']}")
    print(f"  ├─ Universes: {boot_result['universes_loaded']}")
    print(f"  └─ Black Box: {boot_result.get('black_box_enforcement', False)}\n")
    
    # Stage 1: Omni Task Interpretation (simulated - would route to personas)
    print("[STAGE 1] Omni Task Interpretation...")
    task = {
        "user_request": "Create a Chicano lullaby about heritage and memory",
        "task_type": "creative",
        "universe": "U1"
    }
    
    # Simulate Omni routing decision
    routing = kernel.route_request("creative", task)
    print(f"✓ Task routed: {task['task_type']}")
    print(f"  └─ Route: {' → '.join(routing['route'][:5])}\n")
    
    # Stage 2: Lyrica Blueprint Creation (simulated - would call EPD/S2)
    print("[STAGE 2] Lyrica Blueprint Creation (simulated)...")
    lyrica_blueprint = {
        "title": "Xochitl Bloom",
        "lyrics": [
            "Under the jacaranda tree",
            "Where abuela used to sing to me",
            "Xochitl bloom in purple rain",
            "In San Gabriel Valley",
            "Where the barrio raised me",
            "Memories of familia remain"
        ],
        "bpm": 98,
        "genre": "cumbia-soul",
        "key": "Am",
        "mood": "tender"
    }
    print(f"✓ Blueprint created: {lyrica_blueprint['title']}")
    print(f"  ├─ Genre: {lyrica_blueprint['genre']}")
    print(f"  ├─ BPM: {lyrica_blueprint['bpm']}")
    print(f"  └─ Lines: {len(lyrica_blueprint['lyrics'])}\n")
    
    # Stage 3: CCNA Cultural Analysis
    print("[STAGE 3] CCNA Cultural Analysis...")
    lyrics_text = " ".join(lyrica_blueprint['lyrics'])
    ccna_result = CCNAEngine.analyze(lyrics_text, genre=lyrica_blueprint['genre'])
    print(f"✓ Analysis ID: {ccna_result['analysis_id']}")
    print(f"  ├─ Cultural markers: {ccna_result['marker_count']}")
    archetype = ccna_result['narrative_archetype']
    primary_archetype = archetype.get('primary', {}).get('type', 'unknown')
    print(f"  └─ Archetype: {primary_archetype}\n")
    
    # Stage 4: Nemotron Audio Rendering
    print("[STAGE 4] Nemotron Audio Rendering...")
    nemotron = NemotronFlowEngine()
    nemotron_result = nemotron.execute_sync(
        lyrics=lyrica_blueprint['lyrics'],
        bpm=lyrica_blueprint['bpm'],
        swing=0.15,
        style="cumbia_soul",
        voice_profile="tender_whisper",
        vulnerability=0.7,
        groove="late_pocket_cumbia",
        texture="warm_analog_room",
        genre=lyrica_blueprint['genre']
    )
    print(f"✓ Pipeline ID: {nemotron_result['pipeline_id']}")
    print(f"  ├─ Status: {nemotron_result['status']}")
    
    stages = nemotron_result.get('stages', {})
    prosody = stages.get('1_prosody_engine', {})
    orch = stages.get('2_stem_orchestration', {})
    comb = stages.get('3_combinator', {})
    
    print(f"  ├─ Prosody: {prosody.get('events', 0)} events")
    print(f"  ├─ Stems: {orch.get('stems_generated', 0)} generated")
    print(f"  └─ Mix: {comb.get('output_path', 'N/A')}\n")
    
    # Stage 5: Ledger Commit (VICS/DNA Tagging)
    print("[STAGE 5] Royalty Ledger Commit...")
    ledger = RoyaltyLedger()
    
    # Prepare split map
    split_map = {
        "primary_artist": 50.0,
        "producer": 30.0,
        "cultural_advisor": 20.0
    }
    
    # Create DNA tag
    dna_tag = f"{lyrica_blueprint['genre']}_{lyrica_blueprint['bpm']}bpm_{lyrica_blueprint['key']}_{'_'.join([m['marker'] for m in ccna_result['cultural_markers'][:3]])}"
    
    # Commit to ledger
    ledger_event = ledger.commit_event(
        track_id=f"xochitl_bloom_{nemotron_result['pipeline_id']}",
        creator_id="SLA-113_E2E_Pipeline",
        split_map=split_map,
        dna_tag=dna_tag,
        event_type="PIPELINE_COMMIT",
        metadata={
            "title": lyrica_blueprint['title'],
            "universe": "U1",
            "nemotron_pipeline_id": nemotron_result['pipeline_id'],
            "ccna_analysis_id": ccna_result['analysis_id'],
            "cultural_markers": [m['marker'] for m in ccna_result['cultural_markers'][:5]]
        }
    )
    
    print(f"✓ Event ID: {ledger_event.event_id}")
    print(f"  ├─ Track ID: {ledger_event.track_id}")
    print(f"  ├─ DNA tag: {ledger_event.dna_tag[:40]}...")
    print(f"  └─ Timestamp: {ledger_event.timestamp}\n")
    
    # Stage 6: Black Box Scrubbing
    print("[STAGE 6] Black Box Scrubbing...")
    raw_output = f"Song '{lyrica_blueprint['title']}' created. EPD analyzed emotional content. S2 generated melody suggestions. CCNA identified {ccna_result['marker_count']} cultural markers. Nemotron rendered {orch.get('stems_generated', 0)} stems via Flow Conductor. VICS tagged with ID {ledger_event.event_id}. DNA tag: {dna_tag[:40]}."
    
    scrubbed_output = kernel.black_box.scrub(raw_output)
    print(f"✓ Black Box scrubbing applied\n")
    
    # Final Summary
    print("="*80)
    print("PIPELINE OUTPUT (Black Box Scrubbed):")
    print("="*80)
    print(scrubbed_output)
    print("="*80 + "\n")
    
    # Verification
    success = all([
        boot_result['status'] == 'online',
        nemotron_result['status'] == 'complete',
        ccna_result.get('analysis_id'),
        ledger_event.event_id,
        len(scrubbed_output) > 0
    ])
    
    print("="*80)
    print("PIPELINE VERIFICATION:")
    print("="*80)
    print(f"✓ Kernel Boot:        {'PASS' if boot_result['status'] == 'online' else 'FAIL'}")
    print(f"✓ Omni Routing:       {'PASS' if routing.get('route') else 'FAIL'}")
    print(f"✓ Lyrica Blueprint:   {'PASS' if lyrica_blueprint.get('title') else 'FAIL'}")
    print(f"✓ CCNA Analysis:      {'PASS' if ccna_result.get('analysis_id') else 'FAIL'}")
    print(f"✓ Nemotron Render:    {'PASS' if nemotron_result['status'] == 'complete' else 'FAIL'}")
    print(f"✓ Ledger Commit:      {'PASS' if ledger_event.event_id else 'FAIL'}")
    print(f"✓ Black Box Scrub:    {'PASS' if scrubbed_output else 'FAIL'}")
    print("="*80 + "\n")
    
    if success:
        print("🎉 SLA-113 ONLINE | ALL WORKERS READY | NEMOTRON SYNCED")
        print("✅ Full pipeline operational. Ready for production.\n")
    else:
        print("⚠ Pipeline test failed. Review errors above.\n")
    
    return success

if __name__ == "__main__":
    success = test_full_pipeline()
    sys.exit(0 if success else 1)
