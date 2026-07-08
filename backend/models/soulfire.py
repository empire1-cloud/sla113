"""
Soulfire Payload Models
Part of SLA-113 Toxic Drama Expansion

Purpose:
    Pydantic models for Soulfire payload validation and serialization.
    Extends prototype schema with rhythm_groove, texture_dsp, mastering_sss fields.

Schema Evolution:
    - Prototype: rhythm_groove/texture_dsp as strings
    - Current: Full nested objects with MMA/PDA agent outputs

Integration:
    - Used by Lyrica3 Pro orchestration endpoints
    - Consumed by Empire Audio Pipeline
    - Compatible with existing CCNA/Nemotron systems
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum


class EmotionalTag(str, Enum):
    """LML emotional tags for vocal biometrics."""
    VOCAL_FRY = "<vocal_fry>"
    ADAPTIVE_INHALE = "<adaptive_inhale>"
    EMOTIONAL_CRACK = "<emotional_crack>"
    PROXIMITY_EFFECT = "<proximity_effect>"
    AUTOCORRECTION = "<autocorrection>"
    NONE = ""


class TrackMetadata(BaseModel):
    """Track-level metadata."""
    title: str = Field(..., description="Track title")
    core_genre: str = Field(..., description="Primary genre (Trap-Soul, Drill, etc.)")
    s2_mutation_applied: Optional[str] = Field(None, description="S2 disruption heuristic (juxtaposition, transplantation, etc.)")
    dna_tag_preview: str = Field(..., description="DNA tag preview (e.g., toxic-breakup-late-pocket-analog)")
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Innocent Act",
                "core_genre": "Trap-Soul",
                "s2_mutation_applied": "juxtaposition",
                "dna_tag_preview": "toxic-breakup-late-pocket-analog"
            }
        }


class MIDISequence(BaseModel):
    """MIDI sequence from MMA agent."""
    bpm: int = Field(..., ge=60, le=200, description="Tempo (BPM)")
    swing_feel: str = Field("late_pocket", description="Swing feel (late_pocket, on_grid)")
    style: str = Field(..., description="Musical style (trap, drill, soul, etc.)")
    intensity: str = Field(..., description="Intensity level (low, medium, high)")
    tracks: Dict[str, Any] = Field(..., description="MIDI tracks (kick, snare, hihat)")
    
    class Config:
        schema_extra = {
            "example": {
                "bpm": 120,
                "swing_feel": "late_pocket",
                "style": "trap",
                "intensity": "high",
                "tracks": {
                    "kick": {"pattern": [1,0,0,0, 1,0,0,0, 1,0,0,0, 1,0,0,0], "velocity": [100]*16},
                    "snare": {"pattern": [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0], "timing_offset_ms": [0,0,0,0, 15.2,0,0,0, 0,0,0,0, 12.8,0,0,0]},
                    "hihat": {"pattern": [1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1], "velocity_humanized": [85,72,90,78, 82,88,75,91, 80,77,85,73, 88,81,79,86]}
                }
            }
        }


class RhythmGroove(BaseModel):
    """Rhythm groove from MMA agent (full object)."""
    midi_sequence: MIDISequence = Field(..., description="16-step MIDI sequence with late-pocket timing")
    
    class Config:
        schema_extra = {
            "example": {
                "midi_sequence": {
                    "bpm": 120,
                    "swing_feel": "late_pocket",
                    "style": "trap",
                    "intensity": "high",
                    "tracks": {}
                }
            }
        }


class MasterBusDSP(BaseModel):
    """Master bus DSP from PDA agent."""
    vocal_channel: Dict[str, Any] = Field(..., description="Vocal channel DSP parameters")
    drum_channel: Dict[str, Any] = Field(..., description="Drum channel DSP parameters")
    bass_channel: Dict[str, Any] = Field(..., description="Bass channel DSP parameters")
    master_out: Dict[str, Any] = Field(..., description="Master output DSP parameters")
    metadata: Optional[Dict[str, Any]] = Field(None, description="DSP metadata")
    
    class Config:
        schema_extra = {
            "example": {
                "vocal_channel": {
                    "eq_200hz_gain_db": 3.0,
                    "reverb_decay_sec": 1.2
                },
                "drum_channel": {
                    "parallel_comp_ratio": 4.0
                },
                "bass_channel": {
                    "saturation_drive": 0.35,
                    "multiband_comp_sub_ratio": 6.0
                },
                "master_out": {
                    "tape_hiss_noise_floor_db": -70,
                    "low_pass_filter_hz": 12000
                }
            }
        }


class TextureDSP(BaseModel):
    """Texture DSP from PDA agent (full object)."""
    master_bus_dsp: MasterBusDSP = Field(..., description="Master bus DSP parameters")
    
    class Config:
        schema_extra = {
            "example": {
                "master_bus_dsp": {
                    "vocal_channel": {},
                    "drum_channel": {},
                    "bass_channel": {},
                    "master_out": {}
                }
            }
        }


class DOPEAudioBlueprint(BaseModel):
    """DOPE audio blueprint with extended fields."""
    vulnerability_level: float = Field(..., ge=0.0, le=1.0, description="Vulnerability level (0.0-1.0)")
    rhythm_groove: RhythmGroove = Field(..., description="MMA rhythm groove (full object)")
    texture_dsp: TextureDSP = Field(..., description="PDA texture DSP (full object)")
    mastering_sss: str = Field(..., description="SSS preset name (SANCHA_SIREN_V1, TOXICO_HARSH_V1)")
    stem_priorities: Optional[Dict[str, float]] = Field(None, description="Stem mix priorities (vocal: 1.0, 808: 0.85, etc.)")
    
    class Config:
        schema_extra = {
            "example": {
                "vulnerability_level": 0.72,
                "rhythm_groove": {
                    "midi_sequence": {
                        "bpm": 120,
                        "swing_feel": "late_pocket",
                        "style": "trap",
                        "intensity": "high",
                        "tracks": {}
                    }
                },
                "texture_dsp": {
                    "master_bus_dsp": {}
                },
                "mastering_sss": "SANCHA_SIREN_V1",
                "stem_priorities": {
                    "vocal": 1.0,
                    "808": 0.85,
                    "drums": 0.75
                }
            }
        }


class LyricLine(BaseModel):
    """Single lyric line with LML trigger."""
    line: str = Field(..., description="Lyric line text")
    lml_trigger: str = Field("", description="LML emotional tag (<vocal_fry>, <emotional_crack>, etc.)")
    
    class Config:
        schema_extra = {
            "example": {
                "line": "She plays innocent, but I see through",
                "lml_trigger": "<vocal_fry>"
            }
        }


class SoulfirePayload(BaseModel):
    """
    Complete Soulfire payload schema.
    
    Generated by: AURA → ASE → EFL → ECHO → EFAD prompt chain
    Consumed by: Empire Audio Pipeline → Nemotron → SSS → Video Engine
    
    Schema Version: 2.0 (extended with rhythm_groove, texture_dsp objects)
    """
    track_metadata: TrackMetadata = Field(..., description="Track metadata")
    dope_audio_blueprint: DOPEAudioBlueprint = Field(..., description="Audio production blueprint")
    lyrics_payload: List[LyricLine] = Field(..., description="Lyric lines with LML tags")
    
    class Config:
        schema_extra = {
            "example": {
                "track_metadata": {
                    "title": "Innocent Act",
                    "core_genre": "Trap-Soul",
                    "s2_mutation_applied": "juxtaposition",
                    "dna_tag_preview": "toxic-breakup-late-pocket-analog"
                },
                "dope_audio_blueprint": {
                    "vulnerability_level": 0.72,
                    "rhythm_groove": {
                        "midi_sequence": {
                            "bpm": 120,
                            "swing_feel": "late_pocket",
                            "style": "trap",
                            "intensity": "high",
                            "tracks": {}
                        }
                    },
                    "texture_dsp": {
                        "master_bus_dsp": {}
                    },
                    "mastering_sss": "SANCHA_SIREN_V1",
                    "stem_priorities": {
                        "vocal": 1.0,
                        "808": 0.85
                    }
                },
                "lyrics_payload": [
                    {
                        "line": "She plays innocent, but I see through",
                        "lml_trigger": "<vocal_fry>"
                    },
                    {
                        "line": "All those lies, girl, I know you",
                        "lml_trigger": "<emotional_crack>"
                    }
                ]
            }
        }


# Legacy support: Allow string values for rhythm_groove and texture_dsp
class SoulfirePayloadLegacy(BaseModel):
    """
    Legacy Soulfire payload schema (prototype compatibility).
    
    rhythm_groove and texture_dsp are strings instead of objects.
    Use SoulfirePayload for new implementations.
    """
    track_metadata: TrackMetadata
    dope_audio_blueprint: Dict[str, Any]  # Flexible for legacy
    lyrics_payload: List[LyricLine]
    
    class Config:
        schema_extra = {
            "example": {
                "track_metadata": {
                    "title": "Innocent Act",
                    "core_genre": "Trap-Soul",
                    "s2_mutation_applied": "juxtaposition",
                    "dna_tag_preview": "toxic-breakup-late-pocket-analog"
                },
                "dope_audio_blueprint": {
                    "vulnerability_level": 0.72,
                    "rhythm_groove": "120bpm_trap_late_snare",
                    "texture_dsp": "vintage_ssl_analog_warmth",
                    "mastering_sss": "SANCHA_SIREN_V1"
                },
                "lyrics_payload": [
                    {
                        "line": "She plays innocent, but I see through",
                        "lml_trigger": "<vocal_fry>"
                    }
                ]
            }
        }


# Conversion utilities
def convert_legacy_to_v2(legacy_payload: SoulfirePayloadLegacy,
                        mma_agent,
                        pda_agent) -> SoulfirePayload:
    """
    Convert legacy payload (strings) to v2 payload (objects).
    
    Args:
        legacy_payload: Legacy payload with rhythm_groove/texture_dsp as strings
        mma_agent: MMAGrooveAgent instance
        pda_agent: PDAMasteringAgent instance
    
    Returns:
        SoulfirePayload with full objects
    """
    blueprint = legacy_payload.dope_audio_blueprint
    
    # Generate rhythm_groove object from string descriptor
    rhythm_groove_str = blueprint.get("rhythm_groove", "120bpm_standard")
    rhythm_groove_obj = mma_agent.generate_midi_sequence(rhythm_groove_str)
    
    # Generate texture_dsp object from string descriptor
    texture_dsp_str = blueprint.get("texture_dsp", "standard_production")
    texture_dsp_obj = pda_agent.generate_master_bus_dsp(texture_dsp_str)
    
    # Build v2 payload
    return SoulfirePayload(
        track_metadata=legacy_payload.track_metadata,
        dope_audio_blueprint=DOPEAudioBlueprint(
            vulnerability_level=blueprint.get("vulnerability_level", 0.7),
            rhythm_groove=RhythmGroove(midi_sequence=MIDISequence(**rhythm_groove_obj["midi_sequence"])),
            texture_dsp=TextureDSP(master_bus_dsp=MasterBusDSP(**texture_dsp_obj["master_bus_dsp"])),
            mastering_sss=blueprint.get("mastering_sss", "SANCHA_SIREN_V1"),
            stem_priorities=blueprint.get("stem_priorities")
        ),
        lyrics_payload=legacy_payload.lyrics_payload
    )
