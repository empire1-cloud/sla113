from __future__ import annotations

import importlib.util
import struct
import io
from pathlib import Path
from typing import Any, Dict

import numpy as np

from .node import NodeDef, ServiceDef


def load_procedural_instrumental(node: NodeDef, inputs: Dict[str, Any], service: ServiceDef, creator_id: str) -> Dict[str, Any]:
    """Handler for the procedural-instrumental service."""
    prompt = inputs.get("prompt", "Chicano soul instrumental")
    bpm = inputs.get("bpm", 92)
    key = inputs.get("key", "C")
    cultural_matrix = inputs.get("cultural_matrix", "LA SGV Chicano Heritage")
    duration_beats = inputs.get("duration_beats", 32)
    mood_recipe = inputs.get("mood_recipe", (0.78, 0.66, 0.82, 0.71))

    module_path = Path(service.config.get("path", ""))
    if not module_path.exists():
        raise FileNotFoundError(f"Procedural instrumental module not found at {module_path}")

    spec = importlib.util.spec_from_file_location("procedural_instrumental", module_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    mix = mod.generate_instrumental(
        bpm=bpm,
        key=key,
        cultural_matrix=cultural_matrix,
        mood_recipe=mood_recipe,
        duration_beats=duration_beats,
    )

    wav_bytes = mod.write_wav_bytes(mix)
    return {"audio": wav_bytes, "format": "wav", "sample_rate": 44100, "channels": 1, "bits": 16}


def load_soulfire_mastering(node: NodeDef, inputs: Dict[str, Any], service: ServiceDef, creator_id: str) -> Dict[str, Any]:
    """Handler for the soulfire-mastering service."""
    audio = inputs.get("audio")
    if audio is None:
        raise ValueError("No audio input provided for mastering")

    sample_rate = inputs.get("sample_rate", 44100)

    sig = np.frombuffer(audio, dtype=np.int16).astype(np.float32) / 32767.0
    sig = np.clip(sig * 0.95, -1.0, 1.0)
    sig = (sig * 32767).astype(np.int16)
    data = sig.tobytes()

    buf = io.BytesIO()
    buf.write(b"RIFF")
    buf.write(struct.pack("<I", 36 + len(data)))
    buf.write(b"WAVE")
    buf.write(b"fmt ")
    buf.write(struct.pack("<I", 16))
    buf.write(struct.pack("<HH", 1, 1))
    buf.write(struct.pack("<I", sample_rate))
    buf.write(struct.pack("<I", sample_rate * 2))
    buf.write(struct.pack("<HH", 2, 16))
    buf.write(b"data")
    buf.write(struct.pack("<I", len(data)))
    buf.write(data)
    buf.seek(0)

    return {"mastered": buf.getvalue(), "sample_rate": sample_rate, "format": "wav"}


def load_dna_watermark(node: NodeDef, inputs: Dict[str, Any], service: ServiceDef, creator_id: str) -> Dict[str, Any]:
    """Handler for the dna-watermark service. Embeds a simple metadata watermark."""
    audio = inputs.get("mastered") or inputs.get("signed_audio")
    if audio is None:
        raise ValueError("No audio provided for DNA signing")

    import hashlib
    import json

    dna_manifest = {
        "creator_id": creator_id,
        "version": "1.0",
        "fingerprint": hashlib.sha256(audio).hexdigest()[:16],
        "service": service.id,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }

    return {"signed_audio": audio, "dna_manifest": dna_manifest}


def load_render_engine(node: NodeDef, inputs: Dict[str, Any], service: ServiceDef, creator_id: str) -> Dict[str, Any]:
    """Handler for render services. Writes audio to a local output directory."""
    audio = inputs.get("signed_audio") or inputs.get("audio") or inputs.get("mastered")
    if audio is None:
        raise ValueError("No audio provided for rendering")

    tier = inputs.get("tier", "preview")
    sr = service.config.get("sample_rate", 44100)

    output_dir = Path(f"/tmp/sla113/renders/{creator_id}")
    output_dir.mkdir(parents=True, exist_ok=True)

    import hashlib
    import json
    import datetime

    tag = hashlib.sha256(audio).hexdigest()[:10]
    fname = f"render_{tier}_{tag}.wav"
    out_path = output_dir / fname
    out_path.write_bytes(audio)

    manifest = {
        "url": str(out_path),
        "tier": tier,
        "sample_rate": sr,
        "size_bytes": len(audio),
        "rendered_at": datetime.datetime.utcnow().isoformat(),
    }

    return {"rendered": audio, "url": str(out_path), "manifest": manifest}
