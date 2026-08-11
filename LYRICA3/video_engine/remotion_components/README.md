# Remotion Components - Toxic Drama Split-Screen

Dynamic split-screen video rendering using Remotion for Toxic Drama scenes.

## Features

- **Dynamic Split Ratio**: Screen split adjusts based on persona intensity (0.2-0.8 range)
- **Color Grading Zones**: 
  - Sancha: Cool cyan (-15 temp, +10 tint, 20% grain)
  - Toxico: Harsh amber (+25 temp, -8 tint, 50% grain, 1.3x contrast)
- **Glitch Effects**:
  - Chromatic Aberration (8px max offset, spring easing)
  - Frame Shake (12px max amplitude, sine wave decay)
  - RGB Split (6px max separation, spring release)
  - Distortion Warp (5% max perspective warp, 3D transform)
- **Lyrics Rendering**: Alternating vertical positioning with persona-specific styling

## File Structure

```
/home/shiestybizz/sla113/LYRICA3/video_engine/remotion_components/
├── ToxicDramaSplitScreen.tsx  # Main composition component
├── Root.tsx                    # Remotion entry point
├── package.json                # Dependencies
├── tsconfig.json               # TypeScript config
└── README.md                   # This file
```

## Installation

```bash
cd /home/shiestybizz/sla113/LYRICA3/video_engine/remotion_components
npm install
```

## Development

```bash
npm run dev
```

Opens Remotion Studio at http://localhost:3000

## Rendering

### Single Video Render
```bash
npm run render
```

Output: `output/toxic_drama.mp4` (1080x1920 @ 30fps)

### Lambda Render (AWS)
```bash
npm run render-lambda
```

Deploys to AWS Lambda for serverless rendering.

## Integration with TikTok Engine

The component consumes TikTok Engine payloads exported from:
```python
from LYRICA3.soulfire_engine.tiktok_engine import TikTokEngine

engine = TikTokEngine()
payload = engine.generate_payload(sancha_pfa, toxico_pfa, scene_metadata)
engine.export_to_file(payload, '/path/to/payload.json')
```

Load payload in Remotion:
```typescript
import payload from './payloads/toxic_drama_scene.json';

<Composition
  defaultProps={{
    payload: payload,
    sanchaVideoSrc: '/assets/sancha.mp4',
    toxicoVideoSrc: '/assets/toxico.mp4',
    audioSrc: '/assets/audio.wav'
  }}
/>
```

## Component Architecture

### ToxicDramaSplitScreen
Main composition that orchestrates all visual elements.

**Props:**
- `payload`: TikTok Engine payload
- `sanchaVideoSrc`: Sancha video source URL
- `toxicoVideoSrc`: Toxico video source URL
- `audioSrc`: Mixed audio from Combinator

**Render Flow:**
1. Calculate dynamic split ratio from intensity values
2. Apply color grading to both zones
3. Detect active glitch effects based on timestamp
4. Render frame shake → distortion warp → split screens
5. Apply chromatic aberration + RGB split overlays
6. Render lyrics layer with timing offset

### Glitch Effect Components

#### ChromaticAberration
- Red/blue channel separation
- Spring easing (damping: 10, stiffness: 100)
- Intensity scales offset (0-8px)

#### FrameShake
- Sine wave shake with exponential decay
- 8 horizontal cycles, 6 vertical cycles
- Intensity scales amplitude (0-12px)

#### RGBSplit
- R/G/B channel separation
- Spring release (damping: 15, stiffness: 120)
- Intensity scales separation (0-6px)

#### DistortionWarp
- 3D perspective warp
- Spring easing (damping: 12, stiffness: 90)
- Intensity scales rotation (0-5deg)

### LyricsLayer
- Reads audio_sync_markers from payload
- Applies timing_offset_ms (-50ms by default)
- Fades in over 10 frames (spring animation)
- Alternating vertical positioning (100px + index * 150px)
- Persona-specific styling (font, color, stroke)

## Performance

### Frame Budget (30fps)
- **Target**: 33.3ms per frame
- **Typical render**: 15-25ms per frame
- **With all glitches active**: 30-40ms per frame

### Optimization
- Video elements use hardware acceleration
- Glitch effects conditionally rendered (only when active)
- Color grading applied via CSS filters (GPU-accelerated)
- Spring animations cached by Remotion

### Lambda Rendering
- Parallel rendering across multiple workers
- 60-second video renders in ~2-3 minutes (distributed)
- Cost: ~$0.05-0.10 per video (AWS Lambda)

## Output Specifications

- **Resolution**: 1080x1920 (TikTok vertical)
- **Frame Rate**: 30fps
- **Codec**: H.264
- **Audio Codec**: AAC
- **Bitrate**: 8 Mbps (video), 192 kbps (audio)

## Rule: EVOLVE NEVER DELETE

This component extends the Toxic Drama system without modifying:
- TikTok Engine (`tiktok_engine.py`)
- Glitch Logic Engine (`glitch_logic.py`)
- SSS Presets (`sss_presets.py`)
- Combinator (`combinator.py`)

All integrations are additive through prop-based composition.
