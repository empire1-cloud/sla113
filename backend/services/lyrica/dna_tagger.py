"""
Lyrica DNA Tagger — Immutable Audio Provenance.

Every generated stem receives:
  - DNA Tag: SHA-256 hash of raw PCM audio bytes (first 16 hex chars)
  - Full Hash: Complete SHA-256 hex digest
  - Metadata: sample rate, duration, creation timestamp, contributor info

The Soulfire Synapse Payload assembles all agent outputs into a single
operational JSON document for downstream systems.
"""

import hashlib
import json
import uuid
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)


def compute_audio_dna(file_path: str) -> dict:
    """Compute SHA-256 DNA tag from audio file."""
    import soundfile as sf

    audio, sr = sf.read(file_path, dtype="float32")
    pcm_bytes = audio.tobytes()

    full_hash = hashlib.sha256(pcm_bytes).hexdigest()
    dna_tag = full_hash[:16]

    duration_s = len(audio) / sr if audio.ndim == 1 else len(audio) / sr

    return {
        "dna_tag": dna_tag,
        "full_hash": full_hash,
        "file_path": file_path,
        "sample_rate": sr,
        "channels": 1 if audio.ndim == 1 else audio.shape[1],
        "samples": len(audio),
        "duration_ms": round(duration_s * 1000, 1),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def tag_audio_file(file_path: str, contributor_id: Optional[str] = None) -> dict:
    """Tag an audio file with DNA provenance metadata."""
    dna = compute_audio_dna(file_path)

    if contributor_id:
        dna["contributor_id"] = contributor_id

    meta_path = Path(file_path).with_suffix(".dna.json")
    meta_path.write_text(json.dumps(dna, indent=2))
    dna["meta_path"] = str(meta_path)

    return dna


class SoulfireSynapsePayload:
    """
    Assembles all Lyrica agent outputs into a single operational payload.

    Structure:
    {
      "payload_id": "...",
      "track": { metadata },
      "lyrics": { ghostwriter output },
      "audio_blueprint": { beat + vocal + fx chain },
      "stems": { paths to all stems },
      "dna_tags": { provenance for each stem },
      "created_at": ISO8601
    }
    """

    def __init__(self):
        self.payload_dir = Path("/var/sla/audio/lyrica/payloads")
        self.payload_dir.mkdir(parents=True, exist_ok=True)

    def assemble(
        self,
        track_title: str,
        ghostwriter_output: Optional[dict] = None,
        mma_output: Optional[dict] = None,
        pfa_output: Optional[dict] = None,
        pda_output: Optional[dict] = None,
        voxcpm_output: Optional[dict] = None,
        fx_output: Optional[dict] = None,
        contributor_id: Optional[str] = None,
        genre: Optional[str] = None,
        mood: Optional[str] = None,
    ) -> dict:
        payload_id = str(uuid.uuid4())

        stems = {}
        dna_tags = {}

        if mma_output and "stems" in mma_output:
            for stem_name, stem_path in mma_output["stems"].items():
                stems[f"beat_{stem_name}"] = stem_path
                try:
                    dna_tags[f"beat_{stem_name}"] = compute_audio_dna(stem_path)
                except Exception:
                    pass

        if mma_output and "output_path" in mma_output:
            stems["beat_mix"] = mma_output["output_path"]
            try:
                dna_tags["beat_mix"] = compute_audio_dna(mma_output["output_path"])
            except Exception:
                pass

        if voxcpm_output and "path" in voxcpm_output:
            stems["vocal_raw"] = voxcpm_output["path"]
            try:
                dna_tags["vocal_raw"] = compute_audio_dna(voxcpm_output["path"])
            except Exception:
                pass

        if pfa_output and "output_path" in pfa_output:
            stems["vocal_pfa"] = pfa_output["output_path"]
            try:
                dna_tags["vocal_pfa"] = compute_audio_dna(pfa_output["output_path"])
            except Exception:
                pass

        if pda_output and "output_path" in pda_output:
            stems["vocal_pda"] = pda_output["output_path"]
            try:
                dna_tags["vocal_pda"] = compute_audio_dna(pda_output["output_path"])
            except Exception:
                pass

        if fx_output and "output_path" in fx_output:
            stems["vocal_fx"] = fx_output["output_path"]
            try:
                dna_tags["vocal_fx"] = compute_audio_dna(fx_output["output_path"])
            except Exception:
                pass

        payload = {
            "payload_id": payload_id,
            "payload_type": "soulfire_synapse",
            "version": "1.0",
            "track": {
                "title": track_title,
                "genre": genre,
                "mood": mood,
                "contributor_id": contributor_id,
                "tempo_bpm": (mma_output or {}).get("tempo_bpm"),
                "duration_seconds": (mma_output or {}).get("duration_seconds"),
                "sample_rate": 48000,
            },
            "lyrics": {
                "raw_lml": (ghostwriter_output or {}).get("parsed", {}).get("raw_lml"),
                "sections": (ghostwriter_output or {}).get("parsed", {}).get("sections", []),
                "emotion_cues": (ghostwriter_output or {}).get("parsed", {}).get("emotion_cues", []),
                "flow_style": (ghostwriter_output or {}).get("parsed", {}).get("metadata", {}).get("flow_style"),
            } if ghostwriter_output else None,
            "audio_blueprint": {
                "beat": {
                    "groove": (mma_output or {}).get("groove"),
                    "humanization": (mma_output or {}).get("humanization"),
                } if mma_output else None,
                "vocal": {
                    "voice_id": (voxcpm_output or {}).get("voice_id"),
                    "model": (voxcpm_output or {}).get("model"),
                    "pfa_applied": bool(pfa_output),
                    "pda_texture": (pda_output or {}).get("texture"),
                    "fx_preset": (fx_output or {}).get("preset"),
                } if voxcpm_output else None,
            },
            "stems": stems,
            "dna_tags": dna_tags,
            "stem_count": len(stems),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        payload_path = self.payload_dir / f"{payload_id}_synapse.json"
        payload_path.write_text(json.dumps(payload, indent=2, default=str))
        payload["payload_path"] = str(payload_path)

        return payload
