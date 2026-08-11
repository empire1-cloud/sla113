"""
LYRICA3 Rhythm Engine - MMA (Micro-Rhythm MIDI Agent)
Part of SLA-113 Toxic Drama Expansion

Purpose:
    Translates groove descriptors into 16-step MIDI sequences with Late-Pocket Swing.
    Enforces human timing imperfections: snare drag (+10-18ms), velocity humanization (65-95).

Integration:
    - Called by ECHO Weaver (prompt chain) to generate rhythm_groove payload
    - Output feeds into Soulfire payload: dope_audio_blueprint.rhythm_groove
    - Works alongside PDA (texture/mastering) and PFA (vocal biometrics)

Architecture:
    MMAGrooveAgent
        ├── parse_groove_descriptor() → Extract BPM, style, intensity
        ├── generate_kick_pattern() → 4-on-floor or syncopated
        ├── generate_snare_pattern() → Late-pocket timing offsets
        ├── generate_hihat_pattern() → Velocity humanization
        └── generate_midi_sequence() → Main entry point, returns strict JSON

Late-Pocket Rule:
    - Snare/Clap hits include timing_offset_ms: +10ms to +18ms
    - Simulates drummer playing "behind the beat"
    - Critical for SGV/Souldie cultural authenticity

Velocity Humanization:
    - HiHat velocity randomized between 65-95
    - Simulates human wrist fatigue and emphasis variation
    - Prevents robotic loop detection

Example groove descriptors:
    - "140bpm_sliding_808_late_snare"
    - "85bpm_chicano_soul_cruising"
    - "120bpm_trap_drill_aggressive"
    - "95bpm_corrido_waltz_intimate"
"""

import json
import re
import random
from typing import Dict, List, Any, Tuple


class MMAGrooveAgent:
    """
    MMA (Micro-Rhythm MIDI Agent) - Sub-agent for Late-Pocket Groove sequencing.
    
    Mission:
        Translate acoustic primitives into 16-step MIDI arrays with human timing imperfections.
    
    Output Format:
        Strict JSON with midi_sequence containing bpm, swing_feel, and track patterns.
    """
    
    # Style-based pattern templates
    KICK_PATTERNS = {
        "four_on_floor": [1,0,0,0, 1,0,0,0, 1,0,0,0, 1,0,0,0],
        "trap": [1,0,0,0, 0,0,1,0, 0,0,0,0, 1,0,1,0],
        "drill": [1,0,0,1, 0,0,1,0, 1,0,0,0, 0,1,0,0],
        "corrido": [1,0,0,0, 0,0,1,0, 0,1,0,0, 1,0,0,0],
        "soul": [1,0,0,0, 0,0,0,0, 1,0,0,0, 0,0,0,0],
        "waltz": [1,0,0,0, 0,0,0,0, 0,0,1,0, 0,0,0,0],
    }
    
    SNARE_PATTERNS = {
        "standard": [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
        "trap": [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,1],
        "drill": [0,0,0,0, 1,0,1,0, 0,0,0,0, 1,0,0,0],
        "syncopated": [0,0,0,1, 0,0,1,0, 0,0,0,0, 1,0,0,0],
        "corrido": [0,0,0,0, 1,0,0,0, 0,0,1,0, 0,0,0,0],
        "waltz": [0,0,0,0, 0,1,0,0, 0,0,0,0, 0,1,0,0],
    }
    
    HIHAT_PATTERNS = {
        "closed_16th": [1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1],
        "closed_8th": [1,0,1,0, 1,0,1,0, 1,0,1,0, 1,0,1,0],
        "open_sparse": [1,0,0,0, 1,0,0,0, 1,0,0,1, 0,0,1,0],
        "trap_rolls": [1,1,1,1, 1,1,1,1, 1,1,1,0, 1,1,0,0],
        "drill_aggressive": [1,0,1,1, 1,0,1,1, 1,0,1,1, 1,0,1,0],
    }
    
    def __init__(self, seed: int = None):
        """
        Initialize MMA agent.
        
        Args:
            seed: Random seed for reproducible humanization (optional)
        """
        self.seed = seed
        if seed is not None:
            random.seed(seed)
    
    def parse_groove_descriptor(self, groove: str) -> Dict[str, Any]:
        """
        Parse groove descriptor string into structured components.
        
        Args:
            groove: String like "140bpm_sliding_808_late_snare"
        
        Returns:
            Dict with bpm, style, intensity, and pattern hints
        
        Example:
            Input: "85bpm_chicano_soul_cruising"
            Output: {
                "bpm": 85,
                "style": "soul",
                "substyle": "chicano",
                "intensity": "low",
                "keywords": ["cruising"]
            }
        """
        groove_lower = groove.lower()
        
        # Extract BPM
        bpm_match = re.search(r'(\d+)bpm', groove_lower)
        bpm = int(bpm_match.group(1)) if bpm_match else 120
        
        # Detect style
        style = "standard"
        substyle = None
        if "trap" in groove_lower:
            style = "trap"
        elif "drill" in groove_lower:
            style = "drill"
        elif "corrido" in groove_lower:
            style = "corrido"
        elif "soul" in groove_lower or "cruising" in groove_lower:
            style = "soul"
            if "chicano" in groove_lower:
                substyle = "chicano"
        elif "waltz" in groove_lower:
            style = "waltz"
        elif "808" in groove_lower:
            style = "trap"
        
        # Detect intensity
        intensity = "medium"
        if any(kw in groove_lower for kw in ["aggressive", "harsh", "intense", "heavy"]):
            intensity = "high"
        elif any(kw in groove_lower for kw in ["cruising", "intimate", "soft", "gentle"]):
            intensity = "low"
        
        # Extract keywords
        keywords = []
        keyword_candidates = ["sliding", "late", "snare", "808", "cruising", "intimate", "aggressive"]
        for kw in keyword_candidates:
            if kw in groove_lower:
                keywords.append(kw)
        
        return {
            "bpm": bpm,
            "style": style,
            "substyle": substyle,
            "intensity": intensity,
            "keywords": keywords
        }
    
    def generate_kick_pattern(self, style: str, intensity: str) -> List[int]:
        """
        Generate 16-step kick pattern based on style.
        
        Args:
            style: Music style (trap, drill, soul, corrido, waltz, standard)
            intensity: Intensity level (low, medium, high)
        
        Returns:
            List of 16 integers (1=hit, 0=rest)
        """
        # Select base pattern
        if style in self.KICK_PATTERNS:
            pattern = self.KICK_PATTERNS[style].copy()
        else:
            pattern = self.KICK_PATTERNS["four_on_floor"].copy()
        
        # Modify based on intensity
        if intensity == "high":
            # Add extra kicks for aggressive feel
            if style == "trap" and pattern[14] == 0:
                pattern[14] = 1  # Add extra kick before last beat
        elif intensity == "low":
            # Remove some kicks for sparse feel
            if style == "soul" and pattern[8] == 1:
                pattern[8] = 0
        
        return pattern
    
    def generate_snare_pattern(self, style: str, intensity: str) -> Tuple[List[int], List[float]]:
        """
        Generate 16-step snare pattern with Late-Pocket timing offsets.
        
        Args:
            style: Music style
            intensity: Intensity level
        
        Returns:
            Tuple of (pattern, timing_offsets_ms)
            - pattern: List of 16 integers (1=hit, 0=rest)
            - timing_offsets_ms: List of floats (+10 to +18ms for each hit)
        """
        # Select base pattern
        if style in self.SNARE_PATTERNS:
            pattern = self.SNARE_PATTERNS[style].copy()
        else:
            pattern = self.SNARE_PATTERNS["standard"].copy()
        
        # Generate Late-Pocket timing offsets for each hit
        timing_offsets = []
        for hit in pattern:
            if hit == 1:
                # THE LATE POCKET RULE: +10ms to +18ms behind the grid
                offset = random.uniform(10.0, 18.0)
                timing_offsets.append(round(offset, 2))
            else:
                timing_offsets.append(0.0)
        
        # Modify based on intensity
        if intensity == "high" and style == "drill":
            # Add extra snare hits for aggressive drill feel
            if pattern[6] == 0:
                pattern[6] = 1
                timing_offsets[6] = round(random.uniform(10.0, 18.0), 2)
        
        return pattern, timing_offsets
    
    def generate_hihat_pattern(self, style: str, intensity: str) -> Tuple[List[int], List[int]]:
        """
        Generate 16-step hihat pattern with velocity humanization.
        
        Args:
            style: Music style
            intensity: Intensity level
        
        Returns:
            Tuple of (pattern, velocities)
            - pattern: List of 16 integers (1=hit, 0=rest)
            - velocities: List of 16 integers (65-95, randomized for each hit)
        """
        # Select base pattern
        if style == "trap":
            pattern = self.HIHAT_PATTERNS["trap_rolls"].copy()
        elif style == "drill":
            pattern = self.HIHAT_PATTERNS["drill_aggressive"].copy()
        elif style == "soul" or style == "corrido":
            pattern = self.HIHAT_PATTERNS["closed_8th"].copy()
        elif style == "waltz":
            pattern = self.HIHAT_PATTERNS["open_sparse"].copy()
        else:
            pattern = self.HIHAT_PATTERNS["closed_16th"].copy()
        
        # Generate humanized velocities for each step
        velocities = []
        for i, hit in enumerate(pattern):
            if hit == 1:
                # VELOCITY HUMANIZATION RULE: 65-95 to simulate human wrist movement
                base_velocity = 80
                
                # Add emphasis on downbeats (steps 0, 4, 8, 12)
                if i % 4 == 0:
                    base_velocity = 90
                
                # Add intensity variation
                if intensity == "high":
                    velocity = random.randint(75, 95)
                elif intensity == "low":
                    velocity = random.randint(65, 80)
                else:
                    velocity = random.randint(70, 90)
                
                velocities.append(velocity)
            else:
                velocities.append(0)
        
        # Modify pattern based on intensity
        if intensity == "low":
            # Sparser hihat for intimate feel
            for i in range(len(pattern)):
                if i % 2 == 1 and random.random() < 0.3:
                    pattern[i] = 0
                    velocities[i] = 0
        
        return pattern, velocities
    
    def generate_midi_sequence(self, groove: str) -> Dict[str, Any]:
        """
        Main entry point: Generate complete MIDI sequence from groove descriptor.
        
        Args:
            groove: Groove descriptor string (e.g., "140bpm_sliding_808_late_snare")
        
        Returns:
            Dict with midi_sequence in strict JSON format:
            {
                "midi_sequence": {
                    "bpm": int,
                    "swing_feel": "late_pocket",
                    "tracks": {
                        "kick": {"pattern": [...], "velocity": [...]},
                        "snare": {"pattern": [...], "timing_offset_ms": [...]},
                        "hihat": {"pattern": [...], "velocity_humanized": [...]}
                    }
                }
            }
        
        Example:
            >>> agent = MMAGrooveAgent(seed=42)
            >>> result = agent.generate_midi_sequence("85bpm_chicano_soul_cruising")
            >>> result["midi_sequence"]["bpm"]
            85
            >>> len(result["midi_sequence"]["tracks"]["kick"]["pattern"])
            16
        """
        # Parse groove descriptor
        parsed = self.parse_groove_descriptor(groove)
        
        # Generate patterns
        kick_pattern = self.generate_kick_pattern(parsed["style"], parsed["intensity"])
        snare_pattern, snare_timing = self.generate_snare_pattern(parsed["style"], parsed["intensity"])
        hihat_pattern, hihat_velocity = self.generate_hihat_pattern(parsed["style"], parsed["intensity"])
        
        # Build MIDI sequence
        midi_sequence = {
            "midi_sequence": {
                "bpm": parsed["bpm"],
                "swing_feel": "late_pocket",
                "style": parsed["style"],
                "intensity": parsed["intensity"],
                "tracks": {
                    "kick": {
                        "pattern": kick_pattern,
                        "velocity": [100 for _ in kick_pattern]  # Kick is always 100 velocity
                    },
                    "snare": {
                        "pattern": snare_pattern,
                        "timing_offset_ms": snare_timing
                    },
                    "hihat": {
                        "pattern": hihat_pattern,
                        "velocity_humanized": hihat_velocity
                    }
                }
            }
        }
        
        return midi_sequence


# Convenience function for direct invocation
def generate_late_pocket_groove(groove_descriptor: str, seed: int = None) -> Dict[str, Any]:
    """
    Convenience function to generate Late-Pocket MIDI sequence.
    
    Args:
        groove_descriptor: Groove string (e.g., "140bpm_trap_drill_aggressive")
        seed: Random seed for reproducible humanization (optional)
    
    Returns:
        Dict with midi_sequence in strict JSON format
    
    Example:
        >>> result = generate_late_pocket_groove("120bpm_trap_drill_aggressive", seed=42)
        >>> print(json.dumps(result, indent=2))
    """
    agent = MMAGrooveAgent(seed=seed)
    return agent.generate_midi_sequence(groove_descriptor)


# Example usage
if __name__ == "__main__":
    # Test with different groove descriptors
    test_grooves = [
        "140bpm_sliding_808_late_snare",
        "85bpm_chicano_soul_cruising",
        "120bpm_trap_drill_aggressive",
        "95bpm_corrido_waltz_intimate"
    ]
    
    agent = MMAGrooveAgent(seed=42)
    
    for groove in test_grooves:
        print(f"\n{'='*60}")
        print(f"Groove: {groove}")
        print(f"{'='*60}")
        
        result = agent.generate_midi_sequence(groove)
        print(json.dumps(result, indent=2))
        
        # Verify Late-Pocket Rule
        snare_offsets = result["midi_sequence"]["tracks"]["snare"]["timing_offset_ms"]
        snare_pattern = result["midi_sequence"]["tracks"]["snare"]["pattern"]
        
        print("\nLate-Pocket Verification:")
        for i, (hit, offset) in enumerate(zip(snare_pattern, snare_offsets)):
            if hit == 1:
                print(f"  Step {i}: Snare hit with +{offset}ms offset (Late-Pocket Rule: 10-18ms)")
        
        # Verify Velocity Humanization
        hihat_velocities = result["midi_sequence"]["tracks"]["hihat"]["velocity_humanized"]
        hihat_pattern = result["midi_sequence"]["tracks"]["hihat"]["pattern"]
        
        print("\nVelocity Humanization:")
        active_velocities = [v for v, h in zip(hihat_velocities, hihat_pattern) if h == 1]
        if active_velocities:
            print(f"  HiHat velocity range: {min(active_velocities)}-{max(active_velocities)}")
            print(f"  Average velocity: {sum(active_velocities) / len(active_velocities):.1f}")
            print(f"  Humanization Rule: 65-95 (human wrist variation)")
