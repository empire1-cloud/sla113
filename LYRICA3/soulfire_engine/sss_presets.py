"""
SSS (Soulfire Sonic Sculpting) Presets
Mastering-grade audio processing presets for Toxic Drama personas

Part of: SLA-113 | Lyrica3 Soulfire Engine | Toxic Drama Expansion
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class ReverbParams:
    """Reverb parameters"""
    type: str
    decay_ms: int
    pre_delay_ms: int
    wet_dry_ratio: float
    room_size: Optional[str] = None
    impulse_response: Optional[str] = None


@dataclass
class SidechainCompression:
    """Sidechain compression parameters"""
    enabled: bool
    source: str
    threshold_db: float
    ratio: str
    attack_ms: int
    release_ms: int
    description: str


@dataclass
class EQBand:
    """Single EQ band parameters"""
    frequency_hz: int
    gain_db: float
    q: Optional[float] = None
    slope: Optional[str] = None


# ============================================================================
# SANCHA_SIREN_V1 - Ethereal, Dangerous, Distanced Vocal
# ============================================================================

SANCHA_SIREN_PRESET = {
    "preset_id": "SANCHA_SIREN_V1",
    "persona": "SANCHA_V1",
    "description": "Ethereal, dangerous, distanced vocal with sidechain ducking",
    "version": "1.0.0",
    "created_for": "toxic_drama_expansion",
    
    "reverb": {
        "type": "convolution",
        "impulse_response": "large_cathedral_dampened",
        "params": {
            "decay_ms": 4500,        # Long, haunting decay
            "pre_delay_ms": 85,      # Separates dry vocal from 'Siren' wash
            "wet_dry_ratio": 0.65,   # Heavy on wet signal (65% reverb)
            "hi_shelf_boost_db": 4,  # Highlights 'Sibilant Hiss' in reverb
            "low_cut_hz": 400        # Keeps low-end mud out of drama
        },
        "character": "haunting_distant_cathedral",
        "emotional_profile": "dangerous_ethereal"
    },
    
    "post_processing": {
        "sidechain_compression": {
            "enabled": True,
            "source": "TOXICO_PRIME",  # Her reverb ducks when he speaks
            "threshold_db": -24,
            "ratio": "4:1",
            "attack_ms": 5,
            "release_ms": 150,
            "knee_db": 6,
            "description": "Sancha's reverb ducks when Toxico interrupts"
        },
        
        "eq": {
            "hi_shelf": {
                "frequency_hz": 8000,
                "gain_db": 4,
                "description": "Boost sibilance/air in reverb tail"
            },
            "low_cut": {
                "frequency_hz": 400,
                "slope": "24db_per_octave",
                "description": "Remove low-end rumble from reverb"
            },
            "presence_boost": {
                "frequency_hz": 2500,
                "gain_db": 2,
                "q": 1.5,
                "description": "Subtle vocal presence boost"
            }
        },
        
        "stereo_widening": {
            "enabled": True,
            "amount": 0.4,  # 40% width enhancement
            "frequency_range_hz": [800, 12000],
            "description": "Widen reverb tail, keep vocal center"
        }
    },
    
    "automation": {
        "reverb_intensity": {
            "trigger": "vulnerability",
            "min_wet_dry": 0.45,
            "max_wet_dry": 0.75,
            "curve": "exponential",
            "description": "More reverb on vulnerable phrases"
        },
        "hi_shelf_boost": {
            "trigger": "emotional_crack",
            "min_gain_db": 2,
            "max_gain_db": 6,
            "description": "Boost air/sibilance on cracks"
        }
    },
    
    "mix_parameters": {
        "vocal_level_db": -3,      # 3dB below unity
        "pan": 0.0,                # Center
        "reverb_send_level_db": -6,
        "delay_send_level_db": -12
    },
    
    "visual_association": {
        "color_palette": ["cool_cyan", "distant_blue", "ethereal_white"],
        "glitch_response": "chromatic_aberration",
        "video_zone": "left_split"
    }
}


# ============================================================================
# TOXICO_PRIME_V1 - Dry, Aggressive, In-Your-Face Vocal
# ============================================================================

TOXICO_PRIME_PRESET = {
    "preset_id": "TOXICO_HARSH_V1",
    "persona": "TOXICO_PRIME",
    "description": "Dry, aggressive, in-your-face vocal with minimal reverb",
    "version": "1.0.0",
    "created_for": "toxic_drama_expansion",
    
    "reverb": {
        "type": "algorithmic",
        "params": {
            "decay_ms": 800,         # Short, tight reverb
            "pre_delay_ms": 20,
            "wet_dry_ratio": 0.15,   # Mostly dry (15% reverb)
            "room_size": "small"
        },
        "character": "tight_aggressive_room",
        "emotional_profile": "confrontational_present"
    },
    
    "post_processing": {
        "saturation": {
            "enabled": True,
            "type": "tape_saturation",
            "drive_db": 6,           # 6dB drive for aggression
            "harmonic_bias": "odd",  # Odd harmonics = harsh/aggressive
            "model": "vintage_tape_overdriven",
            "description": "Add aggression and bite"
        },
        
        "eq": {
            "presence_boost": {
                "frequency_hz": 3000,
                "gain_db": 3,
                "q": 1.2,
                "description": "Boost vocal presence/aggression"
            },
            "low_mid_cut": {
                "frequency_hz": 250,
                "gain_db": -2,
                "q": 0.8,
                "description": "Reduce muddiness"
            },
            "hi_shelf": {
                "frequency_hz": 10000,
                "gain_db": 2,
                "description": "Add air/bite to consonants"
            }
        },
        
        "compression": {
            "enabled": True,
            "threshold_db": -18,
            "ratio": "6:1",
            "attack_ms": 3,
            "release_ms": 100,
            "knee_db": 4,
            "makeup_gain_db": 4,
            "description": "Aggressive compression for consistency"
        },
        
        "de_esser": {
            "enabled": True,
            "frequency_hz": 7500,
            "threshold_db": -15,
            "ratio": "3:1",
            "description": "Control harsh sibilance"
        }
    },
    
    "automation": {
        "saturation_drive": {
            "trigger": "intensity",
            "min_drive_db": 4,
            "max_drive_db": 9,
            "description": "More saturation on intense phrases"
        },
        "presence_boost": {
            "trigger": "interruption",
            "min_gain_db": 2,
            "max_gain_db": 5,
            "description": "Boost presence on interruptions"
        }
    },
    
    "mix_parameters": {
        "vocal_level_db": -1,      # 1dB below unity (louder than Sancha)
        "pan": 0.0,                # Center
        "reverb_send_level_db": -18,
        "delay_send_level_db": float('-inf')  # No delay
    },
    
    "visual_association": {
        "color_palette": ["harsh_amber", "grain_yellow", "aggressive_orange"],
        "glitch_response": "frame_shake",
        "video_zone": "right_split"
    }
}


# ============================================================================
# PRESET REGISTRY
# ============================================================================

SSS_PRESET_REGISTRY = {
    "SANCHA_SIREN_V1": SANCHA_SIREN_PRESET,
    "TOXICO_HARSH_V1": TOXICO_PRIME_PRESET
}


# ============================================================================
# SSS PRESET MANAGER
# ============================================================================

class SSSPresetManager:
    """
    Manager for SSS (Soulfire Sonic Sculpting) presets.
    Loads, validates, and applies mastering presets.
    """
    
    def __init__(self):
        """Initialize preset manager"""
        self.presets = SSS_PRESET_REGISTRY.copy()
    
    def get_preset(self, preset_id: str) -> Optional[Dict[str, Any]]:
        """
        Get preset by ID.
        
        Args:
            preset_id: Preset identifier (e.g., "SANCHA_SIREN_V1")
            
        Returns:
            Preset dict or None if not found
        """
        return self.presets.get(preset_id)
    
    def get_preset_for_persona(self, persona_id: str) -> Optional[Dict[str, Any]]:
        """
        Get preset for a persona.
        
        Args:
            persona_id: Persona identifier (e.g., "SANCHA_V1")
            
        Returns:
            Preset dict or None if not found
        """
        for preset in self.presets.values():
            if preset.get("persona") == persona_id:
                return preset
        return None
    
    def list_presets(self) -> List[str]:
        """List all available preset IDs"""
        return list(self.presets.keys())
    
    def apply_preset_to_stem(self, stem_data: Dict[str, Any], 
                            preset_id: str) -> Dict[str, Any]:
        """
        Apply SSS preset to a stem.
        
        Args:
            stem_data: Stem audio data dict
            preset_id: Preset to apply
            
        Returns:
            Updated stem data with SSS processing instructions
        """
        preset = self.get_preset(preset_id)
        if not preset:
            raise ValueError(f"Preset not found: {preset_id}")
        
        stem_data["sss_preset"] = preset_id
        stem_data["sss_processing"] = {
            "reverb": preset["reverb"],
            "post_processing": preset["post_processing"],
            "mix_parameters": preset["mix_parameters"]
        }
        
        if "automation" in preset:
            stem_data["sss_automation"] = preset["automation"]
        
        return stem_data
    
    def export_preset_for_daw(self, preset_id: str, 
                             format: str = "json") -> Dict[str, Any]:
        """
        Export preset in DAW-compatible format.
        
        Args:
            preset_id: Preset to export
            format: Export format (json, logic_pro, ableton, pro_tools)
            
        Returns:
            Exported preset data
        """
        preset = self.get_preset(preset_id)
        if not preset:
            raise ValueError(f"Preset not found: {preset_id}")
        
        if format == "json":
            return preset
        
        # TODO: Implement DAW-specific export formats
        return {
            "preset": preset,
            "format": format,
            "status": "export_format_not_implemented"
        }
    
    def get_sidechain_configuration(self, source_preset_id: str, 
                                   target_preset_id: str) -> Optional[Dict[str, Any]]:
        """
        Get sidechain compression configuration between two presets.
        
        Args:
            source_preset_id: Source preset (e.g., TOXICO_HARSH_V1)
            target_preset_id: Target preset (e.g., SANCHA_SIREN_V1)
            
        Returns:
            Sidechain config dict or None
        """
        target_preset = self.get_preset(target_preset_id)
        if not target_preset:
            return None
        
        sidechain = target_preset.get("post_processing", {}).get("sidechain_compression")
        if not sidechain or not sidechain.get("enabled"):
            return None
        
        source_preset = self.get_preset(source_preset_id)
        if not source_preset:
            return None
        
        # Verify source matches
        if sidechain.get("source") != source_preset.get("persona"):
            return None
        
        return {
            "source_preset": source_preset_id,
            "target_preset": target_preset_id,
            "sidechain_params": sidechain,
            "configuration": {
                "source_persona": source_preset.get("persona"),
                "target_persona": target_preset.get("persona"),
                "threshold_db": sidechain["threshold_db"],
                "ratio": sidechain["ratio"],
                "attack_ms": sidechain["attack_ms"],
                "release_ms": sidechain["release_ms"]
            }
        }
