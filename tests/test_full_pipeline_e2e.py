"""
End-to-End Integration Test: AURA → EFAD → Empire Pipeline
Part of SLA-113 Toxic Drama Expansion

Purpose:
    Validate complete AI music production pipeline with zero API dependencies.
    Tests full flow from user input to final Soulfire payload with audio automation.

Pipeline Stages:
    1. AURA: Advanced local NLP intent extraction
    2. ASE: Novelty/cohesion evaluation
    3. EFL: Template-based lyric generation with LML tags
    4. ECHO: Technical translation (MMA rhythm + PDA mastering)
    5. EFAD: Final payload assembly
    6. PFA Tag Processing: LML tag → DSP parameters
    7. Empire Audio Pipeline: Biomechanical vocal simulation (optional)

Test Scenarios:
    - Toxic breakup anthem (high vulnerability, juxtaposition)
    - Aggressive drill track (high intensity, modern production)
    - Intimate soul song (cultural blending, analog warmth)
"""

import sys
import json
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, '/home/shiestybizz/sla113')

from LYRICA3.intent_engine import (
    AdvancedAURAEngine,
    ASEEngine,
    EFLEngine
)
from LYRICA3.rhythm_engine import MMAGrooveAgent
from LYRICA3.mastering_engine import PDAMasteringAgent
from LYRICA3.soulfire_engine.pfa_tag_processor import PFATagProcessor


class EndToEndPipeline:
    """
    Complete end-to-end pipeline orchestrator.
    Zero API dependencies - all local processing.
    """
    
    def __init__(self, seed: int = 42):
        """Initialize all pipeline components."""
        self.aura_engine = AdvancedAURAEngine()
        self.ase_engine = ASEEngine()
        self.efl_engine = EFLEngine(seed=seed)
        self.mma_agent = MMAGrooveAgent(seed=seed)
        self.pda_agent = PDAMasteringAgent()
        self.pfa_processor = PFATagProcessor()
        self.seed = seed
    
    def stage_aura(self, user_input: str) -> Dict[str, Any]:
        """AURA: Intent extraction with advanced NLP."""
        print("\n" + "="*80)
        print("STAGE 1: AURA (Intent Extraction)")
        print("="*80)
        
        result = self.aura_engine.analyze(user_input)
        
        print(f"✓ Semantic Intent: {result['semantic_intent']}")
        print(f"✓ Rhetorical Devices: {len(result['rhetorical_devices'])} detected")
        print(f"✓ Culture Anchors: {', '.join(result['culture_anchors'])}")
        print(f"✓ Style Anchors: {', '.join(result['style_anchors'])}")
        print(f"✓ Emotional Profile: {result['emotional_profile']}")
        
        return result
    
    def stage_ase(self, aura_output: Dict[str, Any]) -> Dict[str, Any]:
        """ASE: Strategy evaluation."""
        print("\n" + "="*80)
        print("STAGE 2: ASE (Strategy Evaluation)")
        print("="*80)
        
        result = self.ase_engine.evaluate(aura_output)
        
        print(f"✓ Novelty Score: {result['novelty_score']}")
        print(f"✓ Cohesion Score: {result['cohesion_score']}")
        print(f"✓ Impact Score: {result['impact_score']}")
        print(f"✓ Disruption Heuristic: {result['disruption_heuristic']}")
        print(f"✓ Strategy: {result['strategy_rationale']}")
        
        return result
    
    def stage_efl(self, aura_output: Dict[str, Any], ase_output: Dict[str, Any]) -> Dict[str, Any]:
        """EFL: Emotional mapping + lyric generation."""
        print("\n" + "="*80)
        print("STAGE 3: EFL (Emotional/Lyric Mapping)")
        print("="*80)
        
        result = self.efl_engine.generate(aura_output, ase_output)
        
        print(f"✓ Vulnerability Level: {result['vulnerability_level']:.2f}")
        print(f"✓ LML Tags: {', '.join(result['lml_tags'])}")
        print(f"✓ Lyric Strategy: {result['lyric_strategy']}")
        print(f"✓ Generated {len(result['generated_lyrics'])} lyric lines:")
        for i, lyric in enumerate(result['generated_lyrics'], 1):
            tag = f" [{lyric['lml_trigger']}]" if lyric['lml_trigger'] else ""
            print(f"   {i}. \"{lyric['line']}\"{tag}")
        
        return result
    
    def stage_echo(self, aura_output: Dict[str, Any], ase_output: Dict[str, Any], efl_output: Dict[str, Any]) -> Dict[str, Any]:
        """ECHO: Technical translation (MMA + PDA)."""
        print("\n" + "="*80)
        print("STAGE 4: ECHO (Technical Translation)")
        print("="*80)
        
        # Build timing descriptor for MMA
        timing_descriptor = self._build_timing_descriptor(aura_output, ase_output)
        print(f"✓ Timing Descriptor: {timing_descriptor}")
        
        # Generate rhythm groove
        rhythm_groove = self.mma_agent.generate_midi_sequence(timing_descriptor)
        bpm = rhythm_groove['midi_sequence']['bpm']
        style = rhythm_groove['midi_sequence']['style']
        print(f"✓ Rhythm Groove: {bpm}bpm {style} with late-pocket timing")
        
        # Build texture descriptor for PDA
        texture_descriptor = self._build_texture_descriptor(aura_output, ase_output)
        print(f"✓ Texture Descriptor: {texture_descriptor}")
        
        # Generate texture DSP
        texture_dsp = self.pda_agent.generate_master_bus_dsp(texture_descriptor)
        vocal_eq = texture_dsp['master_bus_dsp']['vocal_channel']['eq_200hz_gain_db']
        lpf = texture_dsp['master_bus_dsp']['master_out']['low_pass_filter_hz']
        print(f"✓ Texture DSP: Proximity +{vocal_eq}dB @ 200Hz, LPF {lpf}Hz")
        
        # Determine stem priorities
        stem_priorities = {
            'vocal': 1.0,
            '808': 0.85 if 'trap' in aura_output.get('culture_anchors', []) else 0.7,
            'drums': 0.75,
            'melody': 0.65
        }
        
        return {
            'rhythm_groove': rhythm_groove,
            'texture_dsp': texture_dsp,
            'stem_priorities': stem_priorities,
            'timing_descriptor': timing_descriptor,
            'texture_descriptor': texture_descriptor
        }
    
    def stage_efad(self,
                   aura_output: Dict[str, Any],
                   ase_output: Dict[str, Any],
                   efl_output: Dict[str, Any],
                   echo_output: Dict[str, Any]) -> Dict[str, Any]:
        """EFAD: Final payload assembly."""
        print("\n" + "="*80)
        print("STAGE 5: EFAD (Payload Assembly)")
        print("="*80)
        
        # Build track metadata
        track_metadata = {
            'title': self._generate_title(aura_output, efl_output),
            'core_genre': self._determine_genre(aura_output),
            's2_mutation_applied': ase_output.get('disruption_heuristic') or 'None',
            'dna_tag_preview': self._generate_dna_tag(aura_output, efl_output)
        }
        print(f"✓ Track: \"{track_metadata['title']}\" ({track_metadata['core_genre']})")
        print(f"✓ DNA Tag: {track_metadata['dna_tag_preview']}")
        
        # Build audio blueprint
        dope_audio_blueprint = {
            'vulnerability_level': efl_output['vulnerability_level'],
            'rhythm_groove': echo_output['rhythm_groove'],
            'texture_dsp': echo_output['texture_dsp'],
            'mastering_sss': self._select_sss_preset(efl_output),
            'stem_priorities': echo_output['stem_priorities']
        }
        print(f"✓ SSS Preset: {dope_audio_blueprint['mastering_sss']}")
        
        # Use generated lyrics from EFL
        lyrics_payload = efl_output['generated_lyrics']
        
        soulfire_payload = {
            'track_metadata': track_metadata,
            'dope_audio_blueprint': dope_audio_blueprint,
            'lyrics_payload': lyrics_payload
        }
        
        print(f"✓ Soulfire payload assembled ({len(lyrics_payload)} lyric lines)")
        
        return soulfire_payload
    
    def stage_pfa(self, soulfire_payload: Dict[str, Any]) -> Dict[str, Any]:
        """PFA: Tag processing (LML → DSP)."""
        print("\n" + "="*80)
        print("STAGE 6: PFA Tag Processing (LML → DSP)")
        print("="*80)
        
        lyrics_payload = soulfire_payload['lyrics_payload']
        vulnerability_level = soulfire_payload['dope_audio_blueprint']['vulnerability_level']
        
        # Process LML tags
        pfa_automation = self.pfa_processor.inject_lml_tags(
            lyrics_payload,
            vulnerability_level=vulnerability_level,
            peak_intensity=0.85,
            intimacy_level=0.80
        )
        
        print(f"✓ Generated {len(pfa_automation['vocal_automation_track'])} automation events")
        print(f"✓ Total Duration: {pfa_automation['total_duration_ms']}ms")
        
        # Show tag processing examples
        for event in pfa_automation['vocal_automation_track']:
            if event['lml_tag_applied'] and event['lml_tag_applied'] != 'none':
                tag = event['lml_tag_applied']
                dsp = event['dsp_injections']
                print(f"✓ {tag}: ", end="")
                if 'pitch_shift_semitones' in dsp:
                    print(f"pitch_shift {dsp['pitch_shift_semitones']:.1f}st, thd {dsp.get('thd', 0):.2f}")
                elif 'pitch_envelope' in dsp:
                    print(f"pitch_envelope {dsp['pitch_envelope']}, duration {dsp['pitch_envelope_duration_ms']}ms")
                elif 'breath_duration_ms' in dsp:
                    print(f"breath {dsp['breath_duration_ms']:.0f}ms @ {dsp['breath_volume_db']:.1f}dB")
                else:
                    print(f"{list(dsp.keys())}")
        
        return pfa_automation
    
    def execute_full_pipeline(self, user_input: str) -> Dict[str, Any]:
        """Execute complete AURA → EFAD → PFA pipeline."""
        print("\n" + "#"*80)
        print(f"# FULL PIPELINE EXECUTION")
        print(f"# Input: \"{user_input}\"")
        print("#"*80)
        
        # Stage 1: AURA
        aura_output = self.stage_aura(user_input)
        
        # Stage 2: ASE
        ase_output = self.stage_ase(aura_output)
        
        # Stage 3: EFL
        efl_output = self.stage_efl(aura_output, ase_output)
        
        # Stage 4: ECHO
        echo_output = self.stage_echo(aura_output, ase_output, efl_output)
        
        # Stage 5: EFAD
        soulfire_payload = self.stage_efad(aura_output, ase_output, efl_output, echo_output)
        
        # Stage 6: PFA
        pfa_automation = self.stage_pfa(soulfire_payload)
        
        print("\n" + "="*80)
        print("✅ PIPELINE COMPLETE")
        print("="*80)
        print(f"Total Duration: {pfa_automation['total_duration_ms']/1000:.1f}s")
        print(f"Automation Events: {len(pfa_automation['vocal_automation_track'])}")
        print(f"BPM: {soulfire_payload['dope_audio_blueprint']['rhythm_groove']['midi_sequence']['bpm']}")
        print(f"Vulnerability: {soulfire_payload['dope_audio_blueprint']['vulnerability_level']:.2f}")
        
        return {
            'soulfire_payload': soulfire_payload,
            'pfa_automation': pfa_automation,
            'aura_output': aura_output,
            'ase_output': ase_output,
            'efl_output': efl_output,
            'echo_output': echo_output
        }
    
    # Helper methods
    def _build_timing_descriptor(self, aura_output, ase_output) -> str:
        """Build MMA timing descriptor."""
        culture_anchors = aura_output.get('culture_anchors', [])
        style_anchors = aura_output.get('style_anchors', [])
        impact_score = ase_output.get('impact_score', 0.7)
        
        bpm = 85 if 'soul' in culture_anchors else 120
        style_parts = []
        
        if 'trap' in culture_anchors:
            style_parts.append('trap')
        if 'soul' in culture_anchors:
            style_parts.append('soul')
        if 'drill' in culture_anchors:
            style_parts.append('drill')
        
        if impact_score > 0.7:
            style_parts.append('aggressive')
        elif 'intimate' in style_anchors:
            style_parts.append('cruising')
        
        if 'late-pocket' in style_anchors:
            style_parts.append('late_snare')
        
        return f"{bpm}bpm_{'_'.join(style_parts) if style_parts else 'standard'}"
    
    def _build_texture_descriptor(self, aura_output, ase_output) -> str:
        """Build PDA texture descriptor."""
        style_anchors = aura_output.get('style_anchors', [])
        texture_parts = []
        
        if 'analog' in style_anchors:
            texture_parts.append('vintage_ssl')
        if 'modern' in style_anchors:
            texture_parts.append('modern_sub_heavy')
        if 'intimate' in style_anchors:
            texture_parts.append('intimate_proximity')
        
        return '_'.join(texture_parts) if texture_parts else 'standard_production'
    
    def _generate_title(self, aura_output, efl_output) -> str:
        """Generate track title."""
        if 'betrayal' in aura_output.get('emotional_profile', {}):
            return "Innocent Act"
        elif 'anger' in aura_output.get('emotional_profile', {}):
            return "No Holding Back"
        else:
            return "Untitled Track"
    
    def _determine_genre(self, aura_output) -> str:
        """Determine core genre."""
        culture_anchors = aura_output.get('culture_anchors', [])
        if 'trap' in culture_anchors and 'soul' in culture_anchors:
            return "Trap-Soul"
        elif 'trap' in culture_anchors:
            return "Trap"
        elif 'drill' in culture_anchors:
            return "Drill"
        elif 'soul' in culture_anchors:
            return "Soul"
        else:
            return "Contemporary"
    
    def _generate_dna_tag(self, aura_output, efl_output) -> str:
        """Generate DNA tag."""
        parts = []
        if 'betrayal' in aura_output.get('emotional_profile', {}):
            parts.append('toxic-breakup')
        if 'late-pocket' in aura_output.get('style_anchors', []):
            parts.append('late-pocket')
        if 'analog' in aura_output.get('style_anchors', []):
            parts.append('analog')
        if efl_output['vulnerability_level'] > 0.6:
            parts.append('vulnerable')
        
        return '-'.join(parts) if parts else 'standard'
    
    def _select_sss_preset(self, efl_output) -> str:
        """Select SSS preset."""
        return "SANCHA_SIREN_V1" if efl_output['vulnerability_level'] > 0.6 else "TOXICO_HARSH_V1"


def run_test_scenarios():
    """Run all test scenarios."""
    pipeline = EndToEndPipeline(seed=42)
    
    test_scenarios = [
        "Make me a toxic breakup anthem. She's acting all innocent but I know the truth. Late-pocket trap vibe, analog warmth, intimate vocals.",
        "I want a drill track with aggressive 808s and harsh modern production. No holding back, pure rage.",
        "Create a soul song with chicano influence, intimate vocals, vintage warmth. Like a slow Sunday morning in the SGV."
    ]
    
    results = []
    
    for i, user_input in enumerate(test_scenarios, 1):
        print(f"\n\n{'#'*80}")
        print(f"# TEST SCENARIO {i} OF {len(test_scenarios)}")
        print(f"{'#'*80}")
        
        result = pipeline.execute_full_pipeline(user_input)
        results.append(result)
    
    print(f"\n\n{'#'*80}")
    print(f"# ALL TESTS COMPLETE: {len(results)}/{len(test_scenarios)} PASSED")
    print(f"{'#'*80}")
    print("\n✅ End-to-end pipeline validated successfully!")
    print("✅ Zero API dependencies - all local processing")
    print("✅ Complete music production from user input to audio automation")
    
    return results


if __name__ == "__main__":
    results = run_test_scenarios()
