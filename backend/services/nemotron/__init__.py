"""
Nemotron Flow Engine — Timing, Prosody, Orchestration, and Combinator.

Three-stage pipeline for human groove:
1. Prosody Map — rhythmic math (defines the pocket)
2. Stem Orchestration — vocal + instrumental dispatch
3. Combinator — code-driven mixing (eliminates AI sound)

Sub-engines:
- timing_engine — grid alignment, transient detection, late-pocket calculation
- prosody_engine — lyric-to-prosody mapping with syllable stress
- stem_orchestrator — concurrent vocal and instrumental agent dispatch
- combinator — mastering chain, WAV export, tempo adjustment
- nemotron_flow — top-level orchestrator tying all stages together

Usage:
    from services.nemotron import NemotronFlowEngine
    engine = NemotronFlowEngine()
    result = engine.execute_sync(["City breathin' heavy"], bpm=90)
"""

from .nemotron_flow import NemotronFlowEngine
from .prosody_engine import ProsodyEngine, ProsodyMap
from .timing_engine import TimingEngine, BeatGrid
from .stem_orchestrator import StemOrchestrator, VocalAgent, InstrumentalAgent
from .combinator import Combinator, MasteringChain

__all__ = [
    "NemotronFlowEngine",
    "ProsodyEngine",
    "ProsodyMap",
    "TimingEngine",
    "BeatGrid",
    "StemOrchestrator",
    "VocalAgent",
    "InstrumentalAgent",
    "Combinator",
    "MasteringChain",
]
