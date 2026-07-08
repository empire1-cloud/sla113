"""
LYRICA3 Intent Engine
Part of SLA-113 Toxic Drama Expansion

Components:
    - PromptChainOrchestrator: 5-stage prompt chain (AURA → ASE → EFL → ECHO → EFAD)
    - AdvancedAURAEngine: Local NLP-based intent extraction
    - ASEEngine: Novelty/cohesion evaluation
    - EFLEngine: Template-based lyric generation
    - AURAState, ASEState, EFLState, ECHOState: Intermediate state classes
    - SoulfirePayload: Final payload output
"""

from .prompt_chain_orchestrator import (
    PromptChainOrchestrator,
    AURAState,
    ASEState,
    EFLState,
    ECHOState,
    SoulfirePayload,
    generate_soulfire_payload
)

from .advanced_aura_engine import (
    AdvancedAURAEngine,
    analyze_user_input
)

from .ase_efl_engines import (
    ASEEngine,
    EFLEngine
)

__all__ = [
    "PromptChainOrchestrator",
    "AdvancedAURAEngine",
    "ASEEngine",
    "EFLEngine",
    "AURAState",
    "ASEState",
    "EFLState",
    "ECHOState",
    "SoulfirePayload",
    "generate_soulfire_payload",
    "analyze_user_input"
]
