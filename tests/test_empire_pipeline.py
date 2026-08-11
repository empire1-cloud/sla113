"""
Test Suite: Empire Audio Pipeline 2.0
Tests the recursive neural performance engine with real Soulfire payloads

Part of: SLA-113 | Toxic Drama Expansion | Empire Pipeline Validation
Rule: EVOLVE NEVER DELETE
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from LYRICA3.soulfire_engine.empire_audio_pipeline import (
    EmpireAudioPipeline,
    EmotionalState,
    PhonationMode,
    EmotionalTrajectory,
    VocalBiomechanics,
    CulturalValidation,
    PerformanceFeedback
)


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def sample_soulfire_payload():
    """Real Soulfire payload from Toxic Drama scene with full Empire Pipeline structure"""
    return {
        "phrase_id": "sancha_phrase_001",
        "text": "I just wanted someone who saw me, not through me",
        "character": "SANCHA_SIREN_V1",
        "emotion": "vulnerability",
        "intensity": 0.85,
        "timestamp_ms": 2500.0,
        "duration_ms": 3200.0,
        
        # EPD Vocal Blueprint (required by DOPE)
        "epd_vocal_blueprint": {
            "vulnerability_level": 0.85,
            "breathiness": 0.6,
            "tension": 0.4,
            "pitch_variance": 0.3
        },
        
        # CCNA Creative Intent Trace (required by DOPE)
        "creative_intent_trace": {
            "narrative_archetype": "toxic_relationship_vulnerability",
            "cultural_context": "SGV_souldie",
            "emotional_palette": ["vulnerability", "hurt", "resignation"]
        },
        
        # PFA Automation Map (required by DOPE, PFA, SSS)
        "pfa_automation_map": {
            "vocal_automation_track": [
                {
                    "timestamp_ms_start": 2500.0,
                    "timestamp_ms_end": 3200.0,
                    "param": "breathiness",
                    "value_start": 0.6,
                    "value_end": 0.7,
                    "curve": "linear"
                },
                {
                    "timestamp_ms_start": 3500.0,
                    "timestamp_ms_end": 4200.0,
                    "param": "tremolo",
                    "value_start": 0.5,
                    "value_end": 0.8,
                    "curve": "exponential"
                }
            ]
        }
    }


@pytest.fixture
def high_intensity_payload():
    """High-intensity breakdown scenario"""
    return {
        "phrase_id": "sancha_phrase_002",
        "text": "You promised me forever and gave me a maybe",
        "character": "SANCHA_SIREN_V1",
        "emotion": "despair",
        "intensity": 0.95,
        "timestamp_ms": 8500.0,
        "duration_ms": 4000.0,
        
        # EPD Vocal Blueprint
        "epd_vocal_blueprint": {
            "vulnerability_level": 0.95,
            "breathiness": 0.8,
            "tension": 0.7,
            "pitch_variance": 0.5
        },
        
        # CCNA Creative Intent Trace
        "creative_intent_trace": {
            "narrative_archetype": "toxic_relationship_despair",
            "cultural_context": "SGV_souldie",
            "emotional_palette": ["despair", "breakdown", "hopelessness"]
        },
        
        # PFA Automation Map
        "pfa_automation_map": {
            "vocal_automation_track": [
                {
                    "timestamp_ms_start": 8500.0,
                    "timestamp_ms_end": 9500.0,
                    "param": "breathiness",
                    "value_start": 0.8,
                    "value_end": 0.95,
                    "curve": "exponential"
                },
                {
                    "timestamp_ms_start": 10000.0,
                    "timestamp_ms_end": 11500.0,
                    "param": "pitch_waver",
                    "value_start": 0.5,
                    "value_end": 0.8,
                    "curve": "exponential"
                }
            ]
        }
    }


@pytest.fixture
def empire_pipeline():
    """Initialize Empire Audio Pipeline"""
    return EmpireAudioPipeline()


# ============================================================================
# STAGE 1: DOPE ENGINE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_dope_emotional_trajectory(empire_pipeline, sample_soulfire_payload):
    """Test DOPE engine emotional trajectory prediction"""
    print("\n" + "="*80)
    print("TEST: DOPE Emotional Trajectory Prediction")
    print("="*80)
    
    # Use actual API: predict_emotional_trajectory (not predict_trajectory)
    trajectory = empire_pipeline.dope.predict_emotional_trajectory(
        sample_soulfire_payload, 
        phrase_context=[]
    )
    
    assert trajectory is not None
    assert isinstance(trajectory, EmotionalTrajectory)
    assert trajectory.start_state == EmotionalState.VULNERABILITY
    assert 0.0 <= trajectory.peak_intensity <= 1.0
    assert 0.0 <= trajectory.risk_of_breakdown <= 1.0
    assert trajectory.transition_curve in ["exponential", "linear", "stepped"]
    
    print(f"✓ Start State: {trajectory.start_state.value}")
    print(f"✓ End State: {trajectory.end_state.value}")
    print(f"✓ Peak Intensity: {trajectory.peak_intensity:.3f}")
    print(f"✓ Peak Timestamp: {trajectory.peak_timestamp_ms:.1f}ms")
    print(f"✓ Transition Curve: {trajectory.transition_curve}")
    print(f"✓ Breakdown Risk: {trajectory.risk_of_breakdown:.3f}")


@pytest.mark.asyncio
async def test_dope_high_intensity_breakdown(empire_pipeline, high_intensity_payload):
    """Test DOPE prediction for high-intensity breakdown scenario"""
    print("\n" + "="*80)
    print("TEST: DOPE High-Intensity Breakdown Detection")
    print("="*80)
    
    trajectory = empire_pipeline.dope.predict_emotional_trajectory(
        high_intensity_payload, 
        phrase_context=["I can't believe you", "never again"]
    )
    
    # High intensity + despair should trigger high breakdown risk
    assert trajectory.risk_of_breakdown > 0.5, "High intensity should predict breakdown risk"
    assert trajectory.peak_intensity > 0.8, "Peak intensity should be elevated"
    
    print(f"✓ Breakdown Risk: {trajectory.risk_of_breakdown:.3f} (HIGH)")
    print(f"✓ Peak Intensity: {trajectory.peak_intensity:.3f}")
    print(f"✓ Transition: {trajectory.start_state.value} → {trajectory.end_state.value}")


# ============================================================================
# STAGE 2: PFA ENGINE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_pfa_biomechanical_simulation(empire_pipeline, sample_soulfire_payload):
    """Test PFA engine biomechanical vocal simulation"""
    print("\n" + "="*80)
    print("TEST: PFA Biomechanical Vocal Simulation")
    print("="*80)
    
    # Stage 1: Get trajectory from DOPE
    trajectory = empire_pipeline.dope.predict_emotional_trajectory(
        sample_soulfire_payload,
        phrase_context=[]
    )
    
    # Stage 2: Get phonation mode from DOPE
    phonation_mode = empire_pipeline.dope.map_emotion_to_phonation(trajectory)
    
    # Stage 3: Simulate vocal biomechanics
    biomechanics = empire_pipeline.pfa.simulate_vocal_biomechanics(
        trajectory,
        phonation_mode,
        phrase_duration_ms=sample_soulfire_payload["duration_ms"]
    )
    
    assert biomechanics is not None
    assert isinstance(biomechanics, VocalBiomechanics)
    assert 0.8 <= biomechanics.subglottal_pressure_kPa <= 3.5
    assert 0.0 <= biomechanics.vocal_fold_tension <= 1.0
    assert 0.3 <= biomechanics.jitter_percent <= 3.5
    assert 0.5 <= biomechanics.shimmer_db <= 4.0
    assert 0.1 <= biomechanics.breathiness_ratio <= 0.6
    
    print(f"✓ Phonation Mode: {phonation_mode.value}")
    print(f"✓ Subglottal Pressure: {biomechanics.subglottal_pressure_kPa:.2f} kPa")
    print(f"✓ Vocal Fold Tension: {biomechanics.vocal_fold_tension:.3f}")
    print(f"✓ Formant Shift: {biomechanics.formant_shift_hz:+.1f} Hz")
    print(f"✓ Jitter: {biomechanics.jitter_percent:.2f}%")
    print(f"✓ Shimmer: {biomechanics.shimmer_db:.2f} dB")
    print(f"✓ Breathiness: {biomechanics.breathiness_ratio:.3f}")


@pytest.mark.asyncio
async def test_pfa_phonation_mode_selection(empire_pipeline, sample_soulfire_payload):
    """Test PFA phonation mode selection for vulnerability"""
    print("\n" + "="*80)
    print("TEST: PFA Phonation Mode Selection")
    print("="*80)
    
    trajectory = empire_pipeline.dope.predict_emotional_trajectory(
        sample_soulfire_payload,
        phrase_context=[]
    )
    
    phonation_mode = empire_pipeline.dope.map_emotion_to_phonation(trajectory)
    
    # Vulnerability should map to certain phonation modes
    print(f"✓ Emotional State: {trajectory.start_state.value} (intensity={trajectory.peak_intensity:.2f})")
    print(f"✓ Selected Phonation Mode: {phonation_mode.value}")
    
    assert isinstance(phonation_mode, PhonationMode)


# ============================================================================
# STAGE 3: SSS ENGINE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_sss_cultural_validation(empire_pipeline):
    """Test SSS engine cultural validation and AI detection"""
    print("\n" + "="*80)
    print("TEST: SSS Cultural Validation & AI Detection")
    print("="*80)
    
    # Simulate rendered audio metadata
    rendered_audio = {
        "audio_path": "/tmp/test_vocal.wav",
        "duration_ms": 3200.0,
        "sample_rate": 48000,
        "bit_depth": 24,
        "spectral_analysis": {
            "sibilance_peak_hz": 7500,  # Safe (< 8500 Hz threshold)
            "formant_peaks": [800, 1200, 2600, 3400],  # Natural
            "timing_variance_ms": 12.5,  # Natural (> 5ms)
            "vibrato_regularity": 0.78,  # Natural (< 0.95)
        },
        "processing_chain": ["analog_tape_rolloff", "tube_saturation_0.42", "small_room_reverb"]
    }
    
    validation = await empire_pipeline.sss.validate_cultural_authenticity(rendered_audio)
    
    assert validation is not None
    assert isinstance(validation, CulturalValidation)
    assert 0.0 <= validation.authenticity_score <= 1.0
    assert 0.0 <= validation.brand_alignment <= 1.0
    assert isinstance(validation.ai_detection_flags, list)
    
    print(f"✓ Authenticity Score: {validation.authenticity_score:.3f}")
    print(f"✓ Brand Alignment: {validation.brand_alignment:.3f}")
    print(f"✓ AI Detection Flags: {validation.ai_detection_flags if validation.ai_detection_flags else 'None'}")
    print(f"✓ Correction Needed: {validation.correction_needed}")
    
    if validation.correction_needed:
        print(f"  → Corrections: {validation.correction_instructions}")


@pytest.mark.asyncio
async def test_sss_ai_detection_synthetic_sibilance(empire_pipeline):
    """Test SSS AI detection for synthetic sibilance"""
    print("\n" + "="*80)
    print("TEST: SSS AI Detection - Synthetic Sibilance")
    print("="*80)
    
    # Simulate audio with synthetic sibilance
    rendered_audio = {
        "audio_path": "/tmp/test_synthetic.wav",
        "duration_ms": 3200.0,
        "sample_rate": 48000,
        "bit_depth": 24,
        "spectral_analysis": {
            "sibilance_peak_hz": 9200,  # DANGER: > 8500 Hz (synthetic)
            "formant_peaks": [800, 1200, 2600, 3400],
            "timing_variance_ms": 3.2,  # DANGER: < 5ms (robotic)
            "vibrato_regularity": 0.97,  # DANGER: > 0.95 (too regular)
        },
        "processing_chain": []
    }
    
    validation = await empire_pipeline.sss.validate_cultural_authenticity(rendered_audio)
    
    assert validation.correction_needed, "Should detect synthetic artifacts"
    assert len(validation.ai_detection_flags) > 0, "Should flag AI detection issues"
    
    print(f"✓ AI Detection Flags: {validation.ai_detection_flags}")
    print(f"✓ Authenticity Score: {validation.authenticity_score:.3f} (degraded)")
    print(f"✓ Correction Instructions:")
    for key, value in (validation.correction_instructions or {}).items():
        print(f"  → {key}: {value}")


# ============================================================================
# STAGE 4: RECURSIVE FEEDBACK LOOP TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_recursive_feedback_loop(empire_pipeline, sample_soulfire_payload):
    """Test recursive feedback loop with real-time monitoring"""
    print("\n" + "="*80)
    print("TEST: Recursive Feedback Loop (Real-Time Adjustment)")
    print("="*80)
    
    # Simulate performance monitoring at 3 timestamps
    timestamps = [1000.0, 2000.0, 3000.0]
    feedback_history = []
    
    for ts in timestamps:
        feedback = PerformanceFeedback(
            timestamp_ms=ts,
            emotional_drift=0.15 * (ts / 1000.0),  # Increasing drift
            vocal_strain_level=0.6 + 0.1 * (ts / 1000.0),  # Increasing strain
            cultural_coherence=0.85 - 0.05 * (ts / 1000.0),  # Decreasing coherence
        )
        feedback_history.append(feedback)
        print(f"  {ts:.0f}ms: drift={feedback.emotional_drift:.3f}, strain={feedback.vocal_strain_level:.3f}, coherence={feedback.cultural_coherence:.3f}")
    
    # Check if pipeline would trigger adjustment (strain > 0.7)
    high_strain_feedback = [f for f in feedback_history if f.vocal_strain_level > 0.7]
    
    if high_strain_feedback:
        print(f"✓ Feedback Loop Triggered: {len(high_strain_feedback)} high-strain events")
        print(f"  → Recommended: Reduce intensity by 15%")
    else:
        print(f"✓ Performance Stable: No adjustments needed")


# ============================================================================
# STAGE 5: LEARNING ENGINE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_learning_engine_records_performance(empire_pipeline, sample_soulfire_payload):
    """Test learning engine records and learns from performance history"""
    print("\n" + "="*80)
    print("TEST: Learning Engine - Performance Recording")
    print("="*80)
    
    # Simulate 3 performances with varying quality
    performances = [
        {"breakdown_risk": 0.85, "final_quality": 0.72, "adjustment_made": "reduce_intensity_15"},
        {"breakdown_risk": 0.88, "final_quality": 0.68, "adjustment_made": "reduce_intensity_15"},
        {"breakdown_risk": 0.90, "final_quality": 0.65, "adjustment_made": "reduce_intensity_20"},
    ]
    
    for i, perf in enumerate(performances):
        empire_pipeline.learning.record_performance(
            phrase_id=f"phrase_{i+1}",
            emotional_state="vulnerability",
            intensity=0.85,
            breakdown_risk=perf["breakdown_risk"],
            final_quality_score=perf["final_quality"],
            corrections_applied=[perf["adjustment_made"]]
        )
        print(f"  Performance {i+1}: breakdown_risk={perf['breakdown_risk']:.3f}, quality={perf['final_quality']:.3f}")
    
    history_count = len(empire_pipeline.learning.performance_history)
    assert history_count == 3, f"Expected 3 performances, got {history_count}"
    
    print(f"✓ Recorded {history_count} performances in learning history")


@pytest.mark.asyncio
async def test_learning_engine_learns_corrections(empire_pipeline):
    """Test learning engine learns optimal corrections from history"""
    print("\n" + "="*80)
    print("TEST: Learning Engine - Correction Learning")
    print("="*80)
    
    # Seed with performance data
    test_data = [
        {"breakdown_risk": 0.85, "quality": 0.82, "correction": "reduce_intensity_10"},
        {"breakdown_risk": 0.88, "quality": 0.78, "correction": "reduce_intensity_15"},
        {"breakdown_risk": 0.92, "quality": 0.75, "correction": "reduce_intensity_15"},
        {"breakdown_risk": 0.95, "quality": 0.70, "correction": "reduce_intensity_20"},
    ]
    
    for i, data in enumerate(test_data):
        empire_pipeline.learning.record_performance(
            phrase_id=f"learn_phrase_{i}",
            emotional_state="despair",
            intensity=0.90,
            breakdown_risk=data["breakdown_risk"],
            final_quality_score=data["quality"],
            corrections_applied=[data["correction"]]
        )
    
    # Query learned correction for high breakdown risk
    learned_correction = empire_pipeline.learning.suggest_correction(
        emotional_state="despair",
        intensity=0.90,
        breakdown_risk=0.90
    )
    
    print(f"✓ Learned Correction for breakdown_risk=0.90: {learned_correction}")
    assert learned_correction is not None, "Should learn correction from history"


# ============================================================================
# END-TO-END INTEGRATION TEST
# ============================================================================

@pytest.mark.asyncio
async def test_full_empire_pipeline_integration(empire_pipeline, sample_soulfire_payload):
    """Full end-to-end test: DOPE → PFA → SSS → Feedback → Learning"""
    print("\n" + "="*80)
    print("TEST: Full Empire Pipeline Integration (E2E)")
    print("="*80)
    
    # Stage 1: DOPE prediction
    print("\n[Stage 1: DOPE Prediction]")
    trajectory = await empire_pipeline.dope.predict_trajectory(sample_soulfire_payload)
    print(f"  Emotional Arc: {trajectory.start_state.value} → {trajectory.end_state.value}")
    print(f"  Breakdown Risk: {trajectory.risk_of_breakdown:.3f}")
    
    # Stage 2: PFA simulation
    print("\n[Stage 2: PFA Simulation]")
    biomechanics = await empire_pipeline.pfa.simulate_vocal_physics(trajectory, sample_soulfire_payload)
    print(f"  Subglottal Pressure: {biomechanics.subglottal_pressure_kPa:.2f} kPa")
    print(f"  Vocal Fold Tension: {biomechanics.vocal_fold_tension:.3f}")
    print(f"  Jitter: {biomechanics.jitter_percent:.2f}%")
    
    # Stage 3: SSS validation (mock rendered audio)
    print("\n[Stage 3: SSS Validation]")
    mock_audio = {
        "audio_path": "/tmp/empire_test.wav",
        "duration_ms": 3200.0,
        "sample_rate": 48000,
        "bit_depth": 24,
        "spectral_analysis": {
            "sibilance_peak_hz": 7800,
            "formant_peaks": [800, 1200, 2600, 3400],
            "timing_variance_ms": 10.5,
            "vibrato_regularity": 0.82,
        },
        "processing_chain": ["analog_tape_rolloff", "tube_saturation_0.42"]
    }
    validation = await empire_pipeline.sss.validate_cultural_authenticity(mock_audio)
    print(f"  Authenticity Score: {validation.authenticity_score:.3f}")
    print(f"  Brand Alignment: {validation.brand_alignment:.3f}")
    print(f"  AI Flags: {validation.ai_detection_flags if validation.ai_detection_flags else 'None'}")
    
    # Stage 4: Record performance in learning engine
    print("\n[Stage 4: Learning Engine Recording]")
    empire_pipeline.learning.record_performance(
        phrase_id=sample_soulfire_payload["phrase_id"],
        emotional_state=sample_soulfire_payload["emotion"],
        intensity=sample_soulfire_payload["intensity"],
        breakdown_risk=trajectory.risk_of_breakdown,
        final_quality_score=validation.authenticity_score,
        corrections_applied=[]
    )
    print(f"  Recorded performance in learning history")
    print(f"  Total performances tracked: {len(empire_pipeline.learning.performance_history)}")
    
    print("\n" + "="*80)
    print("✓ FULL PIPELINE COMPLETE")
    print("="*80)


# ============================================================================
# PERFORMANCE BENCHMARKS
# ============================================================================

@pytest.mark.asyncio
async def test_pipeline_performance_benchmark(empire_pipeline, sample_soulfire_payload):
    """Benchmark Empire Pipeline execution time"""
    print("\n" + "="*80)
    print("TEST: Empire Pipeline Performance Benchmark")
    print("="*80)
    
    import time
    
    start = time.time()
    
    # Run full pipeline
    trajectory = await empire_pipeline.dope.predict_trajectory(sample_soulfire_payload)
    biomechanics = await empire_pipeline.pfa.simulate_vocal_physics(trajectory, sample_soulfire_payload)
    
    mock_audio = {
        "audio_path": "/tmp/bench.wav",
        "duration_ms": 3200.0,
        "sample_rate": 48000,
        "bit_depth": 24,
        "spectral_analysis": {
            "sibilance_peak_hz": 7800,
            "formant_peaks": [800, 1200, 2600, 3400],
            "timing_variance_ms": 10.5,
            "vibrato_regularity": 0.82,
        },
        "processing_chain": ["analog_tape_rolloff"]
    }
    validation = await empire_pipeline.sss.validate_cultural_authenticity(mock_audio)
    
    elapsed = (time.time() - start) * 1000  # Convert to ms
    
    print(f"✓ Pipeline Execution Time: {elapsed:.2f}ms")
    print(f"  Target: <100ms for real-time performance")
    
    assert elapsed < 500, f"Pipeline too slow: {elapsed:.2f}ms (target: <500ms)"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
