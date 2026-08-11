"""
Glitch Logic Engine
Translates emotional/audio events into visual glitch envelopes
Produces frame-accurate effect instructions for Remotion/FFmpeg

Part of: SLA-113 | Lyrica3 Soulfire Engine | Toxic Drama Expansion
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
import math
import random


@dataclass
class GlitchEvent:
    """Single glitch event with timing and parameters"""
    event_id: str
    timestamp_ms: int
    duration_ms: int
    effect_type: str
    intensity: float
    params: Dict[str, Any]
    easing: str = "linear"
    target_layer: str = "full_frame"


class GlitchLogicEngine:
    """
    Translates emotional/audio events into visual glitch envelopes.
    Produces a timeline of GlitchEvent objects for Remotion/FFmpeg.
    
    Core Design:
    - Input: TikTok payload events (glitch triggers, sync markers, intensity)
    - Output: Frame-accurate effect instructions
    - Scope: Math + timelines only (no rendering)
    
    Supported Effects:
    1. chromatic_aberration - RGB channel separation
    2. frame_shake - Camera shake with rotation
    3. rgb_split - Full channel split with blur
    4. distortion_warp - Lens distortion / heat haze
    """
    
    # Effect duration ranges (ms)
    DURATIONS = {
        "chromatic_aberration": (220, 500),
        "frame_shake": (260, 600),
        "rgb_split": (180, 400),
        "distortion_warp": (300, 700)
    }
    
    # Easing functions for effects
    EASING_FUNCTIONS = {
        "linear": lambda t: t,
        "exp_out": lambda t: 1 - math.pow(2, -10 * t),
        "sine_in_out": lambda t: -(math.cos(math.pi * t) - 1) / 2,
        "ease_in_quad": lambda t: t * t,
        "ease_out_quad": lambda t: t * (2 - t),
        "bounce_out": lambda t: 1 - abs(math.sin(13.5 * t)) * math.pow(2, -10 * t)
    }
    
    def __init__(self, fps: int = 30, seed: Optional[int] = None):
        """
        Initialize Glitch Logic Engine.
        
        Args:
            fps: Target frame rate (default: 30)
            seed: Random seed for reproducible noise (optional)
        """
        self.fps = fps
        self.frame_duration_ms = 1000.0 / fps
        self._event_counter = 0
        
        if seed is not None:
            random.seed(seed)
    
    def _new_event_id(self, effect_type: str) -> str:
        """Generate unique event ID"""
        self._event_counter += 1
        return f"glitch_{effect_type}_{self._event_counter:04d}"
    
    # ========================================================================
    # PUBLIC API
    # ========================================================================
    
    def build_timeline(self, tiktok_payload: Dict[str, Any]) -> List[GlitchEvent]:
        """
        Build glitch event timeline from TikTok payload.
        
        Args:
            tiktok_payload: Output from tiktok_engine.py
                Expected keys:
                - "glitch_triggers": list of trigger dicts
                - "sync_markers": list of sync marker dicts
                
        Returns:
            List of GlitchEvent objects
        """
        events: List[GlitchEvent] = []
        
        glitch_triggers = tiktok_payload.get("glitch_triggers", [])
        
        for trigger in glitch_triggers:
            effect_type = trigger.get("type", trigger.get("effect_type", "chromatic_aberration"))
            timestamp_ms = trigger.get("timestamp_ms", 0)
            base_intensity = trigger.get("intensity", 0.7)
            
            # Get intensity scale key
            scale_key = trigger.get("intensity_scale", "vulnerability")
            scalar = self._lookup_scalar(trigger, scale_key)
            
            # Calculate final intensity
            intensity = max(0.0, min(1.0, base_intensity * scalar))
            
            # Build effect based on type
            if effect_type == "chromatic_aberration":
                event = self._chromatic_aberration(timestamp_ms, intensity, trigger)
            elif effect_type == "frame_shake":
                event = self._frame_shake(timestamp_ms, intensity, trigger)
            elif effect_type == "rgb_split":
                event = self._rgb_split(timestamp_ms, intensity, trigger)
            elif effect_type == "distortion_warp":
                event = self._distortion_warp(timestamp_ms, intensity, trigger)
            else:
                # Unknown effect type - create generic event
                event = self._generic_glitch(timestamp_ms, intensity, effect_type, trigger)
            
            events.append(event)
        
        # Sort by timestamp
        events.sort(key=lambda e: e.timestamp_ms)
        
        return events
    
    # ========================================================================
    # EFFECT BUILDERS
    # ========================================================================
    
    def _chromatic_aberration(self, timestamp_ms: int, intensity: float, 
                             trigger: Dict[str, Any]) -> GlitchEvent:
        """
        Chromatic Aberration - Edge color fringing that decays quickly.
        
        Visual Effect:
        - RGB channels offset in different directions
        - Creates rainbow-edge distortion
        - Decays exponentially
        
        Use Case: Emotional vulnerability, distant/ethereal moments
        
        Args:
            timestamp_ms: Start time in milliseconds
            intensity: Effect intensity (0.0-1.0)
            trigger: Original trigger dict
            
        Returns:
            GlitchEvent
        """
        # Duration scales with intensity
        min_dur, max_dur = self.DURATIONS["chromatic_aberration"]
        duration_ms = int(min_dur + (max_dur - min_dur) * intensity)
        
        # Offset scales with intensity (max 8px)
        max_offset_px = 8 * intensity
        
        params = {
            "r_offset_px": max_offset_px,              # Red channel offset
            "g_offset_px": -max_offset_px * 0.6,       # Green channel offset (opposite)
            "b_offset_px": max_offset_px * 0.3,        # Blue channel offset (slight)
            "edge_detection": True,                     # Apply stronger on edges
            "blur_amount": 0.2 * intensity,            # Slight blur on separated channels
            "angle_deg": 0                              # Horizontal separation
        }
        
        return GlitchEvent(
            event_id=self._new_event_id("chromatic"),
            timestamp_ms=timestamp_ms,
            duration_ms=duration_ms,
            effect_type="chromatic_aberration",
            intensity=round(intensity, 3),
            params=params,
            easing="exp_out",
            target_layer=trigger.get("source_persona", "full_frame")
        )
    
    def _frame_shake(self, timestamp_ms: int, intensity: float,
                    trigger: Dict[str, Any]) -> GlitchEvent:
        """
        Frame Shake - Camera shake with translation + rotation jitter.
        
        Visual Effect:
        - Random position offsets (x, y)
        - Small rotation oscillation
        - Noise-driven movement
        
        Use Case: Interruptions, aggressive confrontations, impact moments
        
        Args:
            timestamp_ms: Start time in milliseconds
            intensity: Effect intensity (0.0-1.0)
            trigger: Original trigger dict
            
        Returns:
            GlitchEvent
        """
        min_dur, max_dur = self.DURATIONS["frame_shake"]
        duration_ms = int(min_dur + (max_dur - min_dur) * intensity)
        
        # Amplitude scales with intensity (10-30px)
        amplitude_px = 10 + 20 * intensity
        
        # Rotation scales with intensity (1.5-5 degrees)
        rotation_deg = 1.5 + 3.5 * intensity
        
        # Frequency scales with intensity (8-14 Hz)
        frequency_hz = 8 + 6 * intensity
        
        params = {
            "amplitude_px": amplitude_px,
            "rotation_deg": rotation_deg,
            "frequency_hz": frequency_hz,
            "noise_seed": timestamp_ms,                 # Use timestamp for unique noise
            "noise_octaves": 2,                         # Multiple noise layers
            "motion_blur": True,                        # Add motion blur
            "motion_blur_samples": int(3 + 2 * intensity)
        }
        
        return GlitchEvent(
            event_id=self._new_event_id("shake"),
            timestamp_ms=timestamp_ms,
            duration_ms=duration_ms,
            effect_type="frame_shake",
            intensity=round(intensity, 3),
            params=params,
            easing="bounce_out",
            target_layer=trigger.get("source_persona", "full_frame")
        )
    
    def _rgb_split(self, timestamp_ms: int, intensity: float,
                  trigger: Dict[str, Any]) -> GlitchEvent:
        """
        RGB Split - Full channel separation with blur.
        
        Visual Effect:
        - RGB channels separated in different directions
        - Each channel gets slight blur
        - Linear/constant separation
        
        Use Case: Emotional cracks, breakdown moments, tension peaks
        
        Args:
            timestamp_ms: Start time in milliseconds
            intensity: Effect intensity (0.0-1.0)
            trigger: Original trigger dict
            
        Returns:
            GlitchEvent
        """
        min_dur, max_dur = self.DURATIONS["rgb_split"]
        duration_ms = int(min_dur + (max_dur - min_dur) * intensity)
        
        # Base separation scales with intensity (6px max)
        base = 6 * intensity
        
        params = {
            "r_offset_px": base,                        # Red channel
            "g_offset_px": -base * 0.7,                 # Green channel (opposite)
            "b_offset_px": base * 1.2,                  # Blue channel (exaggerated)
            "blur_radius_px": 1.5 * intensity,          # Per-channel blur
            "angle_deg": 45,                            # Diagonal separation
            "separation_mode": "radial"                 # Separate from center
        }
        
        return GlitchEvent(
            event_id=self._new_event_id("rgb_split"),
            timestamp_ms=timestamp_ms,
            duration_ms=duration_ms,
            effect_type="rgb_split",
            intensity=round(intensity, 3),
            params=params,
            easing="linear",
            target_layer=trigger.get("source_persona", "full_frame")
        )
    
    def _distortion_warp(self, timestamp_ms: int, intensity: float,
                        trigger: Dict[str, Any]) -> GlitchEvent:
        """
        Distortion Warp - Lens distortion / heat haze effect.
        
        Visual Effect:
        - Subtle pixel displacement via noise
        - Wavy/fluid distortion
        - Sine wave modulation
        
        Use Case: High intensity, disorientation, surreal moments
        
        Args:
            timestamp_ms: Start time in milliseconds
            intensity: Effect intensity (0.0-1.0)
            trigger: Original trigger dict
            
        Returns:
            GlitchEvent
        """
        min_dur, max_dur = self.DURATIONS["distortion_warp"]
        duration_ms = int(min_dur + (max_dur - min_dur) * intensity)
        
        # Warp strength scales with intensity
        warp_strength = 0.02 + 0.06 * intensity
        
        # Noise scale for displacement
        noise_scale = 1.0 + 1.5 * intensity
        
        params = {
            "warp_strength": warp_strength,
            "noise_scale": noise_scale,
            "noise_speed": 0.5 + 0.5 * intensity,       # Animation speed
            "displacement_mode": "perlin",              # Perlin noise
            "wave_frequency": 2.0 + 3.0 * intensity,    # Wave oscillation
            "center_point": [0.5, 0.5]                  # Center of distortion
        }
        
        return GlitchEvent(
            event_id=self._new_event_id("warp"),
            timestamp_ms=timestamp_ms,
            duration_ms=duration_ms,
            effect_type="distortion_warp",
            intensity=round(intensity, 3),
            params=params,
            easing="sine_in_out",
            target_layer=trigger.get("source_persona", "full_frame")
        )
    
    def _generic_glitch(self, timestamp_ms: int, intensity: float,
                       effect_type: str, trigger: Dict[str, Any]) -> GlitchEvent:
        """
        Generic glitch event for unknown effect types.
        """
        return GlitchEvent(
            event_id=self._new_event_id("generic"),
            timestamp_ms=timestamp_ms,
            duration_ms=300,
            effect_type=effect_type,
            intensity=round(intensity, 3),
            params=trigger.get("parameters", {}),
            easing="linear",
            target_layer="full_frame"
        )
    
    # ========================================================================
    # EASING & ANIMATION
    # ========================================================================
    
    def calculate_frame_value(self, event: GlitchEvent, 
                             current_time_ms: float) -> Optional[float]:
        """
        Calculate effect value at a specific time using easing function.
        
        Args:
            event: GlitchEvent
            current_time_ms: Current time in milliseconds
            
        Returns:
            Normalized value (0.0-1.0) or None if outside event window
        """
        # Check if we're in the event window
        if current_time_ms < event.timestamp_ms:
            return None
        
        end_time = event.timestamp_ms + event.duration_ms
        if current_time_ms >= end_time:
            return None
        
        # Calculate progress (0.0-1.0)
        elapsed = current_time_ms - event.timestamp_ms
        progress = elapsed / event.duration_ms
        
        # Apply easing function
        easing_func = self.EASING_FUNCTIONS.get(event.easing, self.EASING_FUNCTIONS["linear"])
        eased_value = easing_func(progress)
        
        # Scale by intensity
        return eased_value * event.intensity
    
    def generate_frame_timeline(self, events: List[GlitchEvent], 
                               total_duration_ms: float) -> List[Dict[str, Any]]:
        """
        Generate per-frame timeline for rendering.
        
        Args:
            events: List of GlitchEvent objects
            total_duration_ms: Total scene duration
            
        Returns:
            List of frame dicts with active effects
        """
        num_frames = int(math.ceil(total_duration_ms / self.frame_duration_ms))
        timeline = []
        
        for frame_idx in range(num_frames):
            frame_time_ms = frame_idx * self.frame_duration_ms
            
            active_effects = []
            for event in events:
                value = self.calculate_frame_value(event, frame_time_ms)
                if value is not None:
                    active_effects.append({
                        "event_id": event.event_id,
                        "effect_type": event.effect_type,
                        "value": round(value, 4),
                        "params": event.params,
                        "target_layer": event.target_layer
                    })
            
            timeline.append({
                "frame": frame_idx,
                "timestamp_ms": round(frame_time_ms, 2),
                "active_effects": active_effects
            })
        
        return timeline
    
    # ========================================================================
    # HELPERS
    # ========================================================================
    
    def _lookup_scalar(self, trigger: Dict[str, Any], key: str) -> float:
        """
        Pull scalar from trigger context (e.g., vulnerability, intensity).
        Falls back to 1.0 if not present.
        
        Args:
            trigger: Trigger dict
            key: Key to look up
            
        Returns:
            Scalar value (float)
        """
        # Check direct intensity field
        if key == "intensity" and "intensity" in trigger:
            try:
                return float(trigger["intensity"])
            except (TypeError, ValueError):
                pass
        
        # Check context dict
        ctx = trigger.get("context", {})
        val = ctx.get(key, 1.0)
        
        try:
            return float(val)
        except (TypeError, ValueError):
            return 1.0
    
    def serialize_events(self, events: List[GlitchEvent]) -> List[Dict[str, Any]]:
        """
        Convert GlitchEvent objects to JSON-serializable dicts.
        
        Args:
            events: List of GlitchEvent objects
            
        Returns:
            List of dicts
        """
        return [asdict(e) for e in events]
    
    def get_statistics(self, events: List[GlitchEvent]) -> Dict[str, Any]:
        """
        Get statistics about glitch events.
        
        Args:
            events: List of GlitchEvent objects
            
        Returns:
            Statistics dict
        """
        if not events:
            return {
                "total_events": 0,
                "by_type": {},
                "avg_intensity": 0.0,
                "total_duration_ms": 0
            }
        
        by_type = {}
        for event in events:
            by_type[event.effect_type] = by_type.get(event.effect_type, 0) + 1
        
        avg_intensity = sum(e.intensity for e in events) / len(events)
        total_duration = max([e.timestamp_ms + e.duration_ms for e in events])
        
        return {
            "total_events": len(events),
            "by_type": by_type,
            "avg_intensity": round(avg_intensity, 2),
            "total_duration_ms": total_duration,
            "avg_event_duration_ms": round(sum(e.duration_ms for e in events) / len(events), 1)
        }
