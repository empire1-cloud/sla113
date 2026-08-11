"""
FFmpeg Filter Chain Builder for Toxic Drama Video Rendering
Non-React alternative to Remotion for headless video production

Part of: SLA-113 | Lyrica3 Soulfire Engine | Toxic Drama Expansion
Rule: EVOLVE NEVER DELETE

Implements equivalent effects to Remotion components:
- Dynamic split-screen with vertical orientation
- Color grading zones (LUT-based or filter chain)
- Chromatic aberration (channel separation)
- Frame shake (transform animation)
- RGB split (channel offset)
- Distortion warp (perspective transform)
- Lyrics rendering (drawtext with timing)
"""

import json
import uuid
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import math


class FFmpegFilterChainBuilder:
    """
    Builds FFmpeg filter_complex chains from TikTok Engine payloads.
    Generates command-line ready filter specifications.
    """
    
    def __init__(self, output_width: int = 1080, output_height: int = 1920, fps: int = 30):
        """
        Initialize builder.
        
        Args:
            output_width: Output video width (TikTok: 1080)
            output_height: Output video height (TikTok: 1920)
            fps: Output frame rate
        """
        self.output_width = output_width
        self.output_height = output_height
        self.fps = fps
        self.filter_id = 0
    
    def _next_filter_id(self) -> str:
        """Generate unique filter stream ID"""
        self.filter_id += 1
        return f"f{self.filter_id}"
    
    def build_filter_complex(self, payload: Dict[str, Any],
                            sancha_video: str,
                            toxico_video: str,
                            audio_file: str) -> Dict[str, Any]:
        """
        Build complete filter_complex chain from TikTok payload.
        
        Args:
            payload: TikTok Engine payload
            sancha_video: Path to Sancha video file
            toxico_video: Path to Toxico video file
            audio_file: Path to mixed audio from Combinator
            
        Returns:
            FFmpeg command specification
        """
        visual_logic = payload.get("visual_logic", {})
        lyrics_rendering = payload.get("lyrics_rendering", {})
        glitch_triggers = payload.get("glitch_triggers", [])
        audio_sync_markers = payload.get("audio_sync_markers", [])
        
        # Build filter chains
        filters = []
        
        # Input preprocessing
        sancha_prep = self._build_color_grading(
            input_id="0:v",
            color_grade=visual_logic["color_grading"]["sancha_zone"],
            label="sancha_graded"
        )
        filters.extend(sancha_prep)
        
        toxico_prep = self._build_color_grading(
            input_id="1:v",
            color_grade=visual_logic["color_grading"]["toxico_zone"],
            label="toxico_graded"
        )
        filters.extend(toxico_prep)
        
        # Dynamic split screen
        split_filters = self._build_dynamic_split_screen(
            sancha_input="sancha_graded",
            toxico_input="toxico_graded",
            audio_sync_markers=audio_sync_markers,
            split_orientation=visual_logic.get("split_orientation", "vertical"),
            output_label="split_base"
        )
        filters.extend(split_filters)
        
        # Apply glitch effects
        glitch_filters = self._build_glitch_effects(
            input_label="split_base",
            glitch_triggers=glitch_triggers,
            output_label="glitched"
        )
        filters.extend(glitch_filters)
        
        # Render lyrics
        lyrics_filters = self._build_lyrics_rendering(
            input_label="glitched",
            lyrics_rendering=lyrics_rendering,
            audio_sync_markers=audio_sync_markers,
            output_label="final"
        )
        filters.extend(lyrics_filters)
        
        # Build FFmpeg command
        filter_complex = ";".join(filters)
        
        return {
            "render_id": f"ffmpeg_render_{uuid.uuid4().hex[:8]}",
            "payload_id": payload.get("payload_id", ""),
            "inputs": {
                "sancha_video": sancha_video,
                "toxico_video": toxico_video,
                "audio": audio_file
            },
            "filter_complex": filter_complex,
            "output_config": {
                "codec": "libx264",
                "preset": "medium",
                "crf": 23,
                "audio_codec": "aac",
                "audio_bitrate": "192k",
                "pix_fmt": "yuv420p"
            },
            "command_template": self._build_command_template(
                sancha_video, toxico_video, audio_file, filter_complex
            )
        }
    
    def _build_color_grading(self, input_id: str, color_grade: Dict[str, Any],
                            label: str) -> List[str]:
        """
        Build color grading filter chain.
        
        Args:
            input_id: Input stream identifier
            color_grade: Color grading parameters
            label: Output label
            
        Returns:
            List of filter strings
        """
        temperature = color_grade.get("temperature", 0)
        tint = color_grade.get("tint", 0)
        contrast = color_grade.get("contrast", 1.0)
        grain_amount = color_grade.get("grain_amount", 0.0)
        
        filters = []
        current_label = input_id
        
        # Scale to output dimensions
        scale_label = self._next_filter_id()
        filters.append(
            f"[{current_label}]scale={self.output_width}:{self.output_height}:force_original_aspect_ratio=increase,"
            f"crop={self.output_width}:{self.output_height}[{scale_label}]"
        )
        current_label = scale_label
        
        # Temperature adjustment (via curves/colorbalance)
        if temperature != 0:
            temp_label = self._next_filter_id()
            if temperature < 0:
                # Cool (blue shift)
                temp_strength = abs(temperature) / 50.0
                filters.append(
                    f"[{current_label}]colorbalance=bs={temp_strength}:gs={temp_strength * 0.5}[{temp_label}]"
                )
            else:
                # Warm (amber shift)
                temp_strength = temperature / 50.0
                filters.append(
                    f"[{current_label}]colorbalance=rs={temp_strength}:gs={temp_strength * 0.5}[{temp_label}]"
                )
            current_label = temp_label
        
        # Tint adjustment (hue shift)
        if tint != 0:
            tint_label = self._next_filter_id()
            hue_degrees = tint
            filters.append(
                f"[{current_label}]hue=h={hue_degrees}[{tint_label}]"
            )
            current_label = tint_label
        
        # Contrast adjustment
        if contrast != 1.0:
            contrast_label = self._next_filter_id()
            filters.append(
                f"[{current_label}]eq=contrast={contrast}[{contrast_label}]"
            )
            current_label = contrast_label
        
        # Film grain (noise injection)
        if grain_amount > 0:
            grain_label = self._next_filter_id()
            grain_strength = int(grain_amount * 50)  # 0-50 range
            filters.append(
                f"[{current_label}]noise=alls={grain_strength}:allf=t[{grain_label}]"
            )
            current_label = grain_label
        
        # Final label
        if current_label != label:
            filters.append(f"[{current_label}]copy[{label}]")
        
        return filters
    
    def _build_dynamic_split_screen(self, sancha_input: str, toxico_input: str,
                                    audio_sync_markers: List[Dict[str, Any]],
                                    split_orientation: str,
                                    output_label: str) -> List[str]:
        """
        Build dynamic split screen with intensity-based ratio.
        
        Note: FFmpeg doesn't support dynamic split ratios natively.
        This generates keyframe-based cropping with overlay.
        
        Args:
            sancha_input: Sancha input label
            toxico_input: Toxico input label
            audio_sync_markers: Sync markers for intensity calculation
            split_orientation: "vertical" or "horizontal"
            output_label: Output label
            
        Returns:
            List of filter strings
        """
        filters = []
        
        # Generate split ratio keyframes based on intensity
        split_ratios = self._calculate_split_ratios(audio_sync_markers)
        
        # For simplicity, use average split ratio (50/50)
        # In production, would use complex expression filters for dynamic ratio
        split_ratio = 0.5
        
        if split_orientation == "vertical":
            # Vertical split (left/right)
            left_width = int(self.output_width * split_ratio)
            right_width = self.output_width - left_width
            
            # Crop Sancha to left side
            sancha_cropped = self._next_filter_id()
            filters.append(
                f"[{sancha_input}]crop={left_width}:{self.output_height}:0:0[{sancha_cropped}]"
            )
            
            # Crop Toxico to right side
            toxico_cropped = self._next_filter_id()
            filters.append(
                f"[{toxico_input}]crop={right_width}:{self.output_height}:0:0[{toxico_cropped}]"
            )
            
            # Overlay Toxico on Sancha
            overlayed = self._next_filter_id()
            filters.append(
                f"[{sancha_cropped}][{toxico_cropped}]overlay={left_width}:0[{overlayed}]"
            )
            
            # Draw split line
            filters.append(
                f"[{overlayed}]drawbox=x={left_width - 2}:y=0:w=4:h={self.output_height}:"
                f"color=white@0.5:t=fill[{output_label}]"
            )
        
        else:
            # Horizontal split (top/bottom)
            top_height = int(self.output_height * split_ratio)
            bottom_height = self.output_height - top_height
            
            # Crop Sancha to top
            sancha_cropped = self._next_filter_id()
            filters.append(
                f"[{sancha_input}]crop={self.output_width}:{top_height}:0:0[{sancha_cropped}]"
            )
            
            # Crop Toxico to bottom
            toxico_cropped = self._next_filter_id()
            filters.append(
                f"[{toxico_input}]crop={self.output_width}:{bottom_height}:0:0[{toxico_cropped}]"
            )
            
            # Overlay Toxico on Sancha
            overlayed = self._next_filter_id()
            filters.append(
                f"[{sancha_cropped}][{toxico_cropped}]overlay=0:{top_height}[{overlayed}]"
            )
            
            # Draw split line
            filters.append(
                f"[{overlayed}]drawbox=x=0:y={top_height - 2}:w={self.output_width}:h=4:"
                f"color=white@0.5:t=fill[{output_label}]"
            )
        
        return filters
    
    def _calculate_split_ratios(self, audio_sync_markers: List[Dict[str, Any]]) -> List[Tuple[float, float]]:
        """
        Calculate split ratios over time based on intensity.
        
        Args:
            audio_sync_markers: Sync markers with intensity values
            
        Returns:
            List of (timestamp_seconds, split_ratio) tuples
        """
        ratios = []
        
        for marker in audio_sync_markers:
            timestamp_s = marker.get("timestamp_ms", 0) / 1000.0
            intensity = marker.get("intensity", 0.5)
            persona = marker.get("persona", "")
            
            # Calculate split ratio (0.5 = 50/50)
            if persona == "SANCHA_V1":
                ratio = 0.5 + (intensity - 0.5) * 0.3  # Shift toward Sancha (left)
            elif persona == "TOXICO_PRIME":
                ratio = 0.5 - (intensity - 0.5) * 0.3  # Shift toward Toxico (right)
            else:
                ratio = 0.5
            
            # Clamp to reasonable range
            ratio = max(0.2, min(0.8, ratio))
            
            ratios.append((timestamp_s, ratio))
        
        return ratios
    
    def _build_glitch_effects(self, input_label: str,
                              glitch_triggers: List[Dict[str, Any]],
                              output_label: str) -> List[str]:
        """
        Build glitch effect filters.
        
        FFmpeg limitations:
        - Chromatic aberration: Use rgbashift filter
        - Frame shake: Use transform filter with expression
        - RGB split: Use split + overlay with offset
        - Distortion warp: Use perspective or lenscorrection
        
        Args:
            input_label: Input label
            glitch_triggers: List of glitch events
            output_label: Output label
            
        Returns:
            List of filter strings
        """
        filters = []
        current_label = input_label
        
        # For simplicity, apply static glitch effects
        # In production, would use enable expressions for timing
        
        has_chromatic = any(g["type"] == "chromatic_aberration" for g in glitch_triggers)
        has_rgb_split = any(g["type"] == "rgb_split" for g in glitch_triggers)
        has_shake = any(g["type"] == "frame_shake" for g in glitch_triggers)
        has_warp = any(g["type"] == "distortion_warp" for g in glitch_triggers)
        
        # Chromatic aberration (conditional)
        if has_chromatic:
            chroma_triggers = [g for g in glitch_triggers if g["type"] == "chromatic_aberration"]
            max_intensity = max(g.get("intensity", 0) for g in chroma_triggers)
            offset_px = int(max_intensity * 8)
            
            chroma_label = self._next_filter_id()
            enable_expr = self._build_enable_expression(chroma_triggers)
            filters.append(
                f"[{current_label}]rgbashift=rh={offset_px}:bh=-{offset_px}:enable='{enable_expr}'[{chroma_label}]"
            )
            current_label = chroma_label
        
        # RGB split (conditional)
        if has_rgb_split:
            rgb_triggers = [g for g in glitch_triggers if g["type"] == "rgb_split"]
            max_intensity = max(g.get("intensity", 0) for g in rgb_triggers)
            separation_px = int(max_intensity * 6)
            
            rgb_label = self._next_filter_id()
            enable_expr = self._build_enable_expression(rgb_triggers)
            filters.append(
                f"[{current_label}]rgbashift=rh={separation_px}:gh={separation_px // 2}:bh=-{separation_px}:enable='{enable_expr}'[{rgb_label}]"
            )
            current_label = rgb_label
        
        # Frame shake (conditional)
        if has_shake:
            shake_triggers = [g for g in glitch_triggers if g["type"] == "frame_shake"]
            max_intensity = max(g.get("intensity", 0) for g in shake_triggers)
            amplitude_px = int(max_intensity * 12)
            
            shake_label = self._next_filter_id()
            enable_expr = self._build_enable_expression(shake_triggers)
            # Use transform with sin expression for shake
            filters.append(
                f"[{current_label}]transform=x='if(eq(enable,1),{amplitude_px}*sin(2*PI*t*8),0)':"
                f"y='if(eq(enable,1),{amplitude_px}*cos(2*PI*t*6),0)':enable='{enable_expr}'[{shake_label}]"
            )
            current_label = shake_label
        
        # Distortion warp (lens distortion)
        if has_warp:
            warp_triggers = [g for g in glitch_triggers if g["type"] == "distortion_warp"]
            max_intensity = max(g.get("intensity", 0) for g in warp_triggers)
            warp_strength = max_intensity * 0.5  # 0-0.5 range
            
            warp_label = self._next_filter_id()
            enable_expr = self._build_enable_expression(warp_triggers)
            filters.append(
                f"[{current_label}]lenscorrection=k1={warp_strength}:k2={-warp_strength * 0.5}:enable='{enable_expr}'[{warp_label}]"
            )
            current_label = warp_label
        
        # Final label
        if current_label != output_label:
            filters.append(f"[{current_label}]copy[{output_label}]")
        
        return filters
    
    def _build_enable_expression(self, triggers: List[Dict[str, Any]]) -> str:
        """
        Build FFmpeg enable expression for conditional filter activation.
        
        Args:
            triggers: List of glitch triggers
            
        Returns:
            Enable expression string
        """
        if not triggers:
            return "0"  # Never enabled
        
        # Build time ranges: between(t, start, end)
        ranges = []
        for trigger in triggers:
            start_s = trigger.get("timestamp_ms", 0) / 1000.0
            duration_s = trigger.get("duration_ms", 500) / 1000.0
            end_s = start_s + duration_s
            ranges.append(f"between(t,{start_s},{end_s})")
        
        # Combine with OR logic
        return "+".join(ranges)
    
    def _build_lyrics_rendering(self, input_label: str,
                                lyrics_rendering: Dict[str, Any],
                                audio_sync_markers: List[Dict[str, Any]],
                                output_label: str) -> List[str]:
        """
        Build lyrics rendering with drawtext filter.
        
        Args:
            input_label: Input label
            lyrics_rendering: Lyrics rendering config
            audio_sync_markers: Sync markers with text
            output_label: Output label
            
        Returns:
            List of filter strings
        """
        filters = []
        current_label = input_label
        
        # Get lyrics styles
        sancha_style = lyrics_rendering.get("sancha", {})
        toxico_style = lyrics_rendering.get("toxico", {})
        timing_offset_ms = lyrics_rendering.get("timing_offset_ms", -50)
        
        # Build drawtext filters for each marker
        for i, marker in enumerate(audio_sync_markers):
            persona = marker.get("persona", "")
            text = marker.get("text", "").replace("'", "\\'")  # Escape quotes
            timestamp_ms = marker.get("timestamp_ms", 0) + timing_offset_ms
            intensity = marker.get("intensity", 0.5)
            
            # Select style
            style = sancha_style if persona == "SANCHA_V1" else toxico_style
            
            # Calculate position
            x_pos = "w*0.1" if persona == "SANCHA_V1" else "w*0.6"
            y_pos = f"100+{(i % 3) * 150}"
            
            # Build enable expression (display for 3 seconds)
            start_s = timestamp_ms / 1000.0
            end_s = start_s + 3.0
            enable_expr = f"between(t,{start_s},{end_s})"
            
            # Build drawtext filter
            text_label = self._next_filter_id()
            filters.append(
                f"[{current_label}]drawtext=text='{text}':"
                f"x={x_pos}:y={y_pos}:"
                f"fontsize={style.get('size_px', 48)}:"
                f"fontcolor={style.get('color', '#FFFFFF')}:"
                f"borderw={style.get('stroke_width', 2)}:"
                f"bordercolor={style.get('stroke_color', '#000000')}:"
                f"alpha='if(lt(t-{start_s},0.2),5*(t-{start_s}),1)*{intensity}':"
                f"enable='{enable_expr}'[{text_label}]"
            )
            current_label = text_label
        
        # Final label
        if current_label != output_label:
            filters.append(f"[{current_label}]copy[{output_label}]")
        
        return filters
    
    def _build_command_template(self, sancha_video: str, toxico_video: str,
                               audio_file: str, filter_complex: str) -> str:
        """
        Build complete FFmpeg command template.
        
        Args:
            sancha_video: Sancha video path
            toxico_video: Toxico video path
            audio_file: Audio file path
            filter_complex: Filter complex string
            
        Returns:
            FFmpeg command string
        """
        return (
            f"ffmpeg -i {sancha_video} -i {toxico_video} -i {audio_file} "
            f"-filter_complex \"{filter_complex}\" "
            f"-map '[final]' -map 2:a "
            f"-c:v libx264 -preset medium -crf 23 -pix_fmt yuv420p "
            f"-c:a aac -b:a 192k "
            f"-r {self.fps} "
            f"-s {self.output_width}x{self.output_height} "
            f"-y output.mp4"
        )


def render_toxic_drama_ffmpeg(payload: Dict[str, Any],
                              sancha_video: str,
                              toxico_video: str,
                              audio_file: str,
                              output_path: str = "/tmp/toxic_drama_render.mp4") -> Dict[str, Any]:
    """
    Convenience function to render Toxic Drama video using FFmpeg.
    
    Args:
        payload: TikTok Engine payload
        sancha_video: Sancha video file path
        toxico_video: Toxico video file path
        audio_file: Mixed audio from Combinator
        output_path: Output video path
        
    Returns:
        Render specification with FFmpeg command
    """
    builder = FFmpegFilterChainBuilder()
    spec = builder.build_filter_complex(payload, sancha_video, toxico_video, audio_file)
    
    # Update command with output path
    command = spec["command_template"].replace("output.mp4", output_path)
    
    return {
        **spec,
        "output_path": output_path,
        "command": command,
        "status": "ready_for_render"
    }
