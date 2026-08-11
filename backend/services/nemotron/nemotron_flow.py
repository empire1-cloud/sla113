"""
Nemotron Flow Engine — Central Orchestrator.

Ties together all three stages:
1. ProsodyEngine — Rhythmic Math (defines the pocket)
2. StemOrchestrator — Stem Orchestration (dispatches agents)
3. Combinator — Code-Driven Mixing (writes the mix)

Usable as a standalone service or as a sub-agent under Omni.
"""

import asyncio
import uuid
from typing import Dict, Any, Optional, List

from .prosody_engine import ProsodyEngine
from .stem_orchestrator import StemOrchestrator
from .combinator import Combinator


class NemotronFlowEngine:
    """Nemotron Flow Engine — the central Conductor Agent for human groove.

    Replaces monolithic audio generation with a modular three-stage pipeline:
    math -> orchestration -> mixing. Every stage produces auditable JSON.
    """

    def __init__(self):
        self._pipeline_id = None
        self._prosody_map = None
        self._orchestration = None
        self._combined = None

    @property
    def pipeline_id(self) -> Optional[str]:
        return self._pipeline_id

    def execute_sync(self, lyrics: List[str], bpm: int = 90,
                     swing: float = 0.15, style: str = "hip_hop",
                     voice_profile: str = "breathy_souldie_whisper",
                     vulnerability: float = 0.5,
                     groove: str = "late_pocket_dilla_swing",
                     texture: str = "warm_analog_room",
                     genre: str = "sgv_souldie_funk") -> Dict[str, Any]:
        """Execute the full Nemotron pipeline synchronously."""
        return asyncio.run(self.execute(
            lyrics, bpm, swing, style, voice_profile, vulnerability, groove, texture, genre
        ))

    async def execute(self, lyrics: List[str], bpm: int = 90,
                      swing: float = 0.15, style: str = "hip_hop",
                      voice_profile: str = "breathy_souldie_whisper",
                      vulnerability: float = 0.5,
                      groove: str = "late_pocket_dilla_swing",
                      texture: str = "warm_analog_room",
                      genre: str = "sgv_souldie_funk") -> Dict[str, Any]:
        """Execute the full Nemotron pipeline asynchronously.

        Stage 1: Prosody Map — rhythmic math
        Stage 2: Stem Orchestration — vocal + instrumental
        Stage 3: Combinator — mix + master
        """
        self._pipeline_id = f"nemotron_{uuid.uuid4().hex[:12]}"

        self._prosody_map = ProsodyEngine.generate_prosody(
            lyrics=lyrics, bpm=bpm, swing=swing, style=style
        )

        self._orchestration = await StemOrchestrator.orchestrate(
            prosody_map=self._prosody_map,
            voice_profile=voice_profile,
            vulnerability=vulnerability,
            groove=groove,
            texture=texture,
            genre=genre,
        )

        self._combined = Combinator.combine(
            orchestration=self._orchestration,
            output_path=f"/tmp/nemotron/{self._pipeline_id}_final.wav",
        )

        return self.summary()

    def adjust_tempo(self, new_bpm: int) -> Dict[str, Any]:
        """Adjust BPM without full re-generation."""
        if self._prosody_map:
            self._prosody_map = ProsodyEngine.adjust_tempo(self._prosody_map, new_bpm)

        if self._combined:
            self._combined = Combinator.adjust_tempo_and_rerender(self._combined, new_bpm)

        return self.summary()

    def summary(self) -> Dict[str, Any]:
        """Return the complete pipeline summary."""
        return {
            "pipeline_id": self._pipeline_id,
            "status": "complete" if self._combined else "partial",
            "stages": {
                "1_prosody_engine": {
                    "status": "complete" if self._prosody_map else "pending",
                    "stem_id": self._prosody_map.get("stem_id") if self._prosody_map else None,
                    "bpm": self._prosody_map.get("bpm") if self._prosody_map else None,
                    "events": len(self._prosody_map.get("timeline", [])) if self._prosody_map else 0,
                } if self._prosody_map else {"status": "pending"},
                "2_stem_orchestration": {
                    "status": "complete" if self._orchestration else "pending",
                    "orchestration_id": self._orchestration.get("orchestration_id") if self._orchestration else None,
                    "stems_generated": self._orchestration.get("stem_count", 0) if self._orchestration else 0,
                } if self._orchestration else {"status": "pending"},
                "3_combinator": {
                    "status": "complete" if self._combined else "pending",
                    "combinator_id": self._combined.get("combinator_id") if self._combined else None,
                    "output_path": self._combined.get("output_path") if self._combined else None,
                } if self._combined else {"status": "pending"},
            },
            "pipeline": self._combined or self._orchestration or self._prosody_map or {},
        }

    def get_prosody_map(self) -> Optional[Dict[str, Any]]:
        return self._prosody_map

    def get_orchestration(self) -> Optional[Dict[str, Any]]:
        return self._orchestration

    def get_combined(self) -> Optional[Dict[str, Any]]:
        return self._combined
