"""
Nemotron Ad-Lib Bridge
Integrates Toxic Ad-Lib Generator with Nemotron VocalAgent for TTS rendering

Part of: SLA-113 | Lyrica3 Soulfire Engine | Toxic Drama Expansion
Rule: EVOLVE NEVER DELETE
"""

import uuid
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from LYRICA3.soulfire_engine.toxic_adlib_generator import AdLibEvent, ToxicAdLibGenerator
from backend.services.nemotron.stem_orchestrator import VocalAgent


class NemotronAdLibBridge:
    """
    Bridge between Toxic Ad-Lib Generator and Nemotron VocalAgent.
    Converts ad-lib events to Nemotron-compatible prosody format and renders via TTS.
    
    Integration Points:
    1. Takes AdLibEvent list from ToxicAdLibGenerator
    2. Converts to Nemotron prosody map format
    3. Dispatches to VocalAgent for TTS rendering
    4. Returns stem-ready audio spec for Combinator
    """
    
    # Voice profile mappings for TOXICO_PRIME persona
    VOICE_PROFILES = {
        "TOXICO_PRIME_DISMISSIVE": {
            "base_profile": "harsh_dismissive_male",
            "characteristics": {
                "pitch_shift_semitones": -2,
                "speaking_rate": 0.95,
                "energy": 0.7,
                "breathiness": 0.2
            }
        },
        "TOXICO_PRIME_SARCASTIC": {
            "base_profile": "harsh_dismissive_male",
            "characteristics": {
                "pitch_shift_semitones": 1,
                "speaking_rate": 1.1,
                "energy": 0.6,
                "breathiness": 0.3
            }
        },
        "TOXICO_PRIME_AGGRESSIVE": {
            "base_profile": "harsh_dismissive_male",
            "characteristics": {
                "pitch_shift_semitones": -1,
                "speaking_rate": 1.2,
                "energy": 0.9,
                "breathiness": 0.1
            }
        }
    }
    
    # Token-to-TTS mode mapping
    TOKEN_RENDERING_MODES = {
        # Non-verbal tokens (use phoneme-based TTS)
        "<scoff>": {"mode": "non_verbal", "phonemes": "pf_exhale", "duration_scale": 1.0},
        "<deep_sigh>": {"mode": "non_verbal", "phonemes": "hh_exhale_long", "duration_scale": 1.5},
        "mnh-mnh": {"mode": "non_verbal", "phonemes": "mm_nnh_nnh", "duration_scale": 1.2},
        "pff": {"mode": "non_verbal", "phonemes": "pf_short", "duration_scale": 0.8},
        "<sharp_inhale>": {"mode": "non_verbal", "phonemes": "hh_inhale_sharp", "duration_scale": 0.6},
        
        # Verbal tokens (use text-based TTS with style)
        "yeah, right": {"mode": "verbal", "text": "yeah, right", "style": "sarcastic"},
        "whatever": {"mode": "verbal", "text": "whatever", "style": "dismissive"},
        "look...": {"mode": "verbal", "text": "look", "style": "aggressive"},
        "listen...": {"mode": "verbal", "text": "listen", "style": "aggressive"},
    }
    
    def __init__(self, persona_id: str = "TOXICO_PRIME"):
        """
        Initialize bridge.
        
        Args:
            persona_id: ID of the reactive persona (default: TOXICO_PRIME)
        """
        self.persona_id = persona_id
    
    def _select_voice_profile(self, reaction_type: str, intensity: float) -> str:
        """
        Select appropriate voice profile based on reaction type and intensity.
        
        Args:
            reaction_type: Type of reaction (vulnerability_reaction, gap_filler, interruption)
            intensity: Intensity value (0.0-1.0)
            
        Returns:
            Voice profile ID
        """
        if reaction_type == "vulnerability_reaction":
            return "TOXICO_PRIME_DISMISSIVE"
        elif reaction_type == "gap_filler":
            if intensity > 0.6:
                return "TOXICO_PRIME_SARCASTIC"
            else:
                return "TOXICO_PRIME_DISMISSIVE"
        elif reaction_type == "interruption":
            return "TOXICO_PRIME_AGGRESSIVE"
        else:
            return "TOXICO_PRIME_DISMISSIVE"
    
    def _convert_to_prosody(self, ad_lib_events: List[AdLibEvent]) -> Dict[str, Any]:
        """
        Convert ad-lib events to Nemotron-compatible prosody map format.
        
        Args:
            ad_lib_events: List of AdLibEvent objects from ToxicAdLibGenerator
            
        Returns:
            Prosody map dict compatible with Nemotron VocalAgent
        """
        timeline = []
        
        for event in ad_lib_events:
            # Get rendering mode for this token
            render_mode = self.TOKEN_RENDERING_MODES.get(
                event.token,
                {"mode": "verbal", "text": event.token, "style": "neutral"}
            )
            
            # Select voice profile based on reaction type
            voice_profile = self._select_voice_profile(event.reaction_type, event.intensity)
            
            # Build timeline entry
            timeline_entry = {
                "time_ms": event.timestamp_ms,
                "duration_ms": event.duration_ms,
                "text": event.token,
                "intensity": event.intensity,
                "render_mode": render_mode,
                "voice_profile": voice_profile,
                "reaction_type": event.reaction_type,
                "target_phrase_id": event.target_phrase_id,
                "event_id": event.event_id
            }
            
            # Add mode-specific parameters
            if render_mode["mode"] == "non_verbal":
                timeline_entry["phonemes"] = render_mode["phonemes"]
                timeline_entry["action"] = "<non_verbal_vocalization>"
            else:
                timeline_entry["tts_text"] = render_mode["text"]
                timeline_entry["tts_style"] = render_mode.get("style", "neutral")
            
            timeline.append(timeline_entry)
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x["time_ms"])
        
        # Calculate total duration
        total_duration = max(
            [e.timestamp_ms + e.duration_ms for e in ad_lib_events]
        ) if ad_lib_events else 0
        
        return {
            "stem_id": f"adlib_prosody_{self.persona_id}_{uuid.uuid4().hex[:8]}",
            "persona": self.persona_id,
            "timeline": timeline,
            "total_events": len(ad_lib_events),
            "duration_ms": total_duration,
            "bpm": 0,  # Ad-libs are not tempo-locked (reactive)
            "groove_swing": 0.0,
            "status": "prosody_ready"
        }
    
    async def render_adlib_track(self, ad_lib_events: List[AdLibEvent],
                                  output_dir: str = "/tmp/nemotron/adlibs") -> Dict[str, Any]:
        """
        Render ad-lib track using Nemotron VocalAgent.
        
        Args:
            ad_lib_events: List of AdLibEvent objects from ToxicAdLibGenerator
            output_dir: Directory for rendered audio files
            
        Returns:
            Rendered stem specification for Combinator integration
        """
        # Convert to prosody format
        prosody_map = self._convert_to_prosody(ad_lib_events)
        
        # Render individual ad-libs concurrently
        render_tasks = []
        for event in ad_lib_events:
            voice_profile = self._select_voice_profile(event.reaction_type, event.intensity)
            render_tasks.append(
                self._render_single_adlib(event, voice_profile, output_dir)
            )
        
        rendered_clips = await asyncio.gather(*render_tasks)
        
        # Build stem spec for Combinator
        stem_spec = {
            "stem_id": f"adlib_stem_{self.persona_id}_{uuid.uuid4().hex[:8]}",
            "type": "vocal_adlib",
            "persona": self.persona_id,
            "prosody_map": prosody_map,
            "clips": rendered_clips,
            "total_clips": len(rendered_clips),
            "duration_ms": prosody_map["duration_ms"],
            "mix_instructions": {
                "level_db": -6,  # Background level (6dB quieter than lead)
                "pan": 0.0,  # Center
                "reverb_preset": "TOXICO_HARSH_V1",
                "sidechain_source": None,  # Toxico doesn't duck
                "sidechain_target": "SANCHA_SIREN_V1"  # Toxico triggers Sancha's ducking
            },
            "format": "wav_48khz_24bit",
            "status": "rendered"
        }
        
        return stem_spec
    
    async def _render_single_adlib(self, event: AdLibEvent, voice_profile: str,
                                   output_dir: str) -> Dict[str, Any]:
        """
        Render single ad-lib event using VocalAgent.
        
        Args:
            event: AdLibEvent to render
            voice_profile: Voice profile ID
            output_dir: Output directory for audio file
            
        Returns:
            Rendered clip specification
        """
        # Get rendering mode
        render_mode = self.TOKEN_RENDERING_MODES.get(
            event.token,
            {"mode": "verbal", "text": event.token, "style": "neutral"}
        )
        
        # Build mini prosody map for this single event
        mini_prosody = {
            "stem_id": event.event_id,
            "timeline": [{
                "time_ms": 0,  # Relative to clip start
                "text": event.token,
                "duration_ms": event.duration_ms,
                "intensity": event.intensity,
                "render_mode": render_mode
            }],
            "bpm": 0,
            "groove_swing": 0.0
        }
        
        # Render via VocalAgent
        # Note: In production this would call actual TTS engine
        vocal_result = await VocalAgent.render(
            prosody_map=mini_prosody,
            voice_profile=voice_profile,
            vulnerability=0.0  # Toxico is never vulnerable
        )
        
        # Build clip spec
        output_path = f"{output_dir}/{event.event_id}.wav"
        
        return {
            "clip_id": event.event_id,
            "timestamp_ms": event.timestamp_ms,
            "duration_ms": event.duration_ms,
            "audio_path": output_path,
            "voice_profile": voice_profile,
            "token": event.token,
            "render_mode": render_mode["mode"],
            "reaction_type": event.reaction_type,
            "target_phrase_id": event.target_phrase_id,
            "intensity": event.intensity,
            "tts_result": vocal_result,
            "status": "rendered"
        }
    
    def render_adlib_track_sync(self, ad_lib_events: List[AdLibEvent],
                                output_dir: str = "/tmp/nemotron/adlibs") -> Dict[str, Any]:
        """
        Synchronous wrapper for render_adlib_track.
        
        Args:
            ad_lib_events: List of AdLibEvent objects
            output_dir: Output directory for audio files
            
        Returns:
            Rendered stem specification
        """
        return asyncio.run(self.render_adlib_track(ad_lib_events, output_dir))
    
    def get_voice_profile_config(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """
        Get voice profile configuration.
        
        Args:
            profile_id: Voice profile ID
            
        Returns:
            Voice profile config dict or None if not found
        """
        return self.VOICE_PROFILES.get(profile_id)
    
    def list_voice_profiles(self) -> List[str]:
        """
        List all available voice profiles.
        
        Returns:
            List of voice profile IDs
        """
        return list(self.VOICE_PROFILES.keys())
    
    def list_supported_tokens(self) -> List[str]:
        """
        List all supported ad-lib tokens.
        
        Returns:
            List of token strings
        """
        return list(self.TOKEN_RENDERING_MODES.keys())
