"""
LYRICA3 PFA Tag Processor - Explicit LML Tag Translation
Part of SLA-113 Toxic Drama Expansion

Purpose:
    Extends Empire Audio Pipeline PFA with explicit tag-to-DSP translation.
    Converts semantic tags (<vocal_fry>, <adaptive_inhale>, <emotional_crack>) 
    into precise audio engineering parameters.

Integration:
    - Called by Empire Pipeline PFAEngine after biomechanical simulation
    - Processes EFL output with LML tags
    - Injects DSP parameters into vocal_automation_track

Tag Translation Rules (from PFA_Vocal_Biometrics.md):
    1. <vocal_fry>
       → pitch_shift: -2 semitones
       → thd (Total Harmonic Distortion): 0.4
       → phonation_mode: VOCAL_FRY_CRACK
    
    2. <adaptive_inhale>
       → pre_breath_sample: "breath_400ms"
       → breath_duration_ms: 400 (scaled by vulnerability)
       → breath_volume_db: -12 to -6 (based on vulnerability)
    
    3. <emotional_crack>
       → pitch_envelope: [+1 semitone → -2 semitones] over 50ms
       → jitter_increase: +200% (pitch instability spike)
       → shimmer_increase: +3dB (amplitude break)
    
    4. <proximity_effect>
       → eq_boost_200hz: +3dB (close-mic intimacy)
       → compression_ratio: 4:1 (tighter dynamic range)
    
    5. <autocorrection>
       → pitch_correction_amount: 0.0-1.0 (inverse of vulnerability)
       → formant_preservation: true (maintain natural timbre)

Architecture:
    PFATagProcessor
        ├── process_vocal_fry() → Pitch shift + THD
        ├── process_adaptive_inhale() → Breath sample injection
        ├── process_emotional_crack() → Rapid pitch envelope
        ├── process_proximity_effect() → EQ boost + compression
        ├── process_autocorrection() → Pitch correction settings
        └── inject_lml_tags() → Main entry point

Example:
    Input: lyrics_payload = [
        {"line": "She plays innocent", "lml_trigger": "<vocal_fry>"},
        {"line": "but I see through", "lml_trigger": "<emotional_crack>"}
    ]
    
    Output: vocal_automation_track with injected DSP parameters:
        [
            {
                "lyric": "She plays innocent",
                "timestamp_ms_start": 0,
                "dsp_injections": {
                    "pitch_shift_semitones": -2,
                    "thd": 0.4,
                    "phonation_mode": "vocal_fry_crack"
                }
            },
            {
                "lyric": "but I see through",
                "timestamp_ms_start": 2400,
                "dsp_injections": {
                    "pitch_envelope": [1, -2],  # +1 to -2 semitones
                    "pitch_envelope_duration_ms": 50,
                    "jitter_multiplier": 3.0,
                    "shimmer_db_increase": 3.0
                }
            }
        ]
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class LMLTagSpec:
    """Specification for a single LML tag."""
    tag_name: str
    dsp_parameters: Dict[str, Any]
    description: str


class PFATagProcessor:
    """
    PFA Tag Processor - Explicit LML tag to DSP translation.
    
    Mission:
        Convert semantic vocal tags into precise audio engineering parameters.
        Bridge the gap between emotional intent and technical implementation.
    
    Usage:
        >>> processor = PFATagProcessor()
        >>> pfa_map = processor.inject_lml_tags(lyrics_payload, vulnerability_level=0.72)
    """
    
    # Tag specifications (from PFA_Vocal_Biometrics.md)
    TAG_SPECS = {
        "vocal_fry": LMLTagSpec(
            tag_name="vocal_fry",
            dsp_parameters={
                "pitch_shift_semitones": -2,
                "thd": 0.4,  # Total Harmonic Distortion
                "phonation_mode": "vocal_fry_crack",
                "vocal_fold_tension": 0.2  # Relaxed folds
            },
            description="Creaky voice quality with subharmonic frequencies"
        ),
        "adaptive_inhale": LMLTagSpec(
            tag_name="adaptive_inhale",
            dsp_parameters={
                "pre_breath_sample": "breath_400ms",
                "breath_duration_ms": 400,
                "breath_volume_db": -9,  # Default, scaled by vulnerability
                "breath_position": "before"  # Insert before word
            },
            description="Audible breath before phrase (scaled by vulnerability)"
        ),
        "emotional_crack": LMLTagSpec(
            tag_name="emotional_crack",
            dsp_parameters={
                "pitch_envelope": [1, -2],  # Up 1 semitone, down 2 semitones
                "pitch_envelope_duration_ms": 50,
                "pitch_envelope_curve": "exponential",  # Sharp break
                "jitter_multiplier": 3.0,  # 300% increase in pitch instability
                "shimmer_db_increase": 3.0,  # +3dB amplitude variation
                "phonation_mode": "vocal_fry_crack"
            },
            description="Voice breaking under emotional strain"
        ),
        "proximity_effect": LMLTagSpec(
            tag_name="proximity_effect",
            dsp_parameters={
                "eq_boost_200hz_db": 3.0,
                "eq_boost_200hz_q": 1.2,
                "compression_ratio": 4.0,
                "compression_threshold_db": -18,
                "compression_attack_ms": 3,
                "compression_release_ms": 50
            },
            description="Close-mic intimacy with low-frequency warmth"
        ),
        "autocorrection": LMLTagSpec(
            tag_name="autocorrection",
            dsp_parameters={
                "pitch_correction_amount": 0.5,  # 0.0=none, 1.0=full (inverse of vulnerability)
                "pitch_correction_speed_ms": 100,
                "formant_preservation": True,
                "natural_drift_amount": 0.15  # Preserve some human imperfection
            },
            description="Pitch correction (inversely scaled by vulnerability)"
        )
    }
    
    def __init__(self):
        """Initialize PFA tag processor."""
        pass
    
    def parse_lml_tag(self, lml_trigger: str) -> Optional[str]:
        """
        Parse LML tag from trigger string.
        
        Args:
            lml_trigger: Tag string like "<vocal_fry>" or "<adaptive_inhale>"
        
        Returns:
            Tag name without brackets, or None if invalid
        
        Example:
            >>> processor.parse_lml_tag("<vocal_fry>")
            "vocal_fry"
            >>> processor.parse_lml_tag("no_tag")
            None
        """
        if not lml_trigger or not isinstance(lml_trigger, str):
            return None
        
        # Extract tag name from <tag_name> format
        match = re.match(r'^<([a-z_]+)>$', lml_trigger.strip())
        if match:
            return match.group(1)
        
        return None
    
    def process_vocal_fry(self, vulnerability_level: float) -> Dict[str, Any]:
        """
        Process <vocal_fry> tag → pitch shift + THD.
        
        Args:
            vulnerability_level: 0.0-1.0 (affects intensity)
        
        Returns:
            Dict with DSP parameters
        """
        spec = self.TAG_SPECS["vocal_fry"]
        dsp = spec.dsp_parameters.copy()
        
        # Scale THD by vulnerability (more vulnerable = more distortion)
        dsp["thd"] = dsp["thd"] * (0.7 + vulnerability_level * 0.3)
        
        # Scale pitch shift slightly (more vulnerable = deeper fry)
        dsp["pitch_shift_semitones"] = dsp["pitch_shift_semitones"] * (0.8 + vulnerability_level * 0.4)
        
        return dsp
    
    def process_adaptive_inhale(self, vulnerability_level: float) -> Dict[str, Any]:
        """
        Process <adaptive_inhale> tag → breath sample injection.
        
        Args:
            vulnerability_level: 0.0-1.0 (affects breath volume and duration)
        
        Returns:
            Dict with breath parameters
        """
        spec = self.TAG_SPECS["adaptive_inhale"]
        dsp = spec.dsp_parameters.copy()
        
        # Scale breath duration by vulnerability (more vulnerable = longer breath)
        base_duration = 400
        dsp["breath_duration_ms"] = base_duration * (0.7 + vulnerability_level * 0.6)
        
        # Scale breath volume by vulnerability (more vulnerable = louder breath)
        # Range: -12dB (subtle) to -6dB (prominent)
        min_volume_db = -12
        max_volume_db = -6
        dsp["breath_volume_db"] = min_volume_db + (max_volume_db - min_volume_db) * vulnerability_level
        
        return dsp
    
    def process_emotional_crack(self, vulnerability_level: float, peak_intensity: float) -> Dict[str, Any]:
        """
        Process <emotional_crack> tag → rapid pitch envelope.
        
        Args:
            vulnerability_level: 0.0-1.0 (affects crack severity)
            peak_intensity: 0.0-1.0 (affects envelope depth)
        
        Returns:
            Dict with pitch envelope parameters
        """
        spec = self.TAG_SPECS["emotional_crack"]
        dsp = spec.dsp_parameters.copy()
        
        # Scale pitch envelope by intensity (more intense = deeper crack)
        base_up = dsp["pitch_envelope"][0]
        base_down = dsp["pitch_envelope"][1]
        
        intensity_factor = 0.5 + peak_intensity * 0.5
        dsp["pitch_envelope"] = [
            base_up * intensity_factor,
            base_down * intensity_factor
        ]
        
        # Scale jitter multiplier by vulnerability (more vulnerable = more instability)
        dsp["jitter_multiplier"] = dsp["jitter_multiplier"] * (0.8 + vulnerability_level * 0.4)
        
        # Scale shimmer by intensity (more intense = more amplitude variation)
        dsp["shimmer_db_increase"] = dsp["shimmer_db_increase"] * intensity_factor
        
        return dsp
    
    def process_proximity_effect(self, intimacy_level: float = 0.8) -> Dict[str, Any]:
        """
        Process <proximity_effect> tag → EQ boost + compression.
        
        Args:
            intimacy_level: 0.0-1.0 (affects EQ boost and compression)
        
        Returns:
            Dict with EQ and compression parameters
        """
        spec = self.TAG_SPECS["proximity_effect"]
        dsp = spec.dsp_parameters.copy()
        
        # Scale EQ boost by intimacy (more intimate = more warmth)
        base_boost = 3.0
        dsp["eq_boost_200hz_db"] = base_boost * (0.7 + intimacy_level * 0.3)
        
        # Scale compression ratio by intimacy (more intimate = tighter dynamic range)
        base_ratio = 4.0
        dsp["compression_ratio"] = base_ratio * (0.8 + intimacy_level * 0.4)
        
        return dsp
    
    def process_autocorrection(self, vulnerability_level: float) -> Dict[str, Any]:
        """
        Process <autocorrection> tag → pitch correction.
        
        Args:
            vulnerability_level: 0.0-1.0 (inversely affects correction amount)
        
        Returns:
            Dict with pitch correction parameters
        
        Note:
            Higher vulnerability = LESS pitch correction (more natural imperfection)
        """
        spec = self.TAG_SPECS["autocorrection"]
        dsp = spec.dsp_parameters.copy()
        
        # INVERSE relationship: high vulnerability = low correction
        dsp["pitch_correction_amount"] = 1.0 - vulnerability_level
        
        # Preserve more natural drift for vulnerable performances
        dsp["natural_drift_amount"] = 0.05 + (vulnerability_level * 0.2)
        
        return dsp
    
    def inject_lml_tags(self,
                       lyrics_payload: List[Dict[str, str]],
                       vulnerability_level: float = 0.7,
                       peak_intensity: float = 0.8,
                       intimacy_level: float = 0.8) -> Dict[str, Any]:
        """
        Main entry point: Inject LML tags into vocal automation track.
        
        Args:
            lyrics_payload: List of lyric lines with lml_trigger tags
            vulnerability_level: 0.0-1.0 (from EFL stage)
            peak_intensity: 0.0-1.0 (from DOPE stage)
            intimacy_level: 0.0-1.0 (from AURA/EFL stages)
        
        Returns:
            Dict with vocal_automation_track containing DSP injections
        
        Example:
            >>> lyrics = [
            ...     {"line": "She plays innocent", "lml_trigger": "<vocal_fry>"},
            ...     {"line": "I see through you", "lml_trigger": "<emotional_crack>"}
            ... ]
            >>> result = processor.inject_lml_tags(lyrics, vulnerability_level=0.72)
            >>> result["vocal_automation_track"][0]["dsp_injections"]["pitch_shift_semitones"]
            -2.0
        """
        vocal_automation_track = []
        
        # Estimate timing (60 words per minute average speaking rate)
        current_timestamp_ms = 0
        avg_word_duration_ms = 1000  # 1 second per word (60 WPM)
        
        for lyric_entry in lyrics_payload:
            line = lyric_entry.get("line", "")
            lml_trigger = lyric_entry.get("lml_trigger", "")
            
            # Calculate duration based on word count
            word_count = len(line.split())
            line_duration_ms = word_count * avg_word_duration_ms
            
            # Parse LML tag
            tag_name = self.parse_lml_tag(lml_trigger)
            
            # Generate DSP injections based on tag
            dsp_injections = {}
            
            if tag_name == "vocal_fry":
                dsp_injections = self.process_vocal_fry(vulnerability_level)
            elif tag_name == "adaptive_inhale":
                dsp_injections = self.process_adaptive_inhale(vulnerability_level)
                # Adjust timestamp to insert breath BEFORE line
                breath_duration = dsp_injections["breath_duration_ms"]
                current_timestamp_ms += breath_duration
            elif tag_name == "emotional_crack":
                dsp_injections = self.process_emotional_crack(vulnerability_level, peak_intensity)
            elif tag_name == "proximity_effect":
                dsp_injections = self.process_proximity_effect(intimacy_level)
            elif tag_name == "autocorrection":
                dsp_injections = self.process_autocorrection(vulnerability_level)
            else:
                # No tag or unknown tag - use baseline DSP
                dsp_injections = {
                    "pitch_shift_semitones": 0,
                    "thd": 0.0,
                    "jitter_multiplier": 1.0
                }
            
            # Build automation event
            automation_event = {
                "lyric": line,
                "timestamp_ms_start": current_timestamp_ms,
                "timestamp_ms_end": current_timestamp_ms + line_duration_ms,
                "dsp_injections": dsp_injections,
                "lml_tag_applied": tag_name or "none"
            }
            
            vocal_automation_track.append(automation_event)
            
            # Advance timestamp
            current_timestamp_ms += line_duration_ms
        
        return {
            "vocal_automation_track": vocal_automation_track,
            "total_duration_ms": current_timestamp_ms,
            "vulnerability_level": vulnerability_level,
            "peak_intensity": peak_intensity
        }
    
    def merge_with_biomechanics(self,
                               lml_automation: Dict[str, Any],
                               biomechanical_automation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge LML tag automation with biomechanical PFA automation.
        
        Args:
            lml_automation: Output from inject_lml_tags()
            biomechanical_automation: Output from PFAEngine.generate_pfa_automation()
        
        Returns:
            Merged automation track with both tag-based and biomechanical DSP
        
        Note:
            This is called by Empire Pipeline to combine explicit tags with simulation.
        """
        # Handle both nested and direct formats
        if 'pfa_automation_map' in biomechanical_automation:
            bio_track = biomechanical_automation['pfa_automation_map']['vocal_automation_track']
        elif 'vocal_automation_track' in biomechanical_automation:
            bio_track = biomechanical_automation['vocal_automation_track']
        else:
            bio_track = []
        
        lml_track = lml_automation['vocal_automation_track']
        
        # If lengths don't match, use LML track as base
        if len(lml_track) != len(bio_track):
            merged_track = lml_track
        else:
            # Merge DSP injections from both tracks
            merged_track = []
            for lml_event, bio_event in zip(lml_track, bio_track):
                merged_event = lml_event.copy()
                
                # Merge dsp_injections (LML tags take precedence over biomechanics)
                bio_dsp = bio_event.get('dsp_injections', {})
                lml_dsp = lml_event.get('dsp_injections', {})
                
                merged_event['dsp_injections'] = {**bio_dsp, **lml_dsp}
                merged_track.append(merged_event)
        
        return {
            "vocal_automation_track": merged_track,
            "total_duration_ms": lml_automation['total_duration_ms'],
            "vulnerability_level": lml_automation['vulnerability_level']
        }


# Convenience function for direct invocation
def process_lml_tags(lyrics_payload: List[Dict[str, str]],
                    vulnerability_level: float = 0.7,
                    peak_intensity: float = 0.8,
                    intimacy_level: float = 0.8) -> Dict[str, Any]:
    """
    Convenience function to process LML tags.
    
    Args:
        lyrics_payload: List of lyric lines with lml_trigger tags
        vulnerability_level: 0.0-1.0
        peak_intensity: 0.0-1.0
        intimacy_level: 0.0-1.0
    
    Returns:
        Dict with vocal_automation_track
    
    Example:
        >>> lyrics = [{"line": "She plays innocent", "lml_trigger": "<vocal_fry>"}]
        >>> result = process_lml_tags(lyrics, vulnerability_level=0.72)
        >>> print(json.dumps(result, indent=2))
    """
    processor = PFATagProcessor()
    return processor.inject_lml_tags(
        lyrics_payload,
        vulnerability_level,
        peak_intensity,
        intimacy_level
    )


# Example usage
if __name__ == "__main__":
    import json
    
    # Test with example lyrics payload
    test_lyrics = [
        {"line": "She plays innocent, but I see through", "lml_trigger": "<vocal_fry>"},
        {"line": "All those lies, girl, I know you", "lml_trigger": "<emotional_crack>"},
        {"line": "You can't hide from me", "lml_trigger": "<proximity_effect>"},
        {"line": "Not anymore", "lml_trigger": "<adaptive_inhale>"}
    ]
    
    processor = PFATagProcessor()
    
    print("="*80)
    print("PFA Tag Processor Test")
    print("="*80)
    
    result = processor.inject_lml_tags(
        test_lyrics,
        vulnerability_level=0.72,
        peak_intensity=0.85,
        intimacy_level=0.80
    )
    
    print(json.dumps(result, indent=2))
    
    print("\n" + "="*80)
    print("Tag Specifications")
    print("="*80)
    
    for tag_name, spec in processor.TAG_SPECS.items():
        print(f"\n{tag_name.upper()}")
        print(f"  Description: {spec.description}")
        print(f"  DSP Parameters:")
        for param, value in spec.dsp_parameters.items():
            print(f"    - {param}: {value}")
