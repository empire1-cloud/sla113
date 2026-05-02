"""
Lyrica PFA Agent — Biometric Vocal Phonation Control.

Applies human-like vocal characteristics to synthesized speech:
  - Vocal Fry: Transient low-frequency pitch modulation (40-80Hz subglottal)
  - Adaptive Inhale (IRSA): Inserts natural breath sounds at phrase boundaries
  - Silence/phrase detection for breath insertion points

Works on raw audio arrays (numpy) at 48kHz.
"""

import uuid
import logging
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

SAMPLE_RATE = 48000


def detect_silence_gaps(audio: np.ndarray, sample_rate: int = SAMPLE_RATE) -> list:
    """Detect silence gaps suitable for breath insertion."""
    window_size = int(0.020 * sample_rate)
    hop_size = int(0.010 * sample_rate)
    min_gap_samples = int(0.300 * sample_rate)
    max_gap_samples = int(2.000 * sample_rate)

    peak = np.max(np.abs(audio))
    if peak == 0:
        return []
    threshold = peak * 10 ** (-40 / 20)

    n_windows = (len(audio) - window_size) // hop_size + 1
    is_silent = np.zeros(n_windows, dtype=bool)
    for i in range(n_windows):
        start = i * hop_size
        window = audio[start:start + window_size]
        rms = np.sqrt(np.mean(window ** 2))
        is_silent[i] = rms < threshold

    gaps = []
    gap_start = None
    for i, silent in enumerate(is_silent):
        if silent and gap_start is None:
            gap_start = i
        elif not silent and gap_start is not None:
            gap_len_samples = (i - gap_start) * hop_size
            if min_gap_samples <= gap_len_samples <= max_gap_samples:
                center_sample = (gap_start * hop_size + i * hop_size) // 2
                gaps.append({
                    "center_sample": center_sample,
                    "duration_ms": round(gap_len_samples / sample_rate * 1000, 1),
                })
            gap_start = None

    return gaps


def generate_breath(duration_ms: float = 400, volume_db: float = -15) -> np.ndarray:
    """Generate a synthetic breath/inhale sound using pink noise."""
    n_samples = int(duration_ms * SAMPLE_RATE / 1000)
    white = np.random.randn(n_samples).astype(np.float32)

    b = [0.049922035, -0.095993537, 0.050612699, -0.004709510]
    a = [1.0, -2.494956002, 2.017265875, -0.522189400]
    from scipy.signal import lfilter
    pink = lfilter(b, a, white).astype(np.float32)

    t = np.linspace(0, 1, n_samples)
    envelope = np.sin(np.pi * t) ** 0.7
    rise_end = int(n_samples * 0.3)
    envelope[:rise_end] *= np.linspace(0, 1, rise_end) ** 2

    volume_linear = 10 ** (volume_db / 20)
    breath = volume_linear * envelope * pink

    return breath.astype(np.float32)


def apply_vocal_fry(
    audio: np.ndarray,
    fry_rate: float = 60.0,
    depth: float = 0.05,
    onset_ms: float = 50.0,
) -> np.ndarray:
    """Apply vocal fry (low-frequency pitch modulation) to audio."""
    n = len(audio)
    t = np.arange(n, dtype=np.float32) / SAMPLE_RATE

    modulation = depth * np.sin(2 * np.pi * fry_rate * t)

    onset_samples = int(onset_ms * SAMPLE_RATE / 1000)
    if onset_samples > 0 and onset_samples < n:
        onset_curve = np.ones(n, dtype=np.float32)
        onset_curve[:onset_samples] = (np.linspace(0, 1, onset_samples) ** 2).astype(np.float32)
        modulation *= onset_curve

    output = audio * (1.0 + modulation)
    return output.astype(np.float32)


def insert_breaths(audio: np.ndarray, gaps: list, breath_params: Optional[dict] = None) -> np.ndarray:
    """Insert breath sounds at detected silence gaps."""
    params = breath_params or {}
    duration_ms = params.get("duration_ms", 400)
    volume_db = params.get("volume_db", -15)

    output = audio.copy()

    for gap in gaps:
        breath = generate_breath(duration_ms=duration_ms, volume_db=volume_db)
        center = gap["center_sample"]
        start = max(0, center - len(breath) // 2)
        end = min(len(output), start + len(breath))
        actual_len = end - start
        if actual_len > 0:
            output[start:end] += breath[:actual_len]

    return output


class PFAAgent:
    """
    Phonation Agent — vocal fry + adaptive breath insertion.
    Processes audio files to add human-like vocal characteristics.
    """

    def __init__(self):
        self.audio_dir = Path("/var/sla/audio/lyrica/pfa")
        self.audio_dir.mkdir(parents=True, exist_ok=True)

    def process(
        self,
        input_path: str,
        apply_fry: bool = True,
        apply_breaths: bool = True,
        fry_rate: float = 60.0,
        fry_depth: float = 0.05,
        breath_duration_ms: float = 400,
        breath_volume_db: float = -15,
    ) -> dict:
        import soundfile as sf

        audio, sr = sf.read(input_path, dtype="float32")
        if audio.ndim > 1:
            audio = audio[:, 0]

        gaps = []
        if apply_breaths:
            gaps = detect_silence_gaps(audio, sr)
            audio = insert_breaths(audio, gaps, {
                "duration_ms": breath_duration_ms,
                "volume_db": breath_volume_db,
            })

        if apply_fry:
            audio = apply_vocal_fry(audio, fry_rate=fry_rate, depth=fry_depth)

        pfa_id = str(uuid.uuid4())
        output_path = self.audio_dir / f"{pfa_id}_pfa.wav"
        sf.write(str(output_path), audio, sr, subtype="FLOAT")

        return {
            "pfa_id": pfa_id,
            "input_path": input_path,
            "output_path": str(output_path),
            "sample_rate": sr,
            "applied": {
                "vocal_fry": apply_fry,
                "adaptive_breaths": apply_breaths,
            },
            "fry_params": {
                "rate_hz": fry_rate,
                "depth": fry_depth,
            } if apply_fry else None,
            "breath_params": {
                "duration_ms": breath_duration_ms,
                "volume_db": breath_volume_db,
                "gaps_detected": len(gaps),
            } if apply_breaths else None,
            "provider": "lyrica_pfa",
        }
