"""
Toxic Ad-Lib Generator
Reactive background agent for TOXICO_PRIME persona
Injects non-verbal cues based on SANCHA_V1's performance

Part of: SLA-113 | Lyrica3 Soulfire Engine | Toxic Drama Expansion
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import uuid


@dataclass
class AdLibEvent:
    """Single ad-lib event with timing and reaction metadata"""
    event_id: str
    timestamp_ms: float
    token: str
    intensity: float
    reaction_type: str
    target_phrase_id: Optional[str] = None
    duration_ms: float = 500.0


class ToxicAdLibGenerator:
    """
    Background reactive agent for TOXICO_PRIME.
    Injects non-verbal cues based on SANCHA_V1's performance.
    
    Reaction Logic:
    1. Vulnerability Reaction: Responds to emotional cracks (vulnerability > 0.8)
    2. Gap Filler: Fills silences longer than 800ms with dismissive tokens
    3. Interruption: Cuts into high-intensity phrases (intensity > 0.85)
    """
    
    REACTION_TOKENS = {
        "vulnerability_reaction": ["<scoff>", "<deep_sigh>", "mnh-mnh"],
        "gap_filler": ["yeah, right", "pff", "whatever"],
        "interruption": ["look...", "listen...", "<sharp_inhale>"]
    }
    
    # Timing parameters (milliseconds)
    VULNERABILITY_DELAY_MS = 200      # Delay after vulnerability detection
    GAP_THRESHOLD_MS = 800            # Minimum silence to trigger gap filler
    GAP_INSERTION_DELAY_MS = 400      # How far into the gap to insert
    INTERRUPTION_TIMING = 0.8         # Interrupt at 80% through phrase
    
    def __init__(self, persona_id: str = "TOXICO_PRIME"):
        """
        Initialize generator.
        
        Args:
            persona_id: ID of the reactive persona (default: TOXICO_PRIME)
        """
        self.persona_id = persona_id
        self._event_counter = 0
    
    def _new_event_id(self) -> str:
        """Generate unique event ID"""
        self._event_counter += 1
        return f"adlib_{self.persona_id}_{self._event_counter:04d}"
    
    def generate_background_track(self, lead_pfa_map: List[Dict[str, Any]]) -> List[AdLibEvent]:
        """
        Generate reactive ad-lib track based on lead vocal's PFA map.
        
        Args:
            lead_pfa_map: SANCHA_V1's PFA (Prosody-Filled Audio) map
                Expected keys: timestamp_ms_start, duration_ms, intensity, dsp_injections
            
        Returns:
            List of AdLibEvent objects with timing and tokens
        """
        ad_lib_track = []
        
        for i, event in enumerate(lead_pfa_map):
            # Extract event data
            timestamp_start = event.get('timestamp_ms_start', 0)
            duration = event.get('duration_ms', 1000)
            intensity = event.get('intensity', 0.5)
            dsp_injections = event.get('dsp_injections', {})
            vulnerability = dsp_injections.get('vulnerability', 0.0)
            phrase_id = event.get('phrase_id', f"phrase_{i}")
            
            # 1. VULNERABILITY REACTION (vulnerability > 0.8)
            if vulnerability > 0.8:
                token = self._select_token("vulnerability_reaction", vulnerability)
                ad_lib_track.append(AdLibEvent(
                    event_id=self._new_event_id(),
                    timestamp_ms=timestamp_start + self.VULNERABILITY_DELAY_MS,
                    token=token,
                    intensity=min(0.9, vulnerability),
                    reaction_type="vulnerability_reaction",
                    target_phrase_id=phrase_id,
                    duration_ms=300
                ))
            
            # 2. GAP FILLER (silence > 800ms)
            if i < len(lead_pfa_map) - 1:
                next_event = lead_pfa_map[i + 1]
                gap = next_event.get('timestamp_ms_start', 0) - (timestamp_start + duration)
                
                if gap > self.GAP_THRESHOLD_MS:
                    token = self._select_token("gap_filler", gap / 1000.0)
                    ad_lib_track.append(AdLibEvent(
                        event_id=self._new_event_id(),
                        timestamp_ms=timestamp_start + duration + self.GAP_INSERTION_DELAY_MS,
                        token=token,
                        intensity=0.5,
                        reaction_type="gap_filler",
                        target_phrase_id=phrase_id,
                        duration_ms=400
                    ))
            
            # 3. INTERRUPTION (on high-intensity phrases > 0.85)
            if intensity > 0.85:
                token = self._select_token("interruption", intensity)
                interrupt_time = timestamp_start + (duration * self.INTERRUPTION_TIMING)
                ad_lib_track.append(AdLibEvent(
                    event_id=self._new_event_id(),
                    timestamp_ms=interrupt_time,
                    token=token,
                    intensity=0.7,
                    reaction_type="interruption",
                    target_phrase_id=phrase_id,
                    duration_ms=600
                ))
        
        # Sort by timestamp
        ad_lib_track.sort(key=lambda e: e.timestamp_ms)
        
        return ad_lib_track
    
    def _select_token(self, reaction_type: str, intensity_value: float) -> str:
        """
        Select appropriate token based on reaction type and intensity.
        
        Args:
            reaction_type: Type of reaction (vulnerability_reaction, gap_filler, interruption)
            intensity_value: Intensity/threshold value (0.0-1.0+)
            
        Returns:
            Selected token string
        """
        tokens = self.REACTION_TOKENS.get(reaction_type, ["..."])
        
        # Map intensity to token index
        if len(tokens) == 1:
            return tokens[0]
        
        # Higher intensity → later tokens in list
        index = min(int(intensity_value * len(tokens)), len(tokens) - 1)
        return tokens[index]
    
    def render_to_audio_spec(self, ad_lib_track: List[AdLibEvent]) -> Dict[str, Any]:
        """
        Convert ad-lib events to audio rendering specification.
        Ready for integration with Nemotron VocalAgent.
        
        Args:
            ad_lib_track: List of AdLibEvent objects
            
        Returns:
            Audio rendering spec dict
        """
        return {
            "stem_id": f"adlib_{self.persona_id}_{uuid.uuid4().hex[:8]}",
            "persona": self.persona_id,
            "voice_profile": "harsh_dismissive_male",
            "events": [asdict(e) for e in ad_lib_track],
            "total_events": len(ad_lib_track),
            "total_duration_ms": max([e.timestamp_ms + e.duration_ms for e in ad_lib_track]) if ad_lib_track else 0,
            "render_instructions": {
                "mix_level_db": -6,  # Background level (6dB quieter than lead)
                "reverb_preset": "TOXICO_HARSH_V1",
                "sidechain_target": "none"  # Toxico doesn't duck
            },
            "status": "ready_for_render"
        }
    
    def export_to_nemotron_format(self, ad_lib_track: List[AdLibEvent]) -> List[Dict[str, Any]]:
        """
        Export ad-lib track to Nemotron-compatible prosody format.
        
        Args:
            ad_lib_track: List of AdLibEvent objects
            
        Returns:
            List of Nemotron-compatible event dicts
        """
        nemotron_events = []
        
        for event in ad_lib_track:
            nemotron_events.append({
                "timestamp_ms": event.timestamp_ms,
                "duration_ms": event.duration_ms,
                "text": event.token,
                "intensity": event.intensity,
                "voice_profile": "TOXICO_PRIME",
                "dsp_markers": {
                    "reaction_type": event.reaction_type,
                    "target_phrase": event.target_phrase_id
                }
            })
        
        return nemotron_events
    
    def get_statistics(self, ad_lib_track: List[AdLibEvent]) -> Dict[str, Any]:
        """
        Get statistics about generated ad-lib track.
        
        Args:
            ad_lib_track: List of AdLibEvent objects
            
        Returns:
            Statistics dict
        """
        if not ad_lib_track:
            return {
                "total_events": 0,
                "by_type": {},
                "avg_intensity": 0.0,
                "total_duration_ms": 0.0
            }
        
        by_type = {}
        for event in ad_lib_track:
            by_type[event.reaction_type] = by_type.get(event.reaction_type, 0) + 1
        
        avg_intensity = sum(e.intensity for e in ad_lib_track) / len(ad_lib_track)
        total_duration = max([e.timestamp_ms + e.duration_ms for e in ad_lib_track])
        
        return {
            "total_events": len(ad_lib_track),
            "by_type": by_type,
            "avg_intensity": round(avg_intensity, 2),
            "total_duration_ms": total_duration,
            "events_per_second": round(len(ad_lib_track) / (total_duration / 1000.0), 2) if total_duration > 0 else 0
        }
