/**
 * Remotion Video Root Composition
 * Entry point for rendering Toxic Drama videos
 * 
 * Part of: SLA-113 | Lyrica3 Soulfire Engine | Toxic Drama Expansion
 * Rule: EVOLVE NEVER DELETE
 */

import {Composition} from 'remotion';
import {ToxicDramaSplitScreen} from './ToxicDramaSplitScreen';

// Import TikTok payload (in production, this would be dynamically loaded)
// import toxicPayload from './payloads/toxic_drama_scene.json';

/**
 * Example payload structure (loaded from TikTok Engine export)
 */
const examplePayload = {
  payload_id: 'tiktok_example',
  template_id: 'TOXIC_CONFLICT_SPLIT',
  visual_logic: {
    split_ratio: 'dynamic',
    split_orientation: 'vertical',
    transition_speed_ms: 300,
    color_grading: {
      sancha_zone: {
        preset: 'cool_cyan_distant',
        temperature: -15,
        tint: 10,
        grain_amount: 0.2,
        contrast: 1.0,
      },
      toxico_zone: {
        preset: 'harsh_amber_grain',
        temperature: 25,
        tint: -8,
        grain_amount: 0.5,
        contrast: 1.3,
      },
    },
  },
  lyrics_rendering: {
    sancha: {
      font: 'Elegant_Script_Broken',
      size_px: 48,
      color: '#E0F7FF',
      stroke_color: '#003344',
      stroke_width: 2,
      animation: 'fade_in_broken',
    },
    toxico: {
      font: 'Heavy_Industrial_Impact',
      size_px: 56,
      color: '#FFD700',
      stroke_color: '#331100',
      stroke_width: 3,
      animation: 'punch_in_aggressive',
    },
    alignment: 'alternating_vertical',
    timing_offset_ms: -50,
  },
  glitch_triggers: [],
  audio_sync_markers: [],
  output_config: {
    duration_ms: 60000,
    resolution: '1080x1920',
    fps: 30,
  },
};

/**
 * Root composition for Remotion
 */
export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="ToxicDrama"
        component={ToxicDramaSplitScreen}
        durationInFrames={1800} // 60 seconds at 30fps
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          payload: examplePayload,
          sanchaVideoSrc: '/assets/sancha_video.mp4',
          toxicoVideoSrc: '/assets/toxico_video.mp4',
          audioSrc: '/assets/toxic_drama_audio.wav',
        }}
      />
    </>
  );
};
