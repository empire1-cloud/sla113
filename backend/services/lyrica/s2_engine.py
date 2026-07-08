"""
Lyrica S2 Disruption Engine — Serendipity Synthesizer.

The mutation algorithm. Three core operations:

1. Groove Transplantation: Extracts the amplitude envelope (swing) from
   a source track via Hilbert transform and forces a rigid target to
   breathe with that groove.

2. Spectral Morph: Fuses the frequency content of two audio sources via
   STFT magnitude interpolation while preserving rhythmic phase.

3. Ghost Audio Artifact Engine: Ingests raw memory audio (VHS, voicemails,
   cassette recordings) and separates it via HPSS into:
   - Percussive transients → ghost drum kit
   - Harmonic content → ghost 808 sub-bass

All operations at 48kHz. Output stems are DNA-tagged.
"""

import uuid
import logging
from pathlib import Path
from typing import Optional

import numpy as np
import scipy.signal as signal

logger = logging.getLogger(__name__)

SAMPLE_RATE = 48000


class S2DisruptionEngine:
    """Serendipity Synthesizer — Latent Space Disruption Protocol."""

    def __init__(self):
        self.sr = SAMPLE_RATE
        self.audio_dir = Path("/var/sla/audio/lyrica/s2")
        self.audio_dir.mkdir(parents=True, exist_ok=True)

    def transplant_groove(
        self,
        source_path: str,
        target_path: str,
        smoothing_hz: float = 10.0,
    ) -> dict:
        """
        Extract the late-pocket swing (envelope) from an SGV beat (source)
        and force a rigid target (choir, piano, strings) to breathe with it.

        Uses Hilbert transform for analytic envelope extraction,
        Butterworth low-pass for rhythm pulse isolation.
        """
        import soundfile as sf

        source, sr_s = sf.read(source_path, dtype="float32")
        target, sr_t = sf.read(target_path, dtype="float32")

        if source.ndim > 1:
            source = source[:, 0]
        if target.ndim > 1:
            target = target[:, 0]

        min_len = min(len(source), len(target))
        source = source[:min_len]
        target = target[:min_len]

        analytic = signal.hilbert(source)
        amplitude_envelope = np.abs(analytic).astype(np.float32)

        nyq = self.sr / 2
        b, a = signal.butter(3, smoothing_hz / nyq, btype='low')
        smoothed = signal.filtfilt(b, a, amplitude_envelope).astype(np.float32)

        peak = np.max(smoothed)
        if peak > 0:
            normalized = smoothed / peak
        else:
            normalized = smoothed

        mutated = (target * normalized).astype(np.float32)

        s2_id = str(uuid.uuid4())
        output_path = self.audio_dir / f"{s2_id}_groove_transplant.wav"
        sf.write(str(output_path), mutated, self.sr, subtype="FLOAT")

        envelope_path = self.audio_dir / f"{s2_id}_envelope.wav"
        sf.write(str(envelope_path), normalized, self.sr, subtype="FLOAT")

        return {
            "s2_id": s2_id,
            "operation": "groove_transplantation",
            "source_path": source_path,
            "target_path": target_path,
            "output_path": str(output_path),
            "envelope_path": str(envelope_path),
            "smoothing_hz": smoothing_hz,
            "duration_seconds": round(min_len / self.sr, 2),
            "sample_rate": self.sr,
            "provider": "lyrica_s2",
        }

    def spectral_morph(
        self,
        audio_a_path: str,
        audio_b_path: str,
        morph_ratio: float = 0.5,
        nperseg: int = 2048,
    ) -> dict:
        """
        Fuse the frequency content of two audio sources.

        Interpolates STFT magnitudes while preserving the phase of audio_b
        (the rhythmic source) to keep the punch.

        morph_ratio: 0.0 = 100% audio_a, 1.0 = 100% audio_b
        """
        import soundfile as sf

        audio_a, sr_a = sf.read(audio_a_path, dtype="float32")
        audio_b, sr_b = sf.read(audio_b_path, dtype="float32")

        if audio_a.ndim > 1:
            audio_a = audio_a[:, 0]
        if audio_b.ndim > 1:
            audio_b = audio_b[:, 0]

        min_len = min(len(audio_a), len(audio_b))
        audio_a = audio_a[:min_len]
        audio_b = audio_b[:min_len]

        f, t, Zxx_A = signal.stft(audio_a, self.sr, nperseg=nperseg)
        f, t, Zxx_B = signal.stft(audio_b, self.sr, nperseg=nperseg)

        mag_A = np.abs(Zxx_A)
        mag_B = np.abs(Zxx_B)
        mutated_mag = mag_A * (1 - morph_ratio) + mag_B * morph_ratio

        phase_B = np.angle(Zxx_B)

        Zxx_mutated = mutated_mag * np.exp(1j * phase_B)
        _, mutated_audio = signal.istft(Zxx_mutated, self.sr)
        mutated_audio = mutated_audio.astype(np.float32)

        peak = np.max(np.abs(mutated_audio))
        if peak > 0.95:
            mutated_audio = mutated_audio * (0.95 / peak)

        s2_id = str(uuid.uuid4())
        output_path = self.audio_dir / f"{s2_id}_spectral_morph_{int(morph_ratio*100)}pct.wav"
        sf.write(str(output_path), mutated_audio, self.sr, subtype="FLOAT")

        return {
            "s2_id": s2_id,
            "operation": "spectral_morph",
            "audio_a_path": audio_a_path,
            "audio_b_path": audio_b_path,
            "morph_ratio": morph_ratio,
            "output_path": str(output_path),
            "duration_seconds": round(len(mutated_audio) / self.sr, 2),
            "sample_rate": self.sr,
            "provider": "lyrica_s2",
        }

    def ingest_ghost_audio(
        self,
        input_path: str,
        artifact_id: Optional[str] = None,
    ) -> dict:
        """
        Ghost Audio Artifact Engine.

        Ingests raw memory audio (VHS, voicemail, cassette) and separates into:
        - Percussive transients → ghost drum kit
        - Harmonic content → low-passed into ghost 808 sub-bass
        - Full harmonic layer for pad/texture use

        Uses librosa HPSS (Harmonic-Percussive Source Separation).
        """
        import soundfile as sf
        import librosa

        audio, sr = sf.read(input_path, dtype="float32")
        if audio.ndim > 1:
            audio = audio[:, 0]

        if sr != self.sr:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=self.sr)
            sr = self.sr

        harmonic, percussive = librosa.effects.hpss(audio, margin=(1.0, 5.0))

        envelope = np.abs(signal.hilbert(percussive))
        peaks, properties = signal.find_peaks(
            envelope, distance=sr // 4, height=np.max(envelope) * 0.3
        )

        b, a = signal.butter(4, 80 / (sr / 2), btype='low')
        ghost_sub = signal.filtfilt(b, a, harmonic).astype(np.float32) * 5.0
        peak_val = np.max(np.abs(ghost_sub))
        if peak_val > 0.95:
            ghost_sub = ghost_sub * (0.95 / peak_val)

        if not artifact_id:
            artifact_id = f"ghost_{uuid.uuid4().hex[:8]}"

        ghost_dir = self.audio_dir / artifact_id
        ghost_dir.mkdir(exist_ok=True)

        perc_path = ghost_dir / "ghost_drums.wav"
        harm_path = ghost_dir / "ghost_harmonic.wav"
        sub_path = ghost_dir / "ghost_808_sub.wav"
        sf.write(str(perc_path), percussive, sr, subtype="FLOAT")
        sf.write(str(harm_path), harmonic, sr, subtype="FLOAT")
        sf.write(str(sub_path), ghost_sub, sr, subtype="FLOAT")

        return {
            "artifact_id": artifact_id,
            "operation": "ghost_audio_ingest",
            "origin_type": "VHS_OR_VOICEMAIL",
            "input_path": input_path,
            "extracted_transients_count": len(peaks),
            "transient_positions_seconds": [round(p / sr, 3) for p in peaks[:20]],
            "stems": {
                "ghost_drums": str(perc_path),
                "ghost_harmonic": str(harm_path),
                "ghost_808_sub": str(sub_path),
            },
            "duration_seconds": round(len(audio) / sr, 2),
            "sample_rate": sr,
            "provider": "lyrica_s2",
        }
