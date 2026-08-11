"""
LYRICA3 Rhythm Engine
Part of SLA-113 Toxic Drama Expansion

Components:
    - MMAGrooveAgent: Late-Pocket MIDI sequencing with human timing imperfections
"""

from .mma_groove_agent import MMAGrooveAgent, generate_late_pocket_groove

__all__ = [
    "MMAGrooveAgent",
    "generate_late_pocket_groove"
]
