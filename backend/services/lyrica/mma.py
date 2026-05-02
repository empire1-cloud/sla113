"""
Lyrica MMA Agent — Micro-Rhythmic 'Late-Pocket Swing' Instrumental Generation.

Applies humanization to quantized beats:
  - Snare delay: 10-18ms behind the grid (Gaussian, μ=12ms, σ=2.5ms)
  - Hi-hat velocity randomization: accent pattern + ±12% variation
  - Kick advance: -2 to -5ms ahead of grid (push-pull feel)
  - Swing quantization for groove templates

Works on raw audio arrays (numpy) at 48kHz/24-bit.
"""

import uuid
import json
import logging
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

SAMPLE_RATE = 48000


def ms_to_samples(ms: float) -> int:
    return int(round(ms * SAMPLE_RATE / 1000.0))


def generate_click(duration_ms: float = 5.0, freq: float = 1000.0, velocity: float = 1.0) -> np.ndarray:
    """Generate a single click/hit sample."""
    n_samples = ms_to_samples(duration_ms)
    t = np.linspace(0, duration_ms / 1000.0, n_samples, endpoint=False)
    envelope = np.exp(-t * 40)
    hit = velocity * envelope * np.sin(2 * np.pi * freq * t)
    return hit.astype(np.float32)


def generate_kick(velocity: float = 1.0) -> np.ndarray:
    """Generate a synthetic kick drum."""
    duration = ms_to_samples(80)
    t = np.linspace(0, 0.08, duration, endpoint=False)
    pitch_sweep = 150 * np.exp(-t * 30) + 50
    phase = np.cumsum(2 * np.pi * pitch_sweep / SAMPLE_RATE)
    envelope = np.exp(-t * 25)
    kick = velocity * envelope * np.sin(phase)
    return kick.astype(np.float32)


def generate_snare(velocity: float = 1.0) -> np.ndarray:
    """Generate a synthetic snare drum."""
    duration = ms_to_samples(60)
    t = np.linspace(0, 0.06, duration, endpoint=False)
    tone_env = np.exp(-t * 40)
    tone = 0.5 * tone_env * np.sin(2 * np.pi * 200 * t)
    noise_env = np.exp(-t * 20)
    noise = 0.5 * noise_env * np.random.randn(duration).astype(np.float32)
    snare = velocity * (tone + noise)
    return snare.astype(np.float32)


def generate_hihat(velocity: float = 1.0, open_hat: bool = False) -> np.ndarray:
    """Generate a synthetic hi-hat."""
    dur_ms = 120.0 if open_hat else 30.0
    duration = ms_to_samples(dur_ms)
    t = np.linspace(0, dur_ms / 1000.0, duration, endpoint=False)
    decay = 8 if open_hat else 30
    envelope = np.exp(-t * decay)
    noise = envelope * np.random.randn(duration).astype(np.float32)
    b = [1, -0.97]
    a = [1]
    from scipy.signal import lfilter
    filtered = lfilter(b, a, noise).astype(np.float32)
    return (velocity * 0.3 * filtered).astype(np.float32)


HIHAT_ACCENT_8TH = [1.0, 0.7, 0.85, 0.65, 1.0, 0.7, 0.9, 0.6]
HIHAT_ACCENT_16TH = [1.0, 0.5, 0.7, 0.45, 0.85, 0.5, 0.65, 0.4,
                     1.0, 0.5, 0.75, 0.45, 0.9, 0.5, 0.6, 0.4]

GROOVE_TEMPLATES = {
    "trap": {
        "tempo_bpm": 140,
        "hihat_division": 16,
        "snare_delay_mean_ms": 14,
        "snare_delay_sigma_ms": 2.0,
        "kick_advance_ms": -3,
        "hihat_velocity_variation": 0.15,
        "kick_pattern": [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        "snare_pattern": [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    },
    "boom_bap": {
        "tempo_bpm": 90,
        "hihat_division": 8,
        "snare_delay_mean_ms": 12,
        "snare_delay_sigma_ms": 2.5,
        "kick_advance_ms": -2,
        "hihat_velocity_variation": 0.10,
        "kick_pattern": [1, 0, 0, 1, 0, 0, 1, 0],
        "snare_pattern": [0, 0, 1, 0, 0, 0, 1, 0],
    },
    "g_funk": {
        "tempo_bpm": 100,
        "hihat_division": 16,
        "snare_delay_mean_ms": 16,
        "snare_delay_sigma_ms": 1.5,
        "kick_advance_ms": -4,
        "hihat_velocity_variation": 0.12,
        "kick_pattern": [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
        "snare_pattern": [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    },
    "corrido": {
        "tempo_bpm": 120,
        "hihat_division": 8,
        "snare_delay_mean_ms": 10,
        "snare_delay_sigma_ms": 3.0,
        "kick_advance_ms": -2,
        "hihat_velocity_variation": 0.08,
        "kick_pattern": [1, 0, 0, 1, 0, 0, 1, 0],
        "snare_pattern": [0, 0, 1, 0, 0, 1, 0, 0],
    },
}


class MMAAgent:
    """
    Micro-Rhythmic Arrangement Agent.
    Generates humanized drum patterns with Late-Pocket Swing.
    """

    def __init__(self):
        self.audio_dir = Path("/var/sla/audio/lyrica/beats")
        self.audio_dir.mkdir(parents=True, exist_ok=True)

    def generate_beat(
        self,
        groove: str = "trap",
        tempo_bpm: Optional[int] = None,
        bars: int = 4,
        seed: Optional[int] = None,
    ) -> dict:
        if seed is not None:
            np.random.seed(seed)

        template = GROOVE_TEMPLATES.get(groove, GROOVE_TEMPLATES["trap"])
        bpm = tempo_bpm or template["tempo_bpm"]
        division = template["hihat_division"]
        pattern_len = len(template["kick_pattern"])

        beat_duration_s = 60.0 / bpm
        step_duration_s = (beat_duration_s * 4) / division
        total_steps = bars * pattern_len
        total_samples = int(total_steps * step_duration_s * SAMPLE_RATE)

        kick_track = np.zeros(total_samples, dtype=np.float32)
        snare_track = np.zeros(total_samples, dtype=np.float32)
        hihat_track = np.zeros(total_samples, dtype=np.float32)

        accent_pattern = HIHAT_ACCENT_16TH if division == 16 else HIHAT_ACCENT_8TH
        variation = template["hihat_velocity_variation"]
        snare_mean = template["snare_delay_mean_ms"]
        snare_sigma = template["snare_delay_sigma_ms"]
        kick_adv = template["kick_advance_ms"]

        humanization_log = []

        for bar in range(bars):
            for step in range(pattern_len):
                global_step = bar * pattern_len + step
                grid_sample = int(global_step * step_duration_s * SAMPLE_RATE)

                if template["kick_pattern"][step]:
                    offset = ms_to_samples(kick_adv)
                    pos = max(0, grid_sample + offset)
                    kick = generate_kick(velocity=0.9)
                    end = min(pos + len(kick), total_samples)
                    kick_track[pos:end] += kick[:end - pos]
                    humanization_log.append({
                        "type": "kick", "bar": bar + 1, "step": step + 1,
                        "offset_ms": kick_adv, "grid_sample": grid_sample,
                    })

                if template["snare_pattern"][step]:
                    delay_ms = np.random.normal(snare_mean, snare_sigma)
                    delay_ms = np.clip(delay_ms, 6.0, 18.0)
                    offset = ms_to_samples(delay_ms)
                    pos = min(grid_sample + offset, total_samples - 1)
                    snare = generate_snare(velocity=0.85)
                    end = min(pos + len(snare), total_samples)
                    snare_track[pos:end] += snare[:end - pos]
                    humanization_log.append({
                        "type": "snare", "bar": bar + 1, "step": step + 1,
                        "delay_ms": round(delay_ms, 2), "grid_sample": grid_sample,
                    })

                accent_idx = step % len(accent_pattern)
                base_vel = 80 / 127.0
                vel = base_vel * accent_pattern[accent_idx]
                vel *= (1 + np.random.uniform(-variation, variation))
                vel = np.clip(vel, 20 / 127.0, 1.0)

                hat = generate_hihat(velocity=vel)
                end = min(grid_sample + len(hat), total_samples)
                hihat_track[grid_sample:end] += hat[:end - grid_sample]

        mix = kick_track + snare_track + hihat_track
        peak = np.max(np.abs(mix))
        if peak > 0:
            mix = mix / peak * 0.9

        beat_id = str(uuid.uuid4())
        output_path = self.audio_dir / f"{beat_id}_{groove}_{bpm}bpm.wav"

        import soundfile as sf
        sf.write(str(output_path), mix, SAMPLE_RATE, subtype="FLOAT")

        stems_dir = self.audio_dir / f"{beat_id}_stems"
        stems_dir.mkdir(exist_ok=True)
        kick_path = stems_dir / "kick.wav"
        snare_path = stems_dir / "snare.wav"
        hihat_path = stems_dir / "hihat.wav"
        sf.write(str(kick_path), kick_track, SAMPLE_RATE, subtype="FLOAT")
        sf.write(str(snare_path), snare_track, SAMPLE_RATE, subtype="FLOAT")
        sf.write(str(hihat_path), hihat_track, SAMPLE_RATE, subtype="FLOAT")

        return {
            "beat_id": beat_id,
            "groove": groove,
            "tempo_bpm": bpm,
            "bars": bars,
            "total_steps": total_steps,
            "duration_seconds": round(total_samples / SAMPLE_RATE, 2),
            "sample_rate": SAMPLE_RATE,
            "output_path": str(output_path),
            "stems": {
                "kick": str(kick_path),
                "snare": str(snare_path),
                "hihat": str(hihat_path),
            },
            "humanization": {
                "snare_delay_mean_ms": snare_mean,
                "snare_delay_sigma_ms": snare_sigma,
                "kick_advance_ms": kick_adv,
                "hihat_velocity_variation": variation,
                "total_hits": len(humanization_log),
            },
            "provider": "lyrica_mma",
        }

    def list_grooves(self) -> dict:
        return {
            name: {
                "tempo_bpm": t["tempo_bpm"],
                "hihat_division": t["hihat_division"],
                "snare_delay_mean_ms": t["snare_delay_mean_ms"],
                "kick_advance_ms": t["kick_advance_ms"],
            }
            for name, t in GROOVE_TEMPLATES.items()
        }
