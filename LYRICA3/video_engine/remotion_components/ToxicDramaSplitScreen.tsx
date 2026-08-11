/**
 * ToxicDramaSplitScreen - Remotion Composition
 * Dynamic split-screen video rendering for Toxic Drama scenes
 * 
 * Part of: SLA-113 | Lyrica3 Soulfire Engine | Toxic Drama Expansion
 * Rule: EVOLVE NEVER DELETE
 * 
 * Consumes: TikTok Engine payload + glitch events from GlitchLogicEngine
 * Outputs: 1080x1920 @ 30fps TikTok vertical video
 */

import React from 'react';
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Sequence,
} from 'remotion';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

interface TikTokPayload {
  payload_id: string;
  template_id: string;
  visual_logic: VisualLogic;
  lyrics_rendering: LyricsRendering;
  glitch_triggers: GlitchTrigger[];
  audio_sync_markers: AudioSyncMarker[];
  output_config: {
    duration_ms: number;
    resolution: string;
    fps: number;
  };
}

interface VisualLogic {
  split_ratio: string; // "dynamic"
  split_orientation: string; // "vertical"
  transition_speed_ms: number;
  color_grading: {
    sancha_zone: ColorGrade;
    toxico_zone: ColorGrade;
  };
}

interface ColorGrade {
  preset: string;
  temperature: number;
  tint: number;
  grain_amount: number;
  contrast?: number;
}

interface GlitchTrigger {
  timestamp_ms: number;
  type: 'chromatic_aberration' | 'frame_shake' | 'rgb_split' | 'distortion_warp';
  intensity: number;
  duration_ms: number;
  source_persona: 'SANCHA_V1' | 'TOXICO_PRIME';
  easing?: string;
  frame_events?: any[];
}

interface AudioSyncMarker {
  timestamp_ms: number;
  persona: 'SANCHA_V1' | 'TOXICO_PRIME';
  text: string;
  intensity: number;
  type?: string;
}

interface LyricsRendering {
  sancha: LyricsStyle;
  toxico: LyricsStyle;
  alignment: string;
  timing_offset_ms: number;
}

interface LyricsStyle {
  font: string;
  size_px: number;
  color: string;
  stroke_color: string;
  stroke_width: number;
  animation: string;
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Convert milliseconds to frame number
 */
const msToFrame = (ms: number, fps: number): number => {
  return Math.floor((ms / 1000) * fps);
};

/**
 * Calculate dynamic split ratio based on intensity
 * Higher intensity persona gets more screen space
 */
const calculateSplitRatio = (
  sanchaIntensity: number,
  toxicoIntensity: number,
  frame: number,
  fps: number
): number => {
  const intensityDiff = sanchaIntensity - toxicoIntensity;
  
  // Base split at 50/50
  let targetRatio = 0.5;
  
  // Shift toward higher intensity persona
  // +0.3 max shift (0.2 to 0.8 range)
  targetRatio += intensityDiff * 0.3;
  
  // Clamp to reasonable bounds
  targetRatio = Math.max(0.2, Math.min(0.8, targetRatio));
  
  // Smooth transition with spring
  const sprung = spring({
    frame,
    fps,
    config: {
      damping: 20,
      stiffness: 80,
      mass: 1,
    },
  });
  
  return interpolate(sprung, [0, 1], [0.5, targetRatio]);
};

/**
 * Apply color grading transform
 */
const applyColorGrading = (grade: ColorGrade): React.CSSProperties => {
  const {temperature, tint, grain_amount, contrast = 1.0} = grade;
  
  // Temperature: negative = cool (blue), positive = warm (amber)
  const tempFilter = temperature < 0
    ? `sepia(${Math.abs(temperature) / 50}) hue-rotate(180deg)`
    : `sepia(${temperature / 50}) hue-rotate(20deg)`;
  
  // Tint: cyan/magenta shift
  const tintFilter = tint !== 0
    ? `hue-rotate(${tint}deg)`
    : '';
  
  return {
    filter: `${tempFilter} ${tintFilter} contrast(${contrast}) brightness(1.0)`,
    // Film grain applied via ::after pseudo-element
  };
};

// ============================================================================
// GLITCH EFFECT COMPONENTS
// ============================================================================

/**
 * Chromatic Aberration Effect
 * Red/Blue channel separation for emotional cracks
 */
const ChromaticAberration: React.FC<{
  active: boolean;
  intensity: number;
  duration_ms: number;
  frame: number;
  fps: number;
}> = ({active, intensity, duration_ms, frame, fps}) => {
  if (!active) return null;
  
  const offsetPx = intensity * 8; // Max 8px offset at intensity=1.0
  
  const progress = spring({
    frame,
    fps,
    config: {
      damping: 10,
      stiffness: 100,
    },
    durationInFrames: msToFrame(duration_ms, fps),
  });
  
  const currentOffset = interpolate(progress, [0, 0.5, 1], [0, offsetPx, 0]);
  
  return (
    <AbsoluteFill
      style={{
        mixBlendMode: 'screen',
        pointerEvents: 'none',
      }}
    >
      {/* Red channel */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          transform: `translateX(${currentOffset}px)`,
          opacity: 0.8,
          mixBlendMode: 'lighten',
          backgroundColor: 'rgba(255, 0, 0, 0.2)',
        }}
      />
      {/* Blue channel */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          transform: `translateX(${-currentOffset}px)`,
          opacity: 0.8,
          mixBlendMode: 'lighten',
          backgroundColor: 'rgba(0, 0, 255, 0.2)',
        }}
      />
    </AbsoluteFill>
  );
};

/**
 * Frame Shake Effect
 * Camera shake for distortion spikes
 */
const FrameShake: React.FC<{
  active: boolean;
  intensity: number;
  duration_ms: number;
  frame: number;
  fps: number;
  children: React.ReactNode;
}> = ({active, intensity, duration_ms, frame, fps, children}) => {
  if (!active) {
    return <>{children}</>;
  }
  
  const amplitudePx = intensity * 12; // Max 12px shake at intensity=1.0
  
  const durationFrames = msToFrame(duration_ms, fps);
  const progress = (frame % durationFrames) / durationFrames;
  
  // Sine wave shake with exponential decay
  const shakeX = Math.sin(progress * Math.PI * 8) * amplitudePx * (1 - progress);
  const shakeY = Math.cos(progress * Math.PI * 6) * amplitudePx * (1 - progress);
  
  return (
    <div
      style={{
        transform: `translate(${shakeX}px, ${shakeY}px)`,
        width: '100%',
        height: '100%',
      }}
    >
      {children}
    </div>
  );
};

/**
 * RGB Split Effect
 * Channel separation for interruption moments
 */
const RGBSplit: React.FC<{
  active: boolean;
  intensity: number;
  duration_ms: number;
  frame: number;
  fps: number;
}> = ({active, intensity, duration_ms, frame, fps}) => {
  if (!active) return null;
  
  const separationPx = intensity * 6; // Max 6px separation at intensity=1.0
  
  const progress = spring({
    frame,
    fps,
    config: {
      damping: 15,
      stiffness: 120,
    },
    durationInFrames: msToFrame(duration_ms, fps),
  });
  
  const currentSeparation = interpolate(progress, [0, 1], [separationPx, 0]);
  
  return (
    <AbsoluteFill
      style={{
        mixBlendMode: 'screen',
        pointerEvents: 'none',
      }}
    >
      {/* R channel */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          transform: `translate(${currentSeparation}px, 0)`,
          opacity: 0.7,
          backgroundColor: 'rgba(255, 0, 0, 0.15)',
        }}
      />
      {/* G channel */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          transform: `translate(0, ${currentSeparation * 0.5}px)`,
          opacity: 0.7,
          backgroundColor: 'rgba(0, 255, 0, 0.15)',
        }}
      />
      {/* B channel */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          transform: `translate(${-currentSeparation}px, 0)`,
          opacity: 0.7,
          backgroundColor: 'rgba(0, 0, 255, 0.15)',
        }}
      />
    </AbsoluteFill>
  );
};

/**
 * Distortion Warp Effect
 * Lens distortion for intense moments
 */
const DistortionWarp: React.FC<{
  active: boolean;
  intensity: number;
  duration_ms: number;
  frame: number;
  fps: number;
  children: React.ReactNode;
}> = ({active, intensity, duration_ms, frame, fps, children}) => {
  if (!active) {
    return <>{children}</>;
  }
  
  const warpAmount = intensity * 5; // Max 5% warp at intensity=1.0
  
  const progress = spring({
    frame,
    fps,
    config: {
      damping: 12,
      stiffness: 90,
    },
    durationInFrames: msToFrame(duration_ms, fps),
  });
  
  const currentWarp = interpolate(progress, [0, 0.5, 1], [0, warpAmount, 0]);
  
  return (
    <div
      style={{
        transform: `perspective(1000px) rotateY(${currentWarp}deg)`,
        transformStyle: 'preserve-3d',
        width: '100%',
        height: '100%',
      }}
    >
      {children}
    </div>
  );
};

// ============================================================================
// MAIN COMPOSITION COMPONENT
// ============================================================================

export const ToxicDramaSplitScreen: React.FC<{
  payload: TikTokPayload;
  sanchaVideoSrc: string;
  toxicoVideoSrc: string;
  audioSrc: string;
}> = ({payload, sanchaVideoSrc, toxicoVideoSrc, audioSrc}) => {
  const frame = useCurrentFrame();
  const {fps, width, height} = useVideoConfig();
  
  const currentTimeMs = (frame / fps) * 1000;
  
  // Find current audio sync markers for intensity calculation
  const currentSanchaMarker = payload.audio_sync_markers
    .filter(m => m.persona === 'SANCHA_V1' && m.timestamp_ms <= currentTimeMs)
    .sort((a, b) => b.timestamp_ms - a.timestamp_ms)[0];
  
  const currentToxicoMarker = payload.audio_sync_markers
    .filter(m => m.persona === 'TOXICO_PRIME' && m.timestamp_ms <= currentTimeMs)
    .sort((a, b) => b.timestamp_ms - a.timestamp_ms)[0];
  
  const sanchaIntensity = currentSanchaMarker?.intensity ?? 0.5;
  const toxicoIntensity = currentToxicoMarker?.intensity ?? 0.5;
  
  // Calculate dynamic split ratio
  const splitRatio = calculateSplitRatio(sanchaIntensity, toxicoIntensity, frame, fps);
  
  // Find active glitch effects
  const activeGlitches = payload.glitch_triggers.filter(
    g => currentTimeMs >= g.timestamp_ms && currentTimeMs <= g.timestamp_ms + g.duration_ms
  );
  
  const chromaGlitch = activeGlitches.find(g => g.type === 'chromatic_aberration');
  const shakeGlitch = activeGlitches.find(g => g.type === 'frame_shake');
  const rgbGlitch = activeGlitches.find(g => g.type === 'rgb_split');
  const warpGlitch = activeGlitches.find(g => g.type === 'distortion_warp');
  
  const glitchFrame = chromaGlitch 
    ? frame - msToFrame(chromaGlitch.timestamp_ms, fps)
    : frame;
  
  // Color grading zones
  const sanchaGrade = payload.visual_logic.color_grading.sancha_zone;
  const toxicoGrade = payload.visual_logic.color_grading.toxico_zone;
  
  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      {/* Apply frame shake to entire composition */}
      <FrameShake
        active={!!shakeGlitch}
        intensity={shakeGlitch?.intensity ?? 0}
        duration_ms={shakeGlitch?.duration_ms ?? 0}
        frame={glitchFrame}
        fps={fps}
      >
        {/* Apply distortion warp */}
        <DistortionWarp
          active={!!warpGlitch}
          intensity={warpGlitch?.intensity ?? 0}
          duration_ms={warpGlitch?.duration_ms ?? 0}
          frame={glitchFrame}
          fps={fps}
        >
          {/* Sancha's zone (left side) */}
          <div
            style={{
              position: 'absolute',
              left: 0,
              top: 0,
              width: `${splitRatio * 100}%`,
              height: '100%',
              overflow: 'hidden',
              ...applyColorGrading(sanchaGrade),
            }}
          >
            {/* Sancha video background */}
            <video
              src={sanchaVideoSrc}
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover',
              }}
            />
            
            {/* Film grain overlay */}
            <div
              style={{
                position: 'absolute',
                inset: 0,
                backgroundImage: 'url(/grain-texture.png)',
                opacity: sanchaGrade.grain_amount,
                mixBlendMode: 'overlay',
                pointerEvents: 'none',
              }}
            />
          </div>
          
          {/* Toxico's zone (right side) */}
          <div
            style={{
              position: 'absolute',
              right: 0,
              top: 0,
              width: `${(1 - splitRatio) * 100}%`,
              height: '100%',
              overflow: 'hidden',
              ...applyColorGrading(toxicoGrade),
            }}
          >
            {/* Toxico video background */}
            <video
              src={toxicoVideoSrc}
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover',
              }}
            />
            
            {/* Film grain overlay */}
            <div
              style={{
                position: 'absolute',
                inset: 0,
                backgroundImage: 'url(/grain-texture.png)',
                opacity: toxicoGrade.grain_amount,
                mixBlendMode: 'overlay',
                pointerEvents: 'none',
              }}
            />
          </div>
          
          {/* Vertical split line */}
          <div
            style={{
              position: 'absolute',
              left: `${splitRatio * 100}%`,
              top: 0,
              width: '4px',
              height: '100%',
              background: 'linear-gradient(to right, rgba(255,255,255,0.3), rgba(255,255,255,0.8), rgba(255,255,255,0.3))',
              boxShadow: '0 0 20px rgba(255,255,255,0.5)',
              transform: 'translateX(-2px)',
            }}
          />
        </DistortionWarp>
      </FrameShake>
      
      {/* Glitch overlays (applied on top) */}
      <ChromaticAberration
        active={!!chromaGlitch}
        intensity={chromaGlitch?.intensity ?? 0}
        duration_ms={chromaGlitch?.duration_ms ?? 0}
        frame={glitchFrame}
        fps={fps}
      />
      
      <RGBSplit
        active={!!rgbGlitch}
        intensity={rgbGlitch?.intensity ?? 0}
        duration_ms={rgbGlitch?.duration_ms ?? 0}
        frame={glitchFrame}
        fps={fps}
      />
      
      {/* Lyrics rendering layer */}
      <LyricsLayer
        payload={payload}
        currentTimeMs={currentTimeMs}
        frame={frame}
        fps={fps}
      />
    </AbsoluteFill>
  );
};

// ============================================================================
// LYRICS RENDERING COMPONENT
// ============================================================================

const LyricsLayer: React.FC<{
  payload: TikTokPayload;
  currentTimeMs: number;
  frame: number;
  fps: number;
}> = ({payload, currentTimeMs, frame, fps}) => {
  const {lyrics_rendering, audio_sync_markers} = payload;
  const timingOffset = lyrics_rendering.timing_offset_ms;
  
  // Find visible lyrics (within display window)
  const visibleMarkers = audio_sync_markers.filter(
    m => {
      const adjustedTime = m.timestamp_ms + timingOffset;
      const displayDuration = 3000; // Show for 3 seconds
      return currentTimeMs >= adjustedTime && currentTimeMs <= adjustedTime + displayDuration;
    }
  );
  
  return (
    <AbsoluteFill style={{pointerEvents: 'none'}}>
      {visibleMarkers.map((marker, index) => {
        const style = marker.persona === 'SANCHA_V1'
          ? lyrics_rendering.sancha
          : lyrics_rendering.toxico;
        
        const markerFrame = frame - msToFrame(marker.timestamp_ms + timingOffset, fps);
        
        // Fade in animation
        const opacity = spring({
          frame: markerFrame,
          fps,
          config: {damping: 20, stiffness: 80},
          durationInFrames: 10,
        });
        
        // Positioning (alternating vertical)
        const yPosition = 100 + (index % 3) * 150;
        
        return (
          <div
            key={marker.timestamp_ms}
            style={{
              position: 'absolute',
              left: marker.persona === 'SANCHA_V1' ? '10%' : '60%',
              top: `${yPosition}px`,
              fontFamily: style.font,
              fontSize: `${style.size_px}px`,
              color: style.color,
              textShadow: `
                ${style.stroke_width}px ${style.stroke_width}px 0 ${style.stroke_color},
                -${style.stroke_width}px -${style.stroke_width}px 0 ${style.stroke_color},
                ${style.stroke_width}px -${style.stroke_width}px 0 ${style.stroke_color},
                -${style.stroke_width}px ${style.stroke_width}px 0 ${style.stroke_color}
              `,
              opacity: opacity * marker.intensity,
              maxWidth: '35%',
              wordBreak: 'break-word',
            }}
          >
            {marker.text}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

export default ToxicDramaSplitScreen;
