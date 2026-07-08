"""
Simplified Empire Audio Pipeline 2.0 Test
Tests the high-level run_pipeline() integration

Part of: SLA-113 | Toxic Drama Expansion | Empire Pipeline Validation
Rule: EVOLVE NEVER DELETE
"""

import pytest
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from LYRICA3.soulfire_engine.empire_audio_pipeline import EmpireAudioPipeline


@pytest.mark.asyncio
async def test_empire_pipeline_full_integration():
    """Test full Empire Pipeline with realistic Soulfire payload"""
    print("\n" + "="*80)
    print("TEST: Empire Audio Pipeline 2.0 - Full Integration")
    print("="*80)
    
    # Initialize pipeline
    pipeline = EmpireAudioPipeline()
    
    # Realistic Soulfire payload (matches actual LYRICA3 structure)
    soulfire_payload = {
        "phrase_id": "sancha_001",
        "text": "I just wanted someone who saw me, not through me",
        "character": "SANCHA_SIREN_V1",
        
        # EPD Vocal Blueprint
        "epd_vocal_blueprint": {
            "vulnerability_level": 0.85,
            "breathiness": 0.6,
            "tension": 0.4,
            "formant_shift": 0
        },
        
        # CCNA Creative Intent Trace
        "creative_intent_trace": {
            "narrative_archetype": "toxic_relationship_vulnerability",
            "cultural_context": "SGV_souldie",
            "emotional_beats": ["hurt", "vulnerability", "resignation"]
        },
        
        # PFA Automation Map
        "pfa_automation_map": {
            "vocal_automation_track": [
                {
                    "timestamp_ms_start": 0.0,
                    "timestamp_ms_end": 800.0,
                    "param": "breathiness",
                    "value_start": 0.5,
                    "value_end": 0.7,
                    "curve": "linear"
                },
                {
                    "timestamp_ms_start": 800.0,
                    "timestamp_ms_end": 1600.0,
                    "param": "tremolo",
                    "value_start": 0.4,
                    "value_end": 0.8,
                    "curve": "exponential"
                },
                {
                    "timestamp_ms_start": 1600.0,
                    "timestamp_ms_end": 3200.0,
                    "param": "pitch_waver",
                    "value_start": 0.2,
                    "value_end": 0.6,
                    "curve": "exponential"
                }
            ]
        }
    }
    
    # Run full pipeline
    print("\n[Running Full Pipeline]")
    print("  → Stage 1: DOPE (Emotional Trajectory Prediction)")
    print("  → Stage 2: PFA (Biomechanical Simulation)")
    print("  → Stage 3: SSS (Cultural Validation)")
    print("  → Stage 4: Recursive Feedback Loop")
    print("  → Stage 5: Learning Engine")
    
    result = await pipeline.run_pipeline(
        soulfire_payload=soulfire_payload,
        phrase_context=["Why do you always", "I trusted you"],
        enable_recursive_feedback=True,
        enable_learning=True
    )
    
    # Validate results
    print("\n[Pipeline Output]")
    assert result is not None
    assert "pipeline_id" in result
    assert "status" in result
    assert "predicted_trajectory" in result
    assert "vocal_biomechanics" in result
    assert "cultural_validation" in result
    assert "performance_feedback" in result  # Note: it's performance_feedback, not feedback_history
    assert "learning_insights" in result
    
    print(f"✓ Pipeline ID: {result['pipeline_id']}")
    print(f"✓ Status: {result['status']}")
    
    # Check trajectory
    traj = result["predicted_trajectory"]
    print(f"\n[Emotional Trajectory]")
    print(f"  Start State: {traj['start_state']}")
    print(f"  End State: {traj['end_state']}")
    print(f"  Peak Intensity: {traj['peak_intensity']:.3f}")
    print(f"  Breakdown Risk: {traj['breakdown_risk']:.3f}")
    
    assert traj["start_state"] in ["vulnerability", "anger", "defiance", "resignation", "hope", "despair"]
    assert 0.0 <= traj["peak_intensity"] <= 1.0
    assert 0.0 <= traj["breakdown_risk"] <= 1.0
    
    # Check biomechanics
    bio = result["vocal_biomechanics"]
    print(f"\n[Vocal Biomechanics]")
    print(f"  Phonation Mode: {result.get('phonation_mode', 'N/A')}")
    print(f"  Subglottal Pressure: {bio['subglottal_pressure_kPa']:.2f} kPa")
    print(f"  Vocal Fold Tension: {bio['vocal_fold_tension']:.3f}")
    print(f"  Jitter: {bio['jitter_percent']:.2f}%")
    print(f"  Shimmer: {bio['shimmer_db']:.2f} dB")
    
    assert 0.8 <= bio["subglottal_pressure_kPa"] <= 3.5
    assert 0.0 <= bio["vocal_fold_tension"] <= 1.0
    
    # Check cultural validation
    val = result["cultural_validation"]
    print(f"\n[Cultural Validation (SSS)]")
    print(f"  Authenticity Score: {val['authenticity_score']:.3f}")
    print(f"  Brand Alignment: {val['brand_alignment']:.3f}")
    print(f"  AI Detection Flags: {val['ai_detection_flags'] or 'None'}")
    
    assert 0.0 <= val["authenticity_score"] <= 1.0
    assert 0.0 <= val["brand_alignment"] <= 1.0
    
    # Check feedback loop
    perf_feedback = result["performance_feedback"]
    print(f"\n[Recursive Feedback Loop]")
    print(f"  Total Adjustments: {perf_feedback['total_adjustments']}")
    print(f"  Avg Emotional Drift: {perf_feedback['avg_emotional_drift']:.3f}")
    print(f"  Avg Vocal Strain: {perf_feedback['avg_vocal_strain']:.3f}")
    
    # Check learning insights
    learning = result["learning_insights"]
    print(f"\n[Learning Engine]")
    print(f"  Status: {learning.get('status', 'active')}")
    
    if "learned_patterns" in learning:
        print(f"  Learned Patterns: {len(learning['learned_patterns'])}")
    
    print("\n" + "="*80)
    print("✓ FULL EMPIRE PIPELINE TEST PASSED")
    print("="*80)


@pytest.mark.asyncio
async def test_empire_pipeline_high_intensity_breakdown():
    """Test Empire Pipeline with high-intensity breakdown scenario"""
    print("\n" + "="*80)
    print("TEST: Empire Pipeline - High-Intensity Breakdown")
    print("="*80)
    
    pipeline = EmpireAudioPipeline()
    
    # High-intensity despair payload
    soulfire_payload = {
        "phrase_id": "sancha_breakdown",
        "text": "I can't... I can't do this anymore <emotional_crack>",
        "character": "SANCHA_SIREN_V1",
        
        "epd_vocal_blueprint": {
            "vulnerability_level": 0.98,
            "breathiness": 0.9,
            "tension": 0.8,
            "formant_shift": -50
        },
        
        "creative_intent_trace": {
            "narrative_archetype": "toxic_relationship_despair_breakdown",
            "cultural_context": "SGV_souldie",
            "emotional_beats": ["despair", "breakdown", "crack", "hopelessness"]
        },
        
        "pfa_automation_map": {
            "vocal_automation_track": [
                {
                    "timestamp_ms_start": 0.0,
                    "timestamp_ms_end": 1000.0,
                    "param": "breathiness",
                    "value_start": 0.8,
                    "value_end": 0.95,
                    "curve": "exponential"
                },
                {
                    "timestamp_ms_start": 1500.0,
                    "timestamp_ms_end": 2500.0,
                    "param": "pitch_waver",
                    "value_start": 0.6,
                    "value_end": 0.9,
                    "curve": "exponential"
                }
            ]
        }
    }
    
    result = await pipeline.run_pipeline(
        soulfire_payload=soulfire_payload,
        phrase_context=["You promised me", "never again", "can't believe"],
        enable_recursive_feedback=True,
        enable_learning=True
    )
    
    traj = result["predicted_trajectory"]
    print(f"✓ Breakdown Risk: {traj['breakdown_risk']:.3f}")
    
    # High intensity should predict elevated breakdown risk
    assert traj["breakdown_risk"] > 0.5, "High-intensity payload should predict breakdown risk"
    assert traj["peak_intensity"] > 0.8, "Peak intensity should be elevated"
    
    print(f"✓ Peak Intensity: {traj['peak_intensity']:.3f} (HIGH)")
    print(f"✓ Emotional Arc: {traj['start_state']} → {traj['end_state']}")
    
    print("\n✓ HIGH-INTENSITY BREAKDOWN TEST PASSED")


@pytest.mark.asyncio
async def test_empire_pipeline_performance_benchmark():
    """Benchmark Empire Pipeline execution time"""
    print("\n" + "="*80)
    print("TEST: Empire Pipeline Performance Benchmark")
    print("="*80)
    
    import time
    
    pipeline = EmpireAudioPipeline()
    
    minimal_payload = {
        "phrase_id": "bench_001",
        "text": "Test phrase",
        "character": "SANCHA_SIREN_V1",
        "epd_vocal_blueprint": {"vulnerability_level": 0.7, "breathiness": 0.5, "tension": 0.3, "formant_shift": 0},
        "creative_intent_trace": {"narrative_archetype": "test", "cultural_context": "SGV", "emotional_beats": []},
        "pfa_automation_map": {
            "vocal_automation_track": [
                {"timestamp_ms_start": 0.0, "timestamp_ms_end": 1000.0, "param": "breathiness", "value_start": 0.5, "value_end": 0.6, "curve": "linear"}
            ]
        }
    }
    
    start = time.time()
    result = await pipeline.run_pipeline(
        soulfire_payload=minimal_payload,
        phrase_context=[],
        enable_recursive_feedback=False,  # Disable for speed
        enable_learning=False
    )
    elapsed_ms = (time.time() - start) * 1000
    
    print(f"✓ Pipeline Execution Time: {elapsed_ms:.2f}ms")
    print(f"  Target: <500ms for production readiness")
    print(f"  Status: {result['status']}")
    
    assert result["status"] in ["success", "completed", "ready", "READY", "NEEDS_REVISION", "CORRECTION_REQUIRED"], \
        f"Pipeline should complete (got status: {result['status']})"
    assert elapsed_ms < 2000, f"Pipeline too slow: {elapsed_ms:.2f}ms (target: <2000ms for dev)"
    
    print("\n✓ PERFORMANCE BENCHMARK PASSED")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
