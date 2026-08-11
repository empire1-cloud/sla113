"""
CCNA — Cultural Contextualizer & Narrative Architect.

The cultural semiotics mapping layer of the Soulfire ecosystem.
Provides cultural marker extraction, ethical gradient scoring,
narrative archetype suggestion, and genre-to-culture mapping.

Usage:
    from services.cultural import CCNAEngine
    result = CCNAEngine.analyze("text with cultural markers")
"""

from .ccna_engine import CCNAEngine, CulturalMarker, EthicalScore

__all__ = ["CCNAEngine", "CulturalMarker", "EthicalScore"]
