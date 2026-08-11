"""
Nemotron Combinator SSS Extension
Integrates SSS (Soulfire Sonic Sculpting) Presets with Combinator mixing stage

Part of: SLA-113 | Lyrica3 Soulfire Engine | Toxic Drama Expansion
Rule: EVOLVE NEVER DELETE - Extends combinator.py without modifying it

Integration:
- Applies SANCHA_SIREN_V1 reverb to Sancha's lead vocal
- Applies TOXICO_HARSH_V1 reverb to Toxico's ad-lib stem
- Implements sidechain compression (TOXICO_PRIME → SANCHA_SIREN_V1)
- Timing synchronization with PFA + ad-lib timestamps
"""

import uuid
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.services.nemotron.combinator import Combinator, MasteringChain
from LYRICA3.soulfire_engine.sss_presets import (
    SANCHA_SIREN_PRESET,
    TOXICO_PRIME_PRESET,
    SSSPresetManager
)


class SidechainEnvelopeGenerator:
    """
    Generates sidechain compression envelope from ad-lib timestamps.
    Calculates gain reduction curve based on Toxico's voice activity.
    """
    
    @classmethod
    def build_envelope(cls, adlib_clips: List[Dict[str, Any]], 
                       sidechain_config: Dict[str, Any],
                       duration_ms: float) -> Dict[str, Any]:
        """
        Build sidechain compression envelope from ad-lib timestamps.
        
        Args:
            adlib_clips: List of ad-lib clip specs from Nemotron bridge
            sidechain_config: Sidechain compression parameters from SSS preset
            duration_ms: Total duration of the track
            
        Returns:
            Sidechain envelope with automation points
        """
        threshold_db = sidechain_config.get("threshold_db", -24)
        ratio = float(sidechain_config.get("ratio", "4:1").split(":")[0])
        attack_ms = sidechain_config.get("attack_ms", 5)
        release_ms = sidechain_config.get("release_ms", 150)
        knee_db = sidechain_config.get("knee_db", 6)
        
        # Build automation points for gain reduction
        automation_points = []
        
        for clip in adlib_clips:
            timestamp_ms = clip.get("timestamp_ms", 0)
            clip_duration_ms = clip.get("duration_ms", 500)
            intensity = clip.get("intensity", 0.7)
            
            # Calculate input level from intensity (normalized)
            # Assume intensity maps to dBFS level: 0.0 → -inf dB, 1.0 → -6 dB
            input_db = -60 + (intensity * 54)  # Maps 0.0→-60dB, 1.0→-6dB
            
            # Calculate gain reduction amount
            if input_db > threshold_db:
                # Soft knee compression
                overshoot_db = input_db - threshold_db
                if overshoot_db < knee_db:
                    # Soft knee region (gradual compression)
                    gain_reduction_db = (overshoot_db ** 2) / (2 * knee_db * ratio)
                else:
                    # Full compression (past knee)
                    gain_reduction_db = overshoot_db / ratio
                
                # Clamp gain reduction
                gain_reduction_db = min(gain_reduction_db, 20)  # Max 20dB reduction
            else:
                gain_reduction_db = 0.0
            
            # Build envelope: attack → hold → release
            # Attack phase
            automation_points.append({
                "time_ms": timestamp_ms,
                "gain_reduction_db": 0.0,
                "phase": "pre_attack"
            })
            
            # Peak compression (after attack)
            automation_points.append({
                "time_ms": timestamp_ms + attack_ms,
                "gain_reduction_db": gain_reduction_db,
                "phase": "compression_peak"
            })
            
            # Hold during clip duration
            automation_points.append({
                "time_ms": timestamp_ms + clip_duration_ms,
                "gain_reduction_db": gain_reduction_db,
                "phase": "compression_hold"
            })
            
            # Release phase
            automation_points.append({
                "time_ms": timestamp_ms + clip_duration_ms + release_ms,
                "gain_reduction_db": 0.0,
                "phase": "release_complete"
            })
        
        # Sort by timestamp
        automation_points.sort(key=lambda x: x["time_ms"])
        
        # Merge overlapping compression events (keep max reduction)
        merged_points = cls._merge_overlapping_events(automation_points)
        
        return {
            "envelope_id": f"sidechain_envelope_{uuid.uuid4().hex[:8]}",
            "source": "TOXICO_PRIME",
            "target": "SANCHA_SIREN_V1_REVERB_TAIL",
            "duration_ms": duration_ms,
            "automation_points": merged_points,
            "total_points": len(merged_points),
            "sidechain_config": sidechain_config,
            "status": "ready"
        }
    
    @classmethod
    def _merge_overlapping_events(cls, automation_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merge overlapping compression events, keeping maximum gain reduction.
        
        Args:
            automation_points: List of automation points sorted by time
            
        Returns:
            Merged automation points
        """
        if not automation_points:
            return []
        
        merged = []
        current_max_reduction = 0.0
        
        for point in automation_points:
            time_ms = point["time_ms"]
            reduction = point["gain_reduction_db"]
            
            # Update current max reduction
            current_max_reduction = max(current_max_reduction, reduction)
            
            # Add point with current max reduction
            merged.append({
                **point,
                "gain_reduction_db": current_max_reduction
            })
            
            # Decay max reduction over time (natural release)
            # If we hit a release_complete phase, reset max
            if point.get("phase") == "release_complete" and reduction == 0.0:
                current_max_reduction = 0.0
        
        return merged


class CombinatorSSS:
    """
    SSS-Enhanced Combinator for Toxic Drama mixing.
    Extends base Combinator with SSS preset integration and sidechain compression.
    
    Rule: EVOLVE NEVER DELETE - This is an extension, not a replacement.
    """
    
    @classmethod
    def combine_with_sss(cls, orchestration: Dict[str, Any],
                         adlib_stem: Optional[Dict[str, Any]] = None,
                         output_path: str = "/tmp/nemotron/output_sss.wav") -> Dict[str, Any]:
        """
        Combine orchestration with SSS presets applied.
        
        Args:
            orchestration: Standard Nemotron orchestration from StemOrchestrator
            adlib_stem: Optional ad-lib stem from NemotronAdLibBridge
            output_path: Output file path
            
        Returns:
            Enhanced combinator result with SSS processing
        """
        # Start with base combinator result
        base_result = Combinator.combine(orchestration, output_path)
        
        # Get SSS preset manager
        preset_manager = SSSPresetManager()
        
        # Load presets
        sancha_preset = preset_manager.get_preset("SANCHA_SIREN_V1")
        toxico_preset = preset_manager.get_preset("TOXICO_HARSH_V1")
        
        # Build SSS processing chain
        sss_chain = {
            "sancha_vocal": cls._build_vocal_sss_chain(
                orchestration.get("vocal", {}),
                sancha_preset
            ),
            "toxico_adlib": None,
            "sidechain_envelope": None
        }
        
        # If ad-lib stem provided, add Toxico processing + sidechain
        if adlib_stem:
            sss_chain["toxico_adlib"] = cls._build_adlib_sss_chain(
                adlib_stem,
                toxico_preset
            )
            
            # Build sidechain compression envelope
            sidechain_config = sancha_preset["post_processing"]["sidechain_compression"]
            adlib_clips = adlib_stem.get("clips", [])
            duration_ms = base_result.get("duration_ms", 0)
            
            sss_chain["sidechain_envelope"] = SidechainEnvelopeGenerator.build_envelope(
                adlib_clips=adlib_clips,
                sidechain_config=sidechain_config,
                duration_ms=duration_ms
            )
        
        # Build enhanced mastering chain
        enhanced_chain = cls._build_enhanced_mastering_chain(
            base_result.get("mastering_chain", {}),
            sss_chain,
            orchestration.get("bpm", 90)
        )
        
        return {
            **base_result,
            "combinator_id": f"comb_sss_{uuid.uuid4().hex[:8]}",
            "sss_processing": sss_chain,
            "mastering_chain": enhanced_chain,
            "provider": "nemotron_combinator_sss",
            "status": "combined_with_sss"
        }
    
    @classmethod
    def _build_vocal_sss_chain(cls, vocal_stem: Dict[str, Any],
                               preset: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build SSS processing chain for Sancha's lead vocal.
        
        Args:
            vocal_stem: Vocal stem from orchestration
            preset: SANCHA_SIREN_V1 preset
            
        Returns:
            SSS processing chain for vocal
        """
        reverb_params = preset["reverb"]["params"]
        post_processing = preset["post_processing"]
        
        return {
            "stem_id": vocal_stem.get("stem_id", ""),
            "preset_id": preset["preset_id"],
            "processing_chain": [
                # Stage 1: Pre-reverb EQ (clean up input)
                {
                    "stage": "eq",
                    "type": "pre_reverb",
                    "bands": [
                        {
                            "type": "low_cut",
                            "frequency_hz": post_processing["eq"]["low_cut"]["frequency_hz"],
                            "slope": post_processing["eq"]["low_cut"]["slope"],
                            "description": "Remove low-end rumble before reverb"
                        }
                    ]
                },
                
                # Stage 2: Convolution Reverb (Siren wash)
                {
                    "stage": "convolution_reverb",
                    "impulse_response": preset["reverb"]["impulse_response"],
                    "params": {
                        "decay_ms": reverb_params["decay_ms"],
                        "pre_delay_ms": reverb_params["pre_delay_ms"],
                        "wet_dry_ratio": reverb_params["wet_dry_ratio"],
                        "description": f"Long haunting reverb ({reverb_params['decay_ms']}ms decay)"
                    },
                    "reverb_bus_id": "SANCHA_SIREN_REVERB_BUS"
                },
                
                # Stage 3: Post-reverb EQ (shape reverb tail)
                {
                    "stage": "eq",
                    "type": "post_reverb",
                    "bus": "SANCHA_SIREN_REVERB_BUS",
                    "bands": [
                        {
                            "type": "hi_shelf",
                            "frequency_hz": post_processing["eq"]["hi_shelf"]["frequency_hz"],
                            "gain_db": post_processing["eq"]["hi_shelf"]["gain_db"],
                            "description": "Boost air/sibilance in reverb tail"
                        },
                        {
                            "type": "low_cut",
                            "frequency_hz": reverb_params["low_cut_hz"],
                            "slope": "12db_per_octave",
                            "description": "Remove low-end mud from reverb"
                        }
                    ]
                },
                
                # Stage 4: Stereo Widening
                {
                    "stage": "stereo_widening",
                    "bus": "SANCHA_SIREN_REVERB_BUS",
                    "params": post_processing.get("stereo_widening", {}),
                    "description": "Wide ethereal reverb image"
                },
                
                # Stage 5: Sidechain Compression (applied via envelope)
                {
                    "stage": "sidechain_compression",
                    "bus": "SANCHA_SIREN_REVERB_BUS",
                    "config": post_processing["sidechain_compression"],
                    "description": "Reverb ducks when Toxico speaks (envelope-driven)"
                }
            ],
            "output_routing": {
                "dry_vocal": "MASTER_BUS",
                "wet_reverb": "REVERB_BUS → MASTER_BUS (with sidechain)"
            }
        }
    
    @classmethod
    def _build_adlib_sss_chain(cls, adlib_stem: Dict[str, Any],
                               preset: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build SSS processing chain for Toxico's ad-libs.
        
        Args:
            adlib_stem: Ad-lib stem from NemotronAdLibBridge
            preset: TOXICO_HARSH_V1 preset
            
        Returns:
            SSS processing chain for ad-libs
        """
        reverb_params = preset["reverb"]["params"]
        post_processing = preset["post_processing"]
        
        return {
            "stem_id": adlib_stem.get("stem_id", ""),
            "preset_id": preset["preset_id"],
            "clips": adlib_stem.get("clips", []),
            "processing_chain": [
                # Stage 1: Tape Saturation (aggression)
                {
                    "stage": "saturation",
                    "type": post_processing["saturation"]["type"],
                    "params": {
                        "drive_db": post_processing["saturation"]["drive_db"],
                        "harmonic_bias": post_processing["saturation"]["harmonic_bias"],
                        "description": "Add aggressive harmonic distortion"
                    }
                },
                
                # Stage 2: Presence EQ
                {
                    "stage": "eq",
                    "type": "presence_boost",
                    "bands": [
                        {
                            "type": "bell",
                            "frequency_hz": post_processing["eq"]["presence_boost"]["frequency_hz"],
                            "gain_db": post_processing["eq"]["presence_boost"]["gain_db"],
                            "q": post_processing["eq"]["presence_boost"]["q"],
                            "description": "Boost vocal presence for cut-through"
                        }
                    ]
                },
                
                # Stage 3: Short Reverb (tight, aggressive)
                {
                    "stage": "algorithmic_reverb",
                    "params": {
                        "decay_ms": reverb_params["decay_ms"],
                        "wet_dry_ratio": reverb_params["wet_dry_ratio"],
                        "room_size": reverb_params["room_size"],
                        "description": f"Tight reverb ({reverb_params['decay_ms']}ms decay)"
                    }
                },
                
                # Stage 4: Level adjustment (background)
                {
                    "stage": "gain",
                    "level_db": adlib_stem.get("mix_instructions", {}).get("level_db", -6),
                    "description": "Background level (6dB quieter than lead)"
                }
            ],
            "output_routing": {
                "adlib_bus": "MASTER_BUS (also triggers sidechain on Sancha reverb)"
            },
            "sidechain_trigger": True  # This stem triggers sidechain compression
        }
    
    @classmethod
    def _build_enhanced_mastering_chain(cls, base_chain: Dict[str, Any],
                                       sss_chain: Dict[str, Any],
                                       bpm: int) -> Dict[str, Any]:
        """
        Build enhanced mastering chain integrating SSS processing.
        
        Args:
            base_chain: Base mastering chain from Combinator
            sss_chain: SSS processing chain (vocal + adlib + sidechain)
            bpm: Tempo in BPM
            
        Returns:
            Enhanced mastering chain
        """
        return {
            **base_chain,
            "sss_integration": {
                "sancha_vocal_sss": sss_chain["sancha_vocal"],
                "toxico_adlib_sss": sss_chain["toxico_adlib"],
                "sidechain_automation": sss_chain["sidechain_envelope"]
            },
            "mix_order": [
                "1_sancha_dry_vocal → MASTER_BUS",
                "2_sancha_reverb → REVERB_BUS (sidechain target)",
                "3_toxico_adlibs → MASTER_BUS (sidechain source)",
                "4_instrumental → MASTER_BUS",
                "5_apply_sidechain_envelope → REVERB_BUS",
                "6_master_bus_processing → OUTPUT"
            ],
            "timing_sync": {
                "pfa_timestamps": "Sancha vocal timing from ProsodyEngine",
                "adlib_timestamps": "Toxico ad-lib timing from ToxicAdLibGenerator",
                "sidechain_triggers": f"{len(sss_chain['sidechain_envelope']['automation_points']) if sss_chain['sidechain_envelope'] else 0} automation points"
            }
        }


# Convenience function for direct integration
def combine_toxic_drama_scene(sancha_orchestration: Dict[str, Any],
                              toxico_adlib_stem: Dict[str, Any],
                              output_path: str = "/tmp/nemotron/toxic_drama_final.wav") -> Dict[str, Any]:
    """
    Convenience function to combine a full Toxic Drama scene with SSS processing.
    
    Args:
        sancha_orchestration: Orchestration result from Nemotron (Sancha lead vocal + instrumental)
        toxico_adlib_stem: Ad-lib stem from NemotronAdLibBridge
        output_path: Output file path
        
    Returns:
        Final combined mix with SSS processing and sidechain compression
    """
    return CombinatorSSS.combine_with_sss(
        orchestration=sancha_orchestration,
        adlib_stem=toxico_adlib_stem,
        output_path=output_path
    )
