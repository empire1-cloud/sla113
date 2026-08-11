"""
TikTok Engine (Lane G) - Visual Metadata Generator
Maps audio performance data (PFA) to video rendering instructions

Part of: SLA-113 | Lyrica3 Soulfire Engine | Toxic Drama Expansion
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
import uuid
import json

from .glitch_logic import GlitchLogicEngine, GlitchEvent


@dataclass
class GlitchTrigger:
    """Single glitch trigger event"""
    timestamp_ms: float
    type: str
    intensity: float
    duration_ms: float
    source_persona: str
    trigger_event: str
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SyncMarker:
    """Audio-to-video synchronization marker"""
    timestamp_ms: float
    persona: str
    text: str
    intensity: float
    event_type: str
    visual_cue: Optional[str] = None


@dataclass
class ColorGradingZone:
    """Color grading configuration for a persona zone"""
    preset: str
    temperature: int
    tint: int
    grain_amount: float
    contrast: float = 1.0
    saturation: float = 1.0


@dataclass
class TikTokPayload:
    """Complete TikTok video rendering payload"""
    payload_id: str
    template_id: str
    visual_logic: Dict[str, Any]
    lyrics_rendering: Dict[str, Any]
    glitch_triggers: List[Dict[str, Any]]
    audio_sync_markers: List[Dict[str, Any]]
    output_config: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# TOXIC CONFLICT SPLIT TEMPLATE
# ============================================================================

TOXIC_CONFLICT_TEMPLATE = {
    "template_id": "TOXIC_CONFLICT_SPLIT",
    "description": "Dynamic split-screen with reactive glitches and color zones",
    "version": "1.0.0",
    
    "visual_logic": {
        "split_ratio": "dynamic",  # Moves toward person with higher 'intensity'
        "split_orientation": "vertical",
        "transition_speed_ms": 300,
        "default_split_position": 0.5,  # 50/50 split at rest
        
        "split_movement": {
            "intensity_threshold": 0.7,  # Trigger movement at intensity > 0.7
            "max_displacement": 0.3,     # Move up to 30% toward speaker
            "easing": "ease_in_out_cubic"
        },
        
        "color_grading": {
            "sancha_zone": {
                "preset": "cool_cyan_distant",
                "temperature": -15,      # Cool
                "tint": 10,              # Cyan shift
                "grain_amount": 0.2,
                "contrast": 1.1,
                "saturation": 0.9,
                "description": "Ethereal, distant, cold"
            },
            "toxico_zone": {
                "preset": "harsh_amber_grain",
                "temperature": 25,       # Warm/harsh
                "tint": -8,              # Amber shift
                "grain_amount": 0.5,
                "contrast": 1.3,
                "saturation": 1.1,
                "description": "Aggressive, present, harsh"
            }
        },
        
        "glitch_library": {
            "chromatic_aberration": {
                "description": "RGB channel separation",
                "default_intensity": 0.7,
                "default_duration_ms": 150,
                "parameters": {
                    "offset_px": 8,
                    "direction": "horizontal",
                    "red_offset": [8, 0],
                    "blue_offset": [-8, 0]
                }
            },
            "frame_shake": {
                "description": "Aggressive camera shake",
                "default_intensity": 0.8,
                "default_duration_ms": 100,
                "parameters": {
                    "amplitude_px": 12,
                    "frequency_hz": 30,
                    "rotation_deg": 2
                }
            },
            "rgb_split": {
                "description": "Full RGB channel split",
                "default_intensity": 0.6,
                "default_duration_ms": 80,
                "parameters": {
                    "separation_px": 6,
                    "angle_deg": 45
                }
            },
            "distortion_warp": {
                "description": "Lens distortion warp",
                "default_intensity": 0.5,
                "default_duration_ms": 200,
                "parameters": {
                    "strength": 0.3,
                    "center": [0.5, 0.5]
                }
            }
        }
    },
    
    "lyrics_rendering": {
        "sancha": {
            "font": "Elegant_Script_Broken",
            "size_px": 48,
            "color": "#E0F7FF",
            "stroke_color": "#003344",
            "stroke_width": 2,
            "animation": "fade_in_broken",
            "position": "lower_third_left",
            "alignment": "left",
            "max_chars_per_line": 30
        },
        "toxico": {
            "font": "Heavy_Industrial_Impact",
            "size_px": 56,
            "color": "#FFD700",
            "stroke_color": "#331100",
            "stroke_width": 3,
            "animation": "punch_in_aggressive",
            "position": "lower_third_right",
            "alignment": "right",
            "max_chars_per_line": 25
        },
        "alignment": "alternating_vertical",
        "timing_offset_ms": -50,  # Lyrics appear 50ms before audio
        "fade_out_duration_ms": 300
    }
}


# ============================================================================
# TIKTOK ENGINE
# ============================================================================

class TikTokEngine:
    """
    Lane G: TikTok Engine (Toxic Template)
    Generates visual rendering metadata from audio PFA maps
    """
    
    def __init__(self, template_id: str = "TOXIC_CONFLICT_SPLIT", fps: int = 30):
        """
        Initialize TikTok Engine.
        
        Args:
            template_id: Template identifier (default: TOXIC_CONFLICT_SPLIT)
            fps: Target frame rate for glitch engine (default: 30)
        """
        self.template_id = template_id
        self.template = TOXIC_CONFLICT_TEMPLATE.copy()
        self.glitch_engine = GlitchLogicEngine(fps=fps)
    
    def generate_payload(self, 
                        sancha_pfa: List[Dict[str, Any]], 
                        toxico_pfa: List[Dict[str, Any]],
                        scene_metadata: Optional[Dict[str, Any]] = None) -> TikTokPayload:
        """
        Generate TikTok rendering payload from dual PFA maps.
        
        Args:
            sancha_pfa: SANCHA_V1's PFA map
            toxico_pfa: TOXICO_PRIME's PFA map (including ad-libs)
            scene_metadata: Optional scene metadata
            
        Returns:
            TikTokPayload with video rendering instructions
        """
        payload_id = f"tiktok_{uuid.uuid4().hex[:12]}"
        
        # Generate glitch triggers
        glitch_triggers = self._map_glitch_triggers(sancha_pfa, toxico_pfa)
        
        # Generate sync markers
        sync_markers = self._create_sync_markers(sancha_pfa, toxico_pfa)
        
        # Calculate scene duration
        all_events = sancha_pfa + toxico_pfa
        scene_duration_ms = max([e.get('timestamp_ms', e.get('timestamp_ms_start', 0)) 
                                 for e in all_events]) if all_events else 0
        
        # Build metadata
        metadata = {
            "scene_title": scene_metadata.get("title", "Untitled") if scene_metadata else "Untitled",
            "scene_duration_ms": scene_duration_ms,
            "sancha_event_count": len(sancha_pfa),
            "toxico_event_count": len(toxico_pfa),
            "total_glitch_triggers": len(glitch_triggers),
            "generated_at": self._get_timestamp()
        }
        
        if scene_metadata:
            metadata.update(scene_metadata)
        
        return TikTokPayload(
            payload_id=payload_id,
            template_id=self.template_id,
            visual_logic=self.template["visual_logic"],
            lyrics_rendering=self.template["lyrics_rendering"],
            glitch_triggers=[asdict(g) for g in glitch_triggers],
            audio_sync_markers=[asdict(m) for m in sync_markers],
            output_config=self._get_output_config(scene_duration_ms),
            metadata=metadata
        )
    
    def _map_glitch_triggers(self, 
                            sancha_pfa: List[Dict[str, Any]], 
                            toxico_pfa: List[Dict[str, Any]]) -> List[GlitchTrigger]:
        """Map PFA events to glitch triggers"""
        triggers = []
        glitch_lib = self.template["visual_logic"]["glitch_library"]
        
        # Sancha vulnerability → chromatic aberration
        for event in sancha_pfa:
            vulnerability = event.get('dsp_injections', {}).get('vulnerability', 0)
            if vulnerability > 0.7:
                triggers.append(GlitchTrigger(
                    timestamp_ms=event.get('timestamp_ms_start', 0),
                    type="chromatic_aberration",
                    intensity=vulnerability,
                    duration_ms=glitch_lib["chromatic_aberration"]["default_duration_ms"],
                    source_persona="SANCHA_V1",
                    trigger_event="vulnerability",
                    parameters=glitch_lib["chromatic_aberration"]["parameters"].copy()
                ))
        
        # Sancha emotional_crack → RGB split
        for event in sancha_pfa:
            dsp_injections = event.get('dsp_injections', {})
            if '<emotional_crack>' in event.get('text', '') or dsp_injections.get('tremolo', 0) > 0.7:
                triggers.append(GlitchTrigger(
                    timestamp_ms=event.get('timestamp_ms_start', 0),
                    type="rgb_split",
                    intensity=0.8,
                    duration_ms=glitch_lib["rgb_split"]["default_duration_ms"],
                    source_persona="SANCHA_V1",
                    trigger_event="emotional_crack",
                    parameters=glitch_lib["rgb_split"]["parameters"].copy()
                ))
        
        # Toxico interruptions → frame shake
        for event in toxico_pfa:
            if event.get('reaction_type') == 'interruption':
                triggers.append(GlitchTrigger(
                    timestamp_ms=event.get('timestamp_ms', 0),
                    type="frame_shake",
                    intensity=event.get('intensity', 0.7),
                    duration_ms=glitch_lib["frame_shake"]["default_duration_ms"],
                    source_persona="TOXICO_PRIME",
                    trigger_event="interruption",
                    parameters=glitch_lib["frame_shake"]["parameters"].copy()
                ))
        
        # Toxico high intensity → distortion warp
        for event in toxico_pfa:
            intensity = event.get('intensity', 0)
            if intensity > 0.85:
                triggers.append(GlitchTrigger(
                    timestamp_ms=event.get('timestamp_ms', 0),
                    type="distortion_warp",
                    intensity=intensity,
                    duration_ms=glitch_lib["distortion_warp"]["default_duration_ms"],
                    source_persona="TOXICO_PRIME",
                    trigger_event="high_intensity",
                    parameters=glitch_lib["distortion_warp"]["parameters"].copy()
                ))
        
        # Sort by timestamp
        triggers.sort(key=lambda t: t.timestamp_ms)
        
        return triggers
    
    def _create_sync_markers(self, 
                            sancha_pfa: List[Dict[str, Any]], 
                            toxico_pfa: List[Dict[str, Any]]) -> List[SyncMarker]:
        """Create audio-to-video sync markers"""
        markers = []
        
        # Sancha markers
        for event in sancha_pfa:
            markers.append(SyncMarker(
                timestamp_ms=event.get('timestamp_ms_start', 0),
                persona="SANCHA_V1",
                text=event.get('text', ''),
                intensity=event.get('intensity', 0.5),
                event_type="speech",
                visual_cue="lyrics_left"
            ))
        
        # Toxico markers
        for event in toxico_pfa:
            markers.append(SyncMarker(
                timestamp_ms=event.get('timestamp_ms', 0),
                persona="TOXICO_PRIME",
                text=event.get('token', event.get('text', '')),
                intensity=event.get('intensity', 0.5),
                event_type=event.get('reaction_type', 'speech'),
                visual_cue="lyrics_right" if event.get('reaction_type') != 'interruption' else "interrupt_flash"
            ))
        
        # Sort by timestamp
        markers.sort(key=lambda m: m.timestamp_ms)
        
        return markers
    
    def _get_output_config(self, duration_ms: float) -> Dict[str, Any]:
        """Get output configuration for video rendering"""
        return {
            "resolution": {
                "width": 1080,
                "height": 1920,
                "aspect_ratio": "9:16"
            },
            "fps": 30,
            "duration_ms": duration_ms,
            "codec": {
                "video": "h264",
                "audio": "aac",
                "bitrate_video_mbps": 8,
                "bitrate_audio_kbps": 192
            },
            "platform": "tiktok",
            "format": "mp4"
        }
    
    def _get_timestamp(self) -> str:
        """Get ISO timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"
    
    def export_to_json(self, payload: TikTokPayload, 
                      pretty: bool = True) -> str:
        """
        Export payload as JSON for video rendering engine.
        
        Args:
            payload: TikTokPayload to export
            pretty: Pretty-print JSON
            
        Returns:
            JSON string
        """
        export_data = {
            "tiktok_engine_v1": asdict(payload),
            "render_engine": "remotion",  # or "ffmpeg"
            "render_instructions": {
                "compositor": "remotion_react",
                "shader_support": True,
                "glitch_engine": "webgl",
                "text_renderer": "canvas_2d"
            }
        }
        
        return json.dumps(export_data, indent=2 if pretty else None)
    
    def export_to_file(self, payload: TikTokPayload, 
                      output_path: str) -> str:
        """
        Export payload to JSON file.
        
        Args:
            payload: TikTokPayload to export
            output_path: Output file path
            
        Returns:
            Output file path
        """
        json_data = self.export_to_json(payload, pretty=True)
        
        with open(output_path, 'w') as f:
            f.write(json_data)
        
        return output_path
    
    def get_glitch_timeline(self, payload: TikTokPayload) -> List[Dict[str, Any]]:
        """
        Get glitch timeline for debugging/visualization.
        
        Args:
            payload: TikTokPayload
            
        Returns:
            List of glitch events with timing
        """
        timeline = []
        
        for trigger_dict in payload.glitch_triggers:
            timeline.append({
                "timestamp_ms": trigger_dict["timestamp_ms"],
                "timestamp_seconds": round(trigger_dict["timestamp_ms"] / 1000.0, 2),
                "type": trigger_dict["type"],
                "persona": trigger_dict["source_persona"],
                "intensity": trigger_dict["intensity"],
                "duration_ms": trigger_dict["duration_ms"]
            })
        
        return timeline
    
    def validate_payload(self, payload: TikTokPayload) -> Dict[str, Any]:
        """
        Validate payload for rendering.
        
        Args:
            payload: TikTokPayload to validate
            
        Returns:
            Validation result dict
        """
        errors = []
        warnings = []
        
        # Check duration
        if payload.output_config.get("duration_ms", 0) <= 0:
            errors.append("Invalid duration: must be > 0")
        
        # Check glitch triggers
        if not payload.glitch_triggers:
            warnings.append("No glitch triggers defined")
        
        # Check sync markers
        if not payload.audio_sync_markers:
            warnings.append("No audio sync markers defined")
        
        # Check template
        if not payload.template_id:
            errors.append("No template ID specified")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "payload_id": payload.payload_id
        }
    
    def build_render_payload(self, payload: TikTokPayload, 
                            generate_frame_timeline: bool = False) -> Dict[str, Any]:
        """
        Build complete render payload with glitch logic events.
        
        Args:
            payload: TikTokPayload from generate_payload()
            generate_frame_timeline: Generate per-frame timeline (default: False)
            
        Returns:
            Complete render payload with glitch events
        """
        # Convert payload to dict
        payload_dict = asdict(payload)
        
        # Build glitch events using Glitch Logic Engine
        glitch_events = self.glitch_engine.build_timeline(payload_dict)
        
        # Add glitch events to payload
        payload_dict["glitch_events"] = self.glitch_engine.serialize_events(glitch_events)
        
        # Get glitch statistics
        payload_dict["glitch_stats"] = self.glitch_engine.get_statistics(glitch_events)
        
        # Optionally generate frame timeline
        if generate_frame_timeline:
            total_duration_ms = payload_dict["output_config"]["duration_ms"]
            frame_timeline = self.glitch_engine.generate_frame_timeline(
                glitch_events, 
                total_duration_ms
            )
            payload_dict["frame_timeline"] = frame_timeline
        
        return payload_dict
