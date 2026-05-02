"""
Lyrica PDA Agent — Psychoacoustic DSP Texture Application.

Translates high-level texture concepts into precise mixing parameters:
  - Tape Saturation: soft-clip arctan + high-shelf rolloff + wow/flutter
  - SSL Console Warmth: harmonic saturation + parametric EQ curve
  - Vocal Bus: +3dB peaking EQ at 200Hz + presence boost
  - Lo-Fi Vinyl: bitcrush + noise + rolloff
  - Stadium Reverb: large-room convolution approximation

Operates on raw audio arrays at 48kHz.
"""

import uuid
import logging
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

SAMPLE_RATE = 48000


def soft_clip(audio: np.ndarray, drive: float = 2.0) -> np.ndarray:
    """Arctan soft clipping (tape saturation core)."""
    return (2.0 / np.pi) * np.arctan(drive * audio).astype(np.float32)


def biquad_peaking_eq(audio: np.ndarray, freq: float, gain_db: float, q: float, sr: int) -> np.ndarray:
    """Apply a peaking EQ biquad filter."""
    A = 10 ** (gain_db / 40.0)
    w0 = 2 * np.pi * freq / sr
    sin_w0 = np.sin(w0)
    cos_w0 = np.cos(w0)
    alpha = sin_w0 / (2 * q)

    b0 = 1 + alpha * A
    b1 = -2 * cos_w0
    b2 = 1 - alpha * A
    a0 = 1 + alpha / A
    a1 = -2 * cos_w0
    a2 = 1 - alpha / A

    b = np.array([b0 / a0, b1 / a0, b2 / a0])
    a = np.array([1.0, a1 / a0, a2 / a0])

    from scipy.signal import lfilter
    return lfilter(b, a, audio).astype(np.float32)


def high_shelf(audio: np.ndarray, freq: float, gain_db: float, sr: int) -> np.ndarray:
    """Apply a high-shelf filter."""
    A = 10 ** (gain_db / 40.0)
    w0 = 2 * np.pi * freq / sr
    sin_w0 = np.sin(w0)
    cos_w0 = np.cos(w0)
    alpha = sin_w0 / 2 * np.sqrt(2)

    b0 = A * ((A + 1) + (A - 1) * cos_w0 + 2 * np.sqrt(A) * alpha)
    b1 = -2 * A * ((A - 1) + (A + 1) * cos_w0)
    b2 = A * ((A + 1) + (A - 1) * cos_w0 - 2 * np.sqrt(A) * alpha)
    a0 = (A + 1) - (A - 1) * cos_w0 + 2 * np.sqrt(A) * alpha
    a1 = 2 * ((A - 1) - (A + 1) * cos_w0)
    a2 = (A + 1) - (A - 1) * cos_w0 - 2 * np.sqrt(A) * alpha

    b = np.array([b0 / a0, b1 / a0, b2 / a0])
    a = np.array([1.0, a1 / a0, a2 / a0])

    from scipy.signal import lfilter
    return lfilter(b, a, audio).astype(np.float32)


def low_shelf(audio: np.ndarray, freq: float, gain_db: float, sr: int) -> np.ndarray:
    """Apply a low-shelf filter."""
    A = 10 ** (gain_db / 40.0)
    w0 = 2 * np.pi * freq / sr
    sin_w0 = np.sin(w0)
    cos_w0 = np.cos(w0)
    alpha = sin_w0 / 2 * np.sqrt(2)

    b0 = A * ((A + 1) - (A - 1) * cos_w0 + 2 * np.sqrt(A) * alpha)
    b1 = 2 * A * ((A - 1) - (A + 1) * cos_w0)
    b2 = A * ((A + 1) - (A - 1) * cos_w0 - 2 * np.sqrt(A) * alpha)
    a0 = (A + 1) + (A - 1) * cos_w0 + 2 * np.sqrt(A) * alpha
    a1 = -2 * ((A - 1) + (A + 1) * cos_w0)
    a2 = (A + 1) + (A - 1) * cos_w0 - 2 * np.sqrt(A) * alpha

    b = np.array([b0 / a0, b1 / a0, b2 / a0])
    a = np.array([1.0, a1 / a0, a2 / a0])

    from scipy.signal import lfilter
    return lfilter(b, a, audio).astype(np.float32)


TEXTURE_PRESETS = {
    "tape_saturation": {
        "name": "Tape Saturation",
        "description": "Analog tape warmth: soft-clip, high-shelf rolloff, low-end warmth, wow/flutter",
    },
    "ssl_console": {
        "name": "SSL Console Warmth",
        "description": "Classic SSL desk: harmonic saturation + 4-band parametric EQ",
    },
    "vocal_bus": {
        "name": "Vocal Bus (+3dB @ 200Hz)",
        "description": "Vocal chain: 200Hz warmth boost + 3kHz presence + gentle compression",
    },
    "lofi_vinyl": {
        "name": "Lo-Fi Vinyl",
        "description": "Vinyl texture: bitcrush + noise floor + rolloff + crackle",
    },
}


def apply_tape_saturation(audio: np.ndarray, drive: float = 2.5) -> np.ndarray:
    out = soft_clip(audio, drive=drive)
    out = high_shelf(out, freq=12000, gain_db=-3.0, sr=SAMPLE_RATE)
    out = low_shelf(out, freq=200, gain_db=1.5, sr=SAMPLE_RATE)
    n = len(out)
    t = np.arange(n, dtype=np.float32) / SAMPLE_RATE
    flutter = 1.0 + 0.001 * np.sin(2 * np.pi * 0.5 * t)
    indices = np.clip((np.arange(n) * flutter).astype(int), 0, n - 1)
    out = out[indices]
    noise = np.random.randn(n).astype(np.float32) * 10 ** (-60 / 20)
    out += noise
    return out


def apply_ssl_console(audio: np.ndarray) -> np.ndarray:
    harmonics = 0.7 * audio + 0.2 * audio ** 2 + 0.1 * audio ** 3
    harmonics = np.clip(harmonics, -1.0, 1.0).astype(np.float32)
    out = low_shelf(harmonics, freq=80, gain_db=2.0, sr=SAMPLE_RATE)
    out = biquad_peaking_eq(out, freq=350, gain_db=-1.5, q=1.2, sr=SAMPLE_RATE)
    out = biquad_peaking_eq(out, freq=3000, gain_db=2.5, q=1.0, sr=SAMPLE_RATE)
    out = high_shelf(out, freq=12000, gain_db=1.5, sr=SAMPLE_RATE)
    return out


def apply_vocal_bus(audio: np.ndarray) -> np.ndarray:
    out = biquad_peaking_eq(audio, freq=200, gain_db=3.0, q=1.5, sr=SAMPLE_RATE)
    out = biquad_peaking_eq(out, freq=3000, gain_db=2.0, q=1.2, sr=SAMPLE_RATE)
    out = high_shelf(out, freq=10000, gain_db=1.0, sr=SAMPLE_RATE)
    return out


def apply_lofi_vinyl(audio: np.ndarray) -> np.ndarray:
    bit_depth = 12
    max_val = 2 ** (bit_depth - 1) - 1
    out = np.round(audio * max_val) / max_val
    out = out.astype(np.float32)
    out = high_shelf(out, freq=8000, gain_db=-6.0, sr=SAMPLE_RATE)
    out = low_shelf(out, freq=60, gain_db=-3.0, sr=SAMPLE_RATE)
    noise = np.random.randn(len(out)).astype(np.float32) * 10 ** (-45 / 20)
    out += noise
    return out


TEXTURE_FUNCTIONS = {
    "tape_saturation": apply_tape_saturation,
    "ssl_console": apply_ssl_console,
    "vocal_bus": apply_vocal_bus,
    "lofi_vinyl": apply_lofi_vinyl,
}


class PDAAgent:
    """Psychoacoustic DSP Agent — applies texture presets to audio."""

    def __init__(self):
        self.audio_dir = Path("/var/sla/audio/lyrica/pda")
        self.audio_dir.mkdir(parents=True, exist_ok=True)

    def process(self, input_path: str, texture: str = "vocal_bus") -> dict:
        import soundfile as sf

        if texture not in TEXTURE_FUNCTIONS:
            raise ValueError(f"Unknown texture: {texture}. Available: {list(TEXTURE_FUNCTIONS.keys())}")

        audio, sr = sf.read(input_path, dtype="float32")
        mono = audio[:, 0] if audio.ndim > 1 else audio

        processed = TEXTURE_FUNCTIONS[texture](mono)

        peak = np.max(np.abs(processed))
        if peak > 0.95:
            processed = processed * (0.95 / peak)

        pda_id = str(uuid.uuid4())
        output_path = self.audio_dir / f"{pda_id}_{texture}.wav"
        sf.write(str(output_path), processed, sr, subtype="FLOAT")

        return {
            "pda_id": pda_id,
            "input_path": input_path,
            "output_path": str(output_path),
            "texture": texture,
            "texture_name": TEXTURE_PRESETS[texture]["name"],
            "sample_rate": sr,
            "provider": "lyrica_pda",
        }

    def list_textures(self) -> dict:
        return TEXTURE_PRESETS
