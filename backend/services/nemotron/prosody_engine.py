"""
Nemotron Prosody Engine — Stage 1: Rhythmic Math Engine.
Maps lyrics to a rigid BPM grid with syllable stress, swing, and breath markers.
Outputs a Prosody Map JSON consumed by the stem orchestrator and combinator.
"""

import math
import json
import uuid
from typing import List, Dict, Any, Optional


class ProsodyMap:
    def __init__(self, stem_id: str, bpm: int, groove_swing: float = 0.0):
        self.stem_id = stem_id
        self.bpm = bpm
        self.groove_swing = groove_swing
        self.ms_per_beat = 60000.0 / bpm
        self.ms_per_16th = self.ms_per_beat / 4.0
        self.timeline: List[Dict[str, Any]] = []

    def add_action(self, time_ms: float, action: str):
        self.timeline.append({"time_ms": round(time_ms, 2), "action": action})

    def add_syllable(self, time_ms: float, text: str, stress: str = "medium",
                     pitch: str = "neutral", effect: Optional[str] = None):
        entry = {"time_ms": round(time_ms, 2), "text": text, "stress": stress, "pitch": pitch}
        if effect:
            entry["effect"] = effect
        self.timeline.append(entry)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stem_id": self.stem_id,
            "bpm": self.bpm,
            "groove_swing": self.groove_swing,
            "ms_per_beat": self.ms_per_beat,
            "ms_per_16th": self.ms_per_16th,
            "timeline": self.timeline,
        }


class ProsodyEngine:
    """Converts lyric lines into a timed ProsodyMap with stress, swing, and breath.

    This is Nemotron's brain — it mathematically defines the pocket before any
    audio is generated, replacing guesswork with deterministic rhythm.
    """

    STRESS_MAP = {"heavy": ["heavy", "loud", "sharp", "drop", "hit", "now", "never", "forever"],
                  "light": ["light", "soft", "breath", "whisper", "calm", "maybe"]}

    PITCH_MAP = {"low": ["low", "deep", "dark", "below"],
                 "falling": ["falling", "down", "drop", "crash"],
                 "rising": ["rising", "up", "climb", "lift"]}

    @classmethod
    def _classify_stress(cls, word: str) -> str:
        clean = word.strip(".,!?;:'\"()[]<>").lower()
        for stress, words in cls.STRESS_MAP.items():
            if clean in words:
                return stress
        return "medium"

    @classmethod
    def _classify_pitch(cls, word: str, stress: str) -> str:
        clean = word.strip(".,!?;:'\"()[]<>").lower()
        for pitch, words in cls.PITCH_MAP.items():
            if clean in words:
                return pitch
        if stress == "heavy":
            return "low"
        if stress == "light":
            return "rising"
        return "neutral"

    @classmethod
    def _detect_action(cls, word: str) -> Optional[str]:
        clean = word.strip(".,!?;:'\"()[]<>").lower()
        actions = {"inhale": "<inhale_sharp>", "<inhale_sharp>": "<inhale_sharp>",
                   "breath": "<micro_pause>", "<micro_pause>": "<micro_pause>",
                   "crack": "<emotional_crack>", "fry": "<vocal_fry>"}
        return actions.get(clean)

    @classmethod
    def generate_prosody(cls, lyrics: List[str], bpm: int = 90,
                         swing: float = 0.15, style: str = "hip_hop") -> Dict[str, Any]:
        """Take lyric lines and generate a full Prosody Map."""
        map_id = f"prosody_{uuid.uuid4().hex[:8]}"
        pm = ProsodyMap(map_id, bpm, swing)

        ms_per_beat = pm.ms_per_beat
        ms_per_16th = pm.ms_per_16th
        swing_offset = ms_per_16th * swing

        current_time = 0.0

        for line_idx, line in enumerate(lyrics):
            if line_idx > 0:
                current_time += ms_per_beat * 0.5
                pm.add_action(current_time, "<micro_pause>")
                current_time += ms_per_beat * 0.25

            words = line.split()
            beat_counter = 0

            is_first = True
            for word in words:
                action = cls._detect_action(word)
                if action:
                    if is_first:
                        current_time += ms_per_16th
                        is_first = False
                    pm.add_action(current_time, action)
                    current_time += ms_per_16th * 0.5
                    continue

                stress = cls._classify_stress(word)
                pitch = cls._classify_pitch(word, stress)

                beat_position = beat_counter % 4
                if beat_position == 2 and stress == "heavy":
                    current_time += swing_offset

                syllable_time = current_time
                effect = None
                if stress == "heavy" and word.endswith("in'"):
                    effect = "vocal_fry"

                pm.add_syllable(
                    time_ms=syllable_time,
                    text=word.strip(".,!?;:'\"()[]<>"),
                    stress=stress,
                    pitch=pitch,
                    effect=effect,
                )

                duration = ms_per_16th * (2 if stress == "heavy" else 1)
                current_time += duration
                beat_counter += 1
                is_first = False

            current_time += ms_per_beat * 0.5

        return pm.to_dict()

    @classmethod
    def adjust_tempo(cls, prosody_map: Dict[str, Any], new_bpm: int) -> Dict[str, Any]:
        """Rescale a prosody map to a new BPM — no re-generation needed."""
        old_bpm = prosody_map["bpm"]
        if old_bpm == new_bpm:
            return prosody_map

        ratio = old_bpm / new_bpm
        new_map = dict(prosody_map)
        new_map["bpm"] = new_bpm
        new_map["ms_per_beat"] = 60000.0 / new_bpm
        new_map["ms_per_16th"] = new_map["ms_per_beat"] / 4.0

        new_timeline = []
        for entry in prosody_map["timeline"]:
            new_entry = dict(entry)
            new_entry["time_ms"] = round(entry["time_ms"] * ratio, 2)
            new_timeline.append(new_entry)
        new_map["timeline"] = new_timeline

        return new_map
