#!/usr/bin/env python3
"""
Full System Test: 60-Second "Toxic" Drama Scene
Tests integration of:
1. Toxic Ad-Lib Generator
2. Sancha Siren Reverb (SSS Presets)
3. TikTok Engine (Lane G)
4. Full PFA → SSS → Video pipeline

Part of: SLA-113 | Lyrica3 Soulfire Engine | Toxic Drama Expansion
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List

sys.path.insert(0, str(Path(__file__).parent.parent))

from LYRICA3.soulfire_engine.toxic_adlib_generator import ToxicAdLibGenerator, AdLibEvent
from LYRICA3.soulfire_engine.tiktok_engine import TikTokEngine, TikTokPayload
from LYRICA3.soulfire_engine.sss_presets import (
    SSSPresetManager, 
    SANCHA_SIREN_PRESET, 
    TOXICO_PRIME_PRESET
)
from LYRICA3.soulfire_engine.nemotron_adlib_bridge import NemotronAdLibBridge


def generate_sancha_pfa_map() -> List[Dict[str, Any]]:
    """
    Generate SANCHA_V1 PFA map for 60-second drama scene.
    Simulates full prosody-filled audio map with vulnerability markers.
    """
    return [
        # Phrase 1: Initial accusation (vulnerable)
        {
            "phrase_id": "sancha_001",
            "timestamp_ms_start": 0,
            "duration_ms": 2500,
            "text": "Why do you always do this?",
            "intensity": 0.7,
            "dsp_injections": {
                "vulnerability": 0.85,
                "tremolo": 0.6,
                "breathiness": 0.7
            }
        },
        
        # Phrase 2: Emotional escalation (high vulnerability)
        {
            "phrase_id": "sancha_002",
            "timestamp_ms_start": 3000,
            "duration_ms": 2000,
            "text": "I trusted you... <emotional_crack>",
            "intensity": 0.9,
            "dsp_injections": {
                "vulnerability": 0.95,
                "tremolo": 0.8,
                "breathiness": 0.9,
                "pitch_waver": 0.6
            }
        },
        
        # Phrase 3: Silence/pause (800ms) before next phrase
        
        # Phrase 4: Quieter, more hurt (medium vulnerability)
        {
            "phrase_id": "sancha_003",
            "timestamp_ms_start": 6500,
            "duration_ms": 2200,
            "text": "You said you'd be different",
            "intensity": 0.6,
            "dsp_injections": {
                "vulnerability": 0.75,
                "tremolo": 0.5,
                "breathiness": 0.8
            }
        },
        
        # Phrase 5: Building anger (low vulnerability, high intensity)
        {
            "phrase_id": "sancha_004",
            "timestamp_ms_start": 9500,
            "duration_ms": 1800,
            "text": "But you're just like everyone else",
            "intensity": 0.88,
            "dsp_injections": {
                "vulnerability": 0.4,
                "tremolo": 0.2,
                "breathiness": 0.3,
                "distortion": 0.3
            }
        },
        
        # Phrase 6: Long silence (1200ms) - big gap for ad-lib
        
        # Phrase 7: Breakdown moment (extreme vulnerability)
        {
            "phrase_id": "sancha_005",
            "timestamp_ms_start": 13500,
            "duration_ms": 2800,
            "text": "I can't... I can't do this anymore <emotional_crack>",
            "intensity": 0.95,
            "dsp_injections": {
                "vulnerability": 0.98,
                "tremolo": 0.9,
                "breathiness": 0.95,
                "pitch_waver": 0.8
            }
        },
        
        # Phrase 8: Quieter resignation
        {
            "phrase_id": "sancha_006",
            "timestamp_ms_start": 17000,
            "duration_ms": 2000,
            "text": "It's over",
            "intensity": 0.5,
            "dsp_injections": {
                "vulnerability": 0.85,
                "tremolo": 0.7,
                "breathiness": 0.9
            }
        }
    ]


def print_test_header(title: str):
    """Print formatted test section header"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}\n")


def print_test_result(name: str, passed: bool, details: str = ""):
    """Print test result"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status} | {name}")
    if details:
        print(f"       └─ {details}")


def test_toxic_drama_full():
    """Run full 60-second Toxic Drama integration test"""
    
    print_test_header("60-SECOND TOXIC DRAMA INTEGRATION TEST")
    
    # ========================================================================
    # STAGE 1: Generate SANCHA_V1 PFA Map
    # ========================================================================
    print("[STAGE 1/6] Generating SANCHA_V1 PFA Map...")
    sancha_pfa = generate_sancha_pfa_map()
    
    print(f"✓ Generated {len(sancha_pfa)} phrases")
    total_duration = max([p['timestamp_ms_start'] + p['duration_ms'] for p in sancha_pfa])
    print(f"  └─ Total duration: {total_duration/1000:.1f}s")
    
    # Calculate vulnerability stats
    avg_vulnerability = sum([p['dsp_injections']['vulnerability'] for p in sancha_pfa]) / len(sancha_pfa)
    print(f"  └─ Avg vulnerability: {avg_vulnerability:.2f}")
    print()
    
    # ========================================================================
    # STAGE 2: Generate TOXICO_PRIME Ad-Libs (Reactive)
    # ========================================================================
    print("[STAGE 2/6] Generating TOXICO_PRIME Ad-Libs (Reactive)...")
    
    ad_lib_gen = ToxicAdLibGenerator(persona_id="TOXICO_PRIME")
    toxico_adlibs = ad_lib_gen.generate_background_track(sancha_pfa)
    
    print(f"✓ Generated {len(toxico_adlibs)} ad-lib events")
    
    # Get statistics
    stats = ad_lib_gen.get_statistics(toxico_adlibs)
    print(f"  ├─ By type: {stats['by_type']}")
    print(f"  ├─ Avg intensity: {stats['avg_intensity']}")
    print(f"  └─ Events/second: {stats['events_per_second']}")
    print()
    
    # Show first 3 ad-libs
    print("Sample ad-lib events:")
    for i, adlib in enumerate(toxico_adlibs[:3]):
        print(f"  {i+1}. [{adlib.timestamp_ms/1000:.2f}s] {adlib.token} ({adlib.reaction_type})")
    print()
    
    # ========================================================================
    # STAGE 3: Render Ad-Libs via Nemotron Bridge
    # ========================================================================
    print("[STAGE 3/7] Rendering Ad-Libs via Nemotron Bridge...")
    
    nemotron_bridge = NemotronAdLibBridge(persona_id="TOXICO_PRIME")
    
    # Convert to prosody format
    prosody_map = nemotron_bridge._convert_to_prosody(toxico_adlibs)
    print(f"✓ Converted to Nemotron prosody format")
    print(f"  ├─ Prosody stem ID: {prosody_map['stem_id']}")
    print(f"  ├─ Timeline events: {prosody_map['total_events']}")
    print(f"  └─ Duration: {prosody_map['duration_ms']/1000:.1f}s")
    print()
    
    # Show voice profile mappings
    print("Voice profile mappings:")
    for i, event in enumerate(prosody_map['timeline'][:3]):
        print(f"  {i+1}. {event['text']} → {event['voice_profile']} ({event['reaction_type']})")
    print()
    
    # Render (sync version for testing)
    adlib_stem = nemotron_bridge.render_adlib_track_sync(toxico_adlibs)
    print(f"✓ Rendered ad-lib stem: {adlib_stem['stem_id']}")
    print(f"  ├─ Clips rendered: {adlib_stem['total_clips']}")
    print(f"  ├─ Mix level: {adlib_stem['mix_instructions']['level_db']}dB")
    print(f"  ├─ Reverb preset: {adlib_stem['mix_instructions']['reverb_preset']}")
    print(f"  └─ Sidechain target: {adlib_stem['mix_instructions']['sidechain_target']}")
    print()
    
    # ========================================================================
    # STAGE 4: Apply SSS Presets (Sancha Siren + Toxico Harsh)
    # ========================================================================
    print("[STAGE 4/7] Applying SSS Presets...")
    
    preset_manager = SSSPresetManager()
    
    # Get presets
    sancha_preset = preset_manager.get_preset("SANCHA_SIREN_V1")
    toxico_preset = preset_manager.get_preset("TOXICO_HARSH_V1")
    
    print(f"✓ Loaded SANCHA_SIREN_V1 preset")
    print(f"  ├─ Reverb: {sancha_preset['reverb']['type']} ({sancha_preset['reverb']['params']['decay_ms']}ms decay)")
    print(f"  ├─ Wet/Dry: {sancha_preset['reverb']['params']['wet_dry_ratio']:.0%}")
    print(f"  └─ Sidechain: {sancha_preset['post_processing']['sidechain_compression']['enabled']}")
    print()
    
    print(f"✓ Loaded TOXICO_HARSH_V1 preset")
    print(f"  ├─ Reverb: {toxico_preset['reverb']['type']} ({toxico_preset['reverb']['params']['decay_ms']}ms decay)")
    print(f"  ├─ Wet/Dry: {toxico_preset['reverb']['params']['wet_dry_ratio']:.0%}")
    print(f"  └─ Saturation: {toxico_preset['post_processing']['saturation']['drive_db']}dB")
    print()
    
    # Get sidechain configuration
    sidechain_config = preset_manager.get_sidechain_configuration("TOXICO_HARSH_V1", "SANCHA_SIREN_V1")
    if sidechain_config:
        print("✓ Sidechain compression configured:")
        print(f"  ├─ Source: {sidechain_config['source_preset']} (TOXICO_PRIME)")
        print(f"  ├─ Target: {sidechain_config['target_preset']} (SANCHA_V1)")
        print(f"  ├─ Threshold: {sidechain_config['configuration']['threshold_db']}dB")
        print(f"  └─ Ratio: {sidechain_config['configuration']['ratio']}")
    print()
    
    # ========================================================================
    # STAGE 5: Generate TikTok Video Payload (Lane G)
    # ========================================================================
    print("[STAGE 5/7] Generating TikTok Video Payload (Lane G)...")
    
    tiktok_engine = TikTokEngine(template_id="TOXIC_CONFLICT_SPLIT")
    
    # Convert ad-libs to PFA format
    toxico_pfa = ad_lib_gen.export_to_nemotron_format(toxico_adlibs)
    
    # Generate payload
    scene_metadata = {
        "title": "Toxic Drama Test Scene",
        "scene_type": "conflict_dialogue",
        "personas": ["SANCHA_V1", "TOXICO_PRIME"]
    }
    
    tiktok_payload = tiktok_engine.generate_payload(
        sancha_pfa=sancha_pfa,
        toxico_pfa=toxico_pfa,
        scene_metadata=scene_metadata
    )
    
    print(f"✓ Generated TikTok payload: {tiktok_payload.payload_id}")
    print(f"  ├─ Template: {tiktok_payload.template_id}")
    print(f"  ├─ Glitch triggers: {len(tiktok_payload.glitch_triggers)}")
    print(f"  ├─ Sync markers: {len(tiktok_payload.audio_sync_markers)}")
    print(f"  └─ Duration: {tiktok_payload.output_config['duration_ms']/1000:.1f}s")
    print()
    
    # Show glitch timeline
    glitch_timeline = tiktok_engine.get_glitch_timeline(tiktok_payload)
    print("Glitch timeline (first 5 events):")
    for i, event in enumerate(glitch_timeline[:5]):
        print(f"  {i+1}. [{event['timestamp_seconds']}s] {event['type']} ({event['persona']}, intensity={event['intensity']:.2f})")
    print()
    
    # ========================================================================
    # STAGE 6: Validate Integration
    # ========================================================================
    print("[STAGE 6/7] Validating Integration...")
    
    validation_result = tiktok_engine.validate_payload(tiktok_payload)
    
    if validation_result["valid"]:
        print("✓ Payload validation: PASS")
    else:
        print("✗ Payload validation: FAIL")
        for error in validation_result["errors"]:
            print(f"  └─ Error: {error}")
    
    if validation_result["warnings"]:
        for warning in validation_result["warnings"]:
            print(f"  └─ Warning: {warning}")
    print()
    
    # ========================================================================
    # STAGE 7: Export Artifacts
    # ========================================================================
    print("[STAGE 7/7] Exporting Artifacts...")
    
    output_dir = Path("/tmp/toxic_drama_test")
    output_dir.mkdir(exist_ok=True)
    
    # Export TikTok payload
    tiktok_json_path = output_dir / f"{tiktok_payload.payload_id}.json"
    tiktok_engine.export_to_file(tiktok_payload, str(tiktok_json_path))
    print(f"✓ Exported TikTok payload: {tiktok_json_path}")
    
    # Export ad-lib spec
    adlib_spec = ad_lib_gen.render_to_audio_spec(toxico_adlibs)
    adlib_json_path = output_dir / "toxico_adlibs_spec.json"
    with open(adlib_json_path, 'w') as f:
        json.dump(adlib_spec, f, indent=2)
    print(f"✓ Exported ad-lib spec: {adlib_json_path}")
    
    # Export Nemotron stem spec
    nemotron_stem_path = output_dir / "nemotron_adlib_stem.json"
    with open(nemotron_stem_path, 'w') as f:
        json.dump(adlib_stem, f, indent=2, default=str)
    print(f"✓ Exported Nemotron stem: {nemotron_stem_path}")
    
    # Export SSS presets
    sss_presets_path = output_dir / "sss_presets.json"
    with open(sss_presets_path, 'w') as f:
        json.dump({
            "sancha_siren": SANCHA_SIREN_PRESET,
            "toxico_harsh": TOXICO_PRIME_PRESET,
            "sidechain_config": sidechain_config
        }, f, indent=2)
    print(f"✓ Exported SSS presets: {sss_presets_path}")
    
    # Export full scene manifest
    manifest = {
        "scene_id": "toxic_drama_test_60s",
        "duration_ms": total_duration,
        "sancha_pfa": sancha_pfa,
        "toxico_adlibs": [vars(a) for a in toxico_adlibs],
        "sss_presets": {
            "sancha": "SANCHA_SIREN_V1",
            "toxico": "TOXICO_HARSH_V1"
        },
        "tiktok_payload_id": tiktok_payload.payload_id,
        "statistics": {
            "sancha_phrases": len(sancha_pfa),
            "toxico_adlibs": len(toxico_adlibs),
            "glitch_triggers": len(tiktok_payload.glitch_triggers),
            "avg_vulnerability": avg_vulnerability,
            "adlib_stats": stats
        }
    }
    
    manifest_path = output_dir / "scene_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"✓ Exported scene manifest: {manifest_path}")
    print()
    
    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    print_test_header("TEST SUMMARY")
    
    test_results = [
        ("SANCHA_V1 PFA Map Generation", len(sancha_pfa) > 0, f"{len(sancha_pfa)} phrases"),
        ("TOXICO_PRIME Ad-Lib Generation", len(toxico_adlibs) > 0, f"{len(toxico_adlibs)} events"),
        ("Nemotron Bridge Prosody Conversion", prosody_map['total_events'] > 0, f"{prosody_map['total_events']} events"),
        ("Nemotron Ad-Lib Rendering", adlib_stem['total_clips'] > 0, f"{adlib_stem['total_clips']} clips"),
        ("SSS Preset Loading", sancha_preset and toxico_preset, "SANCHA_SIREN + TOXICO_HARSH"),
        ("Sidechain Configuration", sidechain_config is not None, "TOXICO → SANCHA ducking"),
        ("TikTok Payload Generation", tiktok_payload is not None, tiktok_payload.payload_id),
        ("Payload Validation", validation_result["valid"], "No errors"),
        ("Artifact Export", all([
            tiktok_json_path.exists(),
            adlib_json_path.exists(),
            nemotron_stem_path.exists(),
            sss_presets_path.exists(),
            manifest_path.exists()
        ]), "5 files exported")
    ]
    
    for name, passed, details in test_results:
        print_test_result(name, passed, details)
    
    print()
    print(f"{'='*80}")
    
    all_passed = all([result[1] for result in test_results])
    
    if all_passed:
        print("✅ TOXIC DRAMA EXPANSION: FULLY OPERATIONAL")
        print("🎭 All systems integrated: Ad-Lib Generator → SSS Presets → TikTok Engine")
        print(f"📁 Artifacts exported to: {output_dir}")
    else:
        print("⚠ Some tests failed. Review errors above.")
    
    print(f"{'='*80}\n")
    
    return all_passed


if __name__ == "__main__":
    success = test_toxic_drama_full()
    sys.exit(0 if success else 1)
