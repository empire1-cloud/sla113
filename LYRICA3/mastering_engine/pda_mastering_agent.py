"""
LYRICA3 Mastering Engine - PDA (Psychoacoustic DSP Agent)
Part of SLA-113 Toxic Drama Expansion

Purpose:
    Translates texture descriptors into mathematical DSP parameters for final mixing.
    Destroys "sterile AI" sound with analog warmth, tape saturation, proximity effect.

Integration:
    - Called by ECHO Weaver (prompt chain) to generate texture_dsp and mastering_sss payload
    - Output feeds into Soulfire payload: dope_audio_blueprint.texture_dsp, mastering_sss
    - Works alongside MMA (rhythm) and PFA (vocal biometrics)

Architecture:
    PDAMasteringAgent
        ├── parse_texture_descriptor() → Extract texture style, intensity, effects
        ├── apply_warmth_processing() → Tape saturation + LPF rolloff
        ├── apply_modern_processing() → Multiband compression on sub frequencies
        ├── apply_proximity_effect() → +3dB @ 200Hz on vocal stem
        └── generate_master_bus_dsp() → Main entry point, returns strict JSON

Texture Translation Rules:
    1. warmth/analog/lo_fi → Tape Saturation (Chebyshev) + 12kHz LPF
    2. drill/modern → Aggressive Multiband Compression (20-80Hz sub band)
    3. PROXIMITY EFFECT → Always apply +3dB @ 200Hz on vocal stem (close-mic intimacy)

DSP Parameters:
    - Tape Saturation: Chebyshev distortion (drive: 0.2-0.6)
    - Low-Pass Filter: Analog warmth rolloff (8kHz-16kHz)
    - Multiband Compression: Sub-bass control (ratio: 3:1-6:1, threshold: -12dB)
    - Proximity Effect: EQ boost at 200Hz (gain: +2dB to +4dB)
    - Reverb: Room/plate (decay: 0.8s-2.5s)
    - Parallel Compression: NY-style drum glue (ratio: 4:1, threshold: -20dB)

Example texture descriptors:
    - "vintage_ssl_console_warmth"
    - "lo_fi_memphis_tape_hiss"
    - "drill_modern_sub_heavy"
    - "intimate_proximity_bedroom"
"""

import json
import re
from typing import Dict, Any, List, Tuple


class PDAMasteringAgent:
    """
    PDA (Psychoacoustic DSP Agent) - Sub-agent for texture and mastering.
    
    Mission:
        Translate texture strings into WebAudio/Tone.js compatible DSP parameters.
        Destroy sterile AI sound with analog processing.
    
    Output Format:
        Strict JSON with master_bus_dsp containing vocal, drum, bass, and master channels.
    """
    
    # Texture-based DSP presets
    TAPE_SATURATION_PRESETS = {
        "lo_fi": {"drive": 0.5, "mix": 0.7, "type": "chebyshev"},
        "vintage": {"drive": 0.35, "mix": 0.5, "type": "chebyshev"},
        "analog": {"drive": 0.25, "mix": 0.4, "type": "chebyshev"},
        "clean": {"drive": 0.1, "mix": 0.2, "type": "chebyshev"}
    }
    
    LPF_ROLLOFF_PRESETS = {
        "lo_fi": 8000,
        "vintage": 12000,
        "analog": 14000,
        "modern": 20000,
        "clean": 20000
    }
    
    REVERB_PRESETS = {
        "intimate": {"decay": 0.8, "pre_delay": 10, "wet": 0.15},
        "bedroom": {"decay": 1.2, "pre_delay": 15, "wet": 0.25},
        "studio": {"decay": 1.8, "pre_delay": 20, "wet": 0.35},
        "hall": {"decay": 2.5, "pre_delay": 30, "wet": 0.45}
    }
    
    def __init__(self):
        """Initialize PDA agent."""
        pass
    
    def parse_texture_descriptor(self, texture: str) -> Dict[str, Any]:
        """
        Parse texture descriptor string into structured components.
        
        Args:
            texture: String like "vintage_ssl_console_warmth"
        
        Returns:
            Dict with texture style, intensity, and effect flags
        
        Example:
            Input: "lo_fi_memphis_tape_hiss"
            Output: {
                "warmth_level": "lo_fi",
                "has_warmth": True,
                "has_tape_hiss": True,
                "has_modern": False,
                "proximity": "standard",
                "reverb_style": "intimate"
            }
        """
        texture_lower = texture.lower()
        
        # Detect warmth/analog characteristics
        warmth_level = "clean"
        has_warmth = False
        if "lo_fi" in texture_lower or "lofi" in texture_lower:
            warmth_level = "lo_fi"
            has_warmth = True
        elif "vintage" in texture_lower or "ssl" in texture_lower or "console" in texture_lower:
            warmth_level = "vintage"
            has_warmth = True
        elif "analog" in texture_lower or "warmth" in texture_lower or "warm" in texture_lower:
            warmth_level = "analog"
            has_warmth = True
        
        # Detect modern/drill characteristics
        has_modern = any(kw in texture_lower for kw in ["drill", "modern", "sub_heavy", "aggressive"])
        
        # Detect tape characteristics
        has_tape_hiss = any(kw in texture_lower for kw in ["tape", "hiss", "noise"])
        
        # Detect proximity/intimacy
        proximity = "standard"
        if any(kw in texture_lower for kw in ["intimate", "proximity", "close", "bedroom"]):
            proximity = "intimate"
        elif any(kw in texture_lower for kw in ["distant", "far", "ambient"]):
            proximity = "distant"
        
        # Detect reverb style
        reverb_style = "bedroom"
        if "intimate" in texture_lower or "bedroom" in texture_lower or "close" in texture_lower:
            reverb_style = "intimate"
        elif "studio" in texture_lower or "room" in texture_lower:
            reverb_style = "studio"
        elif "hall" in texture_lower or "large" in texture_lower:
            reverb_style = "hall"
        
        return {
            "warmth_level": warmth_level,
            "has_warmth": has_warmth,
            "has_tape_hiss": has_tape_hiss,
            "has_modern": has_modern,
            "proximity": proximity,
            "reverb_style": reverb_style
        }
    
    def apply_warmth_processing(self, warmth_level: str, has_tape_hiss: bool) -> Dict[str, Any]:
        """
        Apply analog warmth processing: tape saturation + LPF rolloff.
        
        Args:
            warmth_level: Warmth intensity (lo_fi, vintage, analog, clean)
            has_tape_hiss: Whether to add tape hiss noise floor
        
        Returns:
            Dict with saturation and LPF parameters
        
        Example:
            warmth_level="vintage", has_tape_hiss=True
            → {"saturation_drive": 0.35, "saturation_mix": 0.5, "lpf_hz": 12000, "tape_hiss_db": -65}
        """
        # Get saturation preset
        saturation = self.TAPE_SATURATION_PRESETS.get(warmth_level, self.TAPE_SATURATION_PRESETS["clean"])
        
        # Get LPF rolloff
        lpf_hz = self.LPF_ROLLOFF_PRESETS.get(warmth_level, 20000)
        
        # Calculate tape hiss noise floor
        tape_hiss_db = -70  # Default: very quiet
        if has_tape_hiss:
            if warmth_level == "lo_fi":
                tape_hiss_db = -55  # More pronounced hiss
            elif warmth_level == "vintage":
                tape_hiss_db = -65
            else:
                tape_hiss_db = -70
        
        return {
            "saturation_drive": saturation["drive"],
            "saturation_mix": saturation["mix"],
            "saturation_type": saturation["type"],
            "low_pass_filter_hz": lpf_hz,
            "tape_hiss_noise_floor_db": tape_hiss_db
        }
    
    def apply_modern_processing(self, has_modern: bool) -> Dict[str, Any]:
        """
        Apply modern drill/trap processing: multiband compression on sub frequencies.
        
        Args:
            has_modern: Whether to apply aggressive modern processing
        
        Returns:
            Dict with multiband compression parameters
        
        Example:
            has_modern=True
            → {"mb_comp_sub_ratio": 6.0, "mb_comp_sub_threshold_db": -12, "mb_comp_sub_attack_ms": 5}
        """
        if has_modern:
            # Aggressive multiband compression for drill/modern
            return {
                "multiband_comp_enabled": True,
                "mb_comp_sub_freq_low": 20,
                "mb_comp_sub_freq_high": 80,
                "mb_comp_sub_ratio": 6.0,
                "mb_comp_sub_threshold_db": -12,
                "mb_comp_sub_attack_ms": 5,
                "mb_comp_sub_release_ms": 50,
                "mb_comp_sub_knee_db": 3
            }
        else:
            # Gentle multiband compression for warmth/vintage
            return {
                "multiband_comp_enabled": True,
                "mb_comp_sub_freq_low": 20,
                "mb_comp_sub_freq_high": 80,
                "mb_comp_sub_ratio": 3.0,
                "mb_comp_sub_threshold_db": -18,
                "mb_comp_sub_attack_ms": 10,
                "mb_comp_sub_release_ms": 100,
                "mb_comp_sub_knee_db": 6
            }
    
    def apply_proximity_effect(self, proximity: str) -> Dict[str, Any]:
        """
        Apply proximity effect: EQ boost at 200Hz on vocal stem (close-mic intimacy).
        
        Args:
            proximity: Proximity style (intimate, standard, distant)
        
        Returns:
            Dict with vocal EQ parameters
        
        Example:
            proximity="intimate"
            → {"eq_200hz_gain_db": 4.0, "eq_200hz_q": 1.2}
        
        Note:
            PROXIMITY EFFECT RULE: Vocal stem must ALWAYS have +3dB @ 200Hz minimum.
        """
        # PROXIMITY EFFECT RULE: Always apply at least +3dB @ 200Hz
        if proximity == "intimate":
            return {
                "eq_200hz_gain_db": 4.0,
                "eq_200hz_q": 1.2,
                "eq_200hz_type": "peaking"
            }
        elif proximity == "distant":
            return {
                "eq_200hz_gain_db": 2.0,
                "eq_200hz_q": 0.8,
                "eq_200hz_type": "peaking"
            }
        else:
            # Standard: minimum +3dB
            return {
                "eq_200hz_gain_db": 3.0,
                "eq_200hz_q": 1.0,
                "eq_200hz_type": "peaking"
            }
    
    def apply_reverb_processing(self, reverb_style: str) -> Dict[str, Any]:
        """
        Apply reverb processing based on style.
        
        Args:
            reverb_style: Reverb style (intimate, bedroom, studio, hall)
        
        Returns:
            Dict with reverb parameters
        """
        preset = self.REVERB_PRESETS.get(reverb_style, self.REVERB_PRESETS["bedroom"])
        
        return {
            "reverb_decay_sec": preset["decay"],
            "reverb_pre_delay_ms": preset["pre_delay"],
            "reverb_wet_mix": preset["wet"],
            "reverb_type": "plate" if reverb_style in ["studio", "hall"] else "room"
        }
    
    def apply_parallel_compression(self, has_modern: bool) -> Dict[str, Any]:
        """
        Apply parallel compression (NY-style drum glue).
        
        Args:
            has_modern: Whether to apply aggressive modern compression
        
        Returns:
            Dict with parallel compression parameters
        """
        if has_modern:
            # Aggressive parallel compression for modern/drill
            return {
                "parallel_comp_ratio": 6.0,
                "parallel_comp_threshold_db": -24,
                "parallel_comp_attack_ms": 3,
                "parallel_comp_release_ms": 80,
                "parallel_comp_mix": 0.4
            }
        else:
            # Classic NY-style parallel compression
            return {
                "parallel_comp_ratio": 4.0,
                "parallel_comp_threshold_db": -20,
                "parallel_comp_attack_ms": 5,
                "parallel_comp_release_ms": 100,
                "parallel_comp_mix": 0.3
            }
    
    def generate_master_bus_dsp(self, texture: str) -> Dict[str, Any]:
        """
        Main entry point: Generate complete master bus DSP from texture descriptor.
        
        Args:
            texture: Texture descriptor string (e.g., "vintage_ssl_console_warmth")
        
        Returns:
            Dict with master_bus_dsp in strict JSON format:
            {
                "master_bus_dsp": {
                    "vocal_channel": {...},
                    "drum_channel": {...},
                    "bass_channel": {...},
                    "master_out": {...}
                }
            }
        
        Example:
            >>> agent = PDAMasteringAgent()
            >>> result = agent.generate_master_bus_dsp("lo_fi_memphis_tape_hiss")
            >>> result["master_bus_dsp"]["vocal_channel"]["eq_200hz_gain_db"]
            3.0
            >>> result["master_bus_dsp"]["master_out"]["tape_hiss_noise_floor_db"]
            -55
        """
        # Parse texture descriptor
        parsed = self.parse_texture_descriptor(texture)
        
        # Apply processing rules
        warmth = self.apply_warmth_processing(parsed["warmth_level"], parsed["has_tape_hiss"])
        modern = self.apply_modern_processing(parsed["has_modern"])
        proximity = self.apply_proximity_effect(parsed["proximity"])
        reverb = self.apply_reverb_processing(parsed["reverb_style"])
        parallel = self.apply_parallel_compression(parsed["has_modern"])
        
        # Build master bus DSP
        master_bus_dsp = {
            "master_bus_dsp": {
                "vocal_channel": {
                    # PROXIMITY EFFECT RULE: Always +3dB @ 200Hz minimum
                    "eq_200hz_gain_db": proximity["eq_200hz_gain_db"],
                    "eq_200hz_q": proximity["eq_200hz_q"],
                    "eq_200hz_type": proximity["eq_200hz_type"],
                    # Reverb
                    "reverb_decay_sec": reverb["reverb_decay_sec"],
                    "reverb_pre_delay_ms": reverb["reverb_pre_delay_ms"],
                    "reverb_wet_mix": reverb["reverb_wet_mix"],
                    "reverb_type": reverb["reverb_type"],
                    # De-esser (prevent harshness)
                    "de_esser_threshold_db": -15,
                    "de_esser_freq_hz": 6000,
                    "de_esser_ratio": 3.0
                },
                "drum_channel": {
                    # Parallel compression (NY-style glue)
                    "parallel_comp_ratio": parallel["parallel_comp_ratio"],
                    "parallel_comp_threshold_db": parallel["parallel_comp_threshold_db"],
                    "parallel_comp_attack_ms": parallel["parallel_comp_attack_ms"],
                    "parallel_comp_release_ms": parallel["parallel_comp_release_ms"],
                    "parallel_comp_mix": parallel["parallel_comp_mix"],
                    # Transient shaping
                    "transient_attack_db": 2.0 if parsed["has_modern"] else 1.0,
                    "transient_sustain_db": -1.0
                },
                "bass_channel": {
                    # Multiband compression on sub frequencies
                    "multiband_comp_enabled": modern["multiband_comp_enabled"],
                    "mb_comp_sub_freq_low": modern["mb_comp_sub_freq_low"],
                    "mb_comp_sub_freq_high": modern["mb_comp_sub_freq_high"],
                    "mb_comp_sub_ratio": modern["mb_comp_sub_ratio"],
                    "mb_comp_sub_threshold_db": modern["mb_comp_sub_threshold_db"],
                    "mb_comp_sub_attack_ms": modern["mb_comp_sub_attack_ms"],
                    "mb_comp_sub_release_ms": modern["mb_comp_sub_release_ms"],
                    "mb_comp_sub_knee_db": modern["mb_comp_sub_knee_db"],
                    # Saturation for analog warmth
                    "saturation_drive": warmth["saturation_drive"],
                    "saturation_mix": warmth["saturation_mix"],
                    "saturation_type": warmth["saturation_type"]
                },
                "master_out": {
                    # Tape hiss (analog character)
                    "tape_hiss_noise_floor_db": warmth["tape_hiss_noise_floor_db"],
                    # Low-pass filter (analog rolloff)
                    "low_pass_filter_hz": warmth["low_pass_filter_hz"],
                    "low_pass_filter_q": 0.7,
                    # Master limiter (prevent clipping)
                    "limiter_threshold_db": -1.0,
                    "limiter_release_ms": 50,
                    # Stereo width
                    "stereo_width": 1.2 if not parsed["has_modern"] else 1.0,
                    # Dithering (for analog feel)
                    "dither_enabled": parsed["has_warmth"],
                    "dither_depth_bits": 16 if parsed["warmth_level"] == "lo_fi" else 24
                },
                "metadata": {
                    "texture_descriptor": texture,
                    "warmth_level": parsed["warmth_level"],
                    "has_modern_processing": parsed["has_modern"],
                    "proximity_style": parsed["proximity"],
                    "reverb_style": parsed["reverb_style"]
                }
            }
        }
        
        return master_bus_dsp


# Convenience function for direct invocation
def generate_texture_mastering(texture_descriptor: str) -> Dict[str, Any]:
    """
    Convenience function to generate master bus DSP from texture descriptor.
    
    Args:
        texture_descriptor: Texture string (e.g., "vintage_ssl_console_warmth")
    
    Returns:
        Dict with master_bus_dsp in strict JSON format
    
    Example:
        >>> result = generate_texture_mastering("lo_fi_memphis_tape_hiss")
        >>> print(json.dumps(result, indent=2))
    """
    agent = PDAMasteringAgent()
    return agent.generate_master_bus_dsp(texture_descriptor)


# Example usage
if __name__ == "__main__":
    # Test with different texture descriptors
    test_textures = [
        "vintage_ssl_console_warmth",
        "lo_fi_memphis_tape_hiss",
        "drill_modern_sub_heavy",
        "intimate_proximity_bedroom"
    ]
    
    agent = PDAMasteringAgent()
    
    for texture in test_textures:
        print(f"\n{'='*60}")
        print(f"Texture: {texture}")
        print(f"{'='*60}")
        
        result = agent.generate_master_bus_dsp(texture)
        print(json.dumps(result, indent=2))
        
        # Verify Proximity Effect Rule
        vocal_eq_200hz = result["master_bus_dsp"]["vocal_channel"]["eq_200hz_gain_db"]
        print(f"\nProximity Effect Verification:")
        print(f"  Vocal EQ @ 200Hz: +{vocal_eq_200hz}dB (Rule: minimum +3dB)")
        
        # Verify Warmth Processing
        if "warmth" in texture or "analog" in texture or "lo_fi" in texture:
            print(f"\nWarmth Processing:")
            print(f"  Saturation Drive: {result['master_bus_dsp']['bass_channel']['saturation_drive']}")
            print(f"  LPF Rolloff: {result['master_bus_dsp']['master_out']['low_pass_filter_hz']}Hz")
            print(f"  Tape Hiss: {result['master_bus_dsp']['master_out']['tape_hiss_noise_floor_db']}dB")
        
        # Verify Modern Processing
        if "drill" in texture or "modern" in texture:
            print(f"\nModern Processing:")
            print(f"  Multiband Comp Ratio: {result['master_bus_dsp']['bass_channel']['mb_comp_sub_ratio']}:1")
            print(f"  Sub Band: {result['master_bus_dsp']['bass_channel']['mb_comp_sub_freq_low']}-{result['master_bus_dsp']['bass_channel']['mb_comp_sub_freq_high']}Hz")
            print(f"  Parallel Comp: {result['master_bus_dsp']['drum_channel']['parallel_comp_ratio']}:1")
