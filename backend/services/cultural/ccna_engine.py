"""
CCNA — Cultural Contextualizer & Narrative Architect.

The cultural semiotics mapping layer of the Soulfire ecosystem.
Transforms generic text generation into profound cultural anthropology.

Capabilities:
- Cultural marker extraction (slang, geography, references)
- Ethical gradient scoring (0-1 alignment)
- Narrative archetype suggestion
- Genre-to-culture mapping
- Dynamic knowledge graph (CCAKB / FCCAN)
"""

import json
import uuid
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict


# --- Knowledge Bases ---

SGV_CULTURAL_MARKERS = {
    "geography": ["san gabriel valley", "el monte", "baldwin park", "west covina",
                  "azusa", "covina", "la puente", "hacienda heights", "rowland heights",
                  "whittier", "pico riviera", "montebello", "east la", "pomona"],
    "slang": ["orale", "simon", "que onda", "barrio", "carnal", "carnala",
              "vato", "vata", "cholo", "cholita", "ese", "esita", "rifa",
              "cantón", "jefita", "jefito", "mija", "mijo", "apá", "amá"],
    "cultural_touchstones": ["lowrider", "art laboe", "oldies", "souldies",
                             "cruising", "whittier blvd", "taco truck", "panaderia",
                             "quinceañera", "dia de muertos", "la virgen",
                             "chicano", "chicana", "rasquache", "rasquacha"],
    "values": ["familia", "respeto", "orgullo", "hermandad", "barrio unity",
               "first gen", "immigrant story", "hard work", "faith", "resilience"],
    "dialect_markers": ["spanglish", "caló", "code switching", "poch@",
                        "accented english", "vowel shifting"],
    "sonic_references": ["lowrider oldies", "sgv funk", "chicano soul",
                         "corrido", "norteno", "banda", "cumbia", "ranchera",
                         "souldies", "g funk", "west coast", "latin trap"],
}

CHICANO_IDENTITY_MARKERS = {
    "aesthetics": ["lowrider", "chicano script", "pachuco", "zoot suit",
                   "bandana", "flannel", "ben davis", "khakis", "cortes"],
    "music": ["art laboe dedications", "lowrider oldies", "chicano rap",
              "sgv soul", "east side story", "brown-eyed soul"],
    "experience": ["first generation", "borderland identity", "ni de aqui ni de alla",
                   "spanglish fluency", "cultural code-switching"],
    "resilience_indicators": ["barrio pride", "community over competition",
                              "creative survival", "making something from nothing"],
}

GENRE_TO_CULTURE_MAP = {
    "sgv_souldie_funk": {
        "culture": "chicano",
        "region": "san gabriel valley",
        "vibe": "late night cruising, art laboe dedications, lowrider slow-jam",
        "typical_bpm": (75, 95),
        "emotional_palette": "bright chords with bruised subtext",
    },
    "corrido": {
        "culture": "mexican/northern mexican",
        "region": "northern mexico / southwest us",
        "vibe": "narrative storytelling, accordion-driven, drug war or love ballads",
        "typical_bpm": (110, 130),
        "emotional_palette": "gritty realism, pride, tragedy",
    },
    "chicano_rap": {
        "culture": "chicano",
        "region": "southwest us / california",
        "vibe": "barrio narratives, oldie samples, laid-back flow",
        "typical_bpm": (85, 100),
        "emotional_palette": "playful masking of sadness, resilience",
    },
    "cumbia_soul": {
        "culture": "latinx",
        "region": "latin america / us latino",
        "vibe": "danceable, accordion/guitar fusion, cross-generational",
        "typical_bpm": (85, 110),
        "emotional_palette": "joyful with melancholic undercurrent",
    },
    "latin_trap": {
        "culture": "latin urban",
        "region": "us latin / puerto rico / latin america",
        "vibe": "trap beats, spanglish, street narratives, autotune melodies",
        "typical_bpm": (130, 160),
        "emotional_palette": "hustle, pain, celebration",
    },
    "sgv_lo_fi": {
        "culture": "chicano",
        "region": "san gabriel valley",
        "vibe": "introspective, sample-based, bedroom production, late night",
        "typical_bpm": (70, 90),
        "emotional_palette": "wistful resignation, melancholic nostalgia",
    },
}

ETHICAL_GRADIENT_MAP = {
    "positive": ["resilience", "pride", "community", "love", "familia",
                 "healing", "growth", "hope", "solidarity", "peace",
                 "artistic expression", "cultural preservation"],
    "negative": ["violence against groups", "hate speech", "misogyny",
                 "racial slurs (non-reclamatory)", "glorification of harm",
                 "incitement to violence"],
    "context_sensitive": ["weapon talk", "drug references", "gang references",
                          "death", "tragedy", "poverty narrative"],
}


@dataclass
class CulturalMarker:
    marker: str
    category: str
    confidence: float
    context: str


@dataclass
class EthicalScore:
    overall: float
    cultural_resilience: float
    harmful_content_risk: float
    authenticity: float
    justification: str


class CCNAEngine:
    """Cultural Contextualizer & Narrative Architect.

    Analyzes input for:
    1. Cultural markers (SGV, Chicano, Latinx, etc.)
    2. Ethical gradient (appropriation vs appreciation)
    3. Narrative archetype suggestion
    4. Genre-to-culture mapping
    5. Creative intent trace (cultural justification + poetic divergence)
    """

    @classmethod
    def analyze(cls, text: str, genre: Optional[str] = None) -> Dict[str, Any]:
        """Full cultural analysis of input text."""
        markers = cls.extract_markers(text)
        ethical = cls.score_ethics(text)
        archetype = cls.suggest_archetype(text)
        genre_map = cls.map_genre(genre) if genre else None
        intent_trace = cls.build_intent_trace(markers, ethical, genre_map)

        return {
            "analysis_id": f"ccna_{uuid.uuid4().hex[:8]}",
            "input_sample": text[:100] + "..." if len(text) > 100 else text,
            "cultural_markers": [asdict(m) for m in markers[:15]],
            "marker_count": len(markers),
            "ethical_gradient": asdict(ethical),
            "narrative_archetype": archetype,
            "genre_culture_mapping": genre_map,
            "creative_intent_trace": intent_trace,
            "provider": "ccna_engine",
        }

    @classmethod
    def extract_markers(cls, text: str) -> List[CulturalMarker]:
        """Extract cultural markers from text."""
        markers = []
        text_lower = text.lower()

        for category, items in SGV_CULTURAL_MARKERS.items():
            for item in items:
                if item in text_lower:
                    markers.append(CulturalMarker(
                        marker=item,
                        category=f"sgv_{category}",
                        confidence=0.85,
                        context=f"Matched SGV {category}: {item}"
                    ))

        for category, items in CHICANO_IDENTITY_MARKERS.items():
            for item in items:
                if item in text_lower:
                    markers.append(CulturalMarker(
                        marker=item,
                        category=f"chicano_{category}",
                        confidence=0.9,
                        context=f"Matched Chicano identity {category}: {item}"
                    ))

        return markers

    @classmethod
    def score_ethics(cls, text: str) -> EthicalScore:
        """Score cultural and ethical alignment."""
        text_lower = text.lower()
        positive_count = sum(1 for w in ETHICAL_GRADIENT_MAP["positive"] if w in text_lower)
        negative_count = sum(1 for w in ETHICAL_GRADIENT_MAP["negative"] if w in text_lower)
        sensitive_count = sum(1 for w in ETHICAL_GRADIENT_MAP["context_sensitive"] if w in text_lower)

        total = positive_count + negative_count + sensitive_count
        if total == 0:
            return EthicalScore(
                overall=0.7,
                cultural_resilience=0.5,
                harmful_content_risk=0.1,
                authenticity=0.5,
                justification="Insufficient cultural markers for confident scoring. Default safe."
            )

        harmful_risk = min(1.0, (negative_count + sensitive_count * 0.3) / max(1, total))
        resilience = min(1.0, positive_count / max(1, total) + 0.3)
        authenticity = min(1.0, (positive_count + sensitive_count * 0.5) / max(1, total) * 0.8 + 0.2)

        overall = (resilience * 0.5 + authenticity * 0.3 + (1 - harmful_risk) * 0.2)

        justification_parts = []
        if positive_count > 0:
            justification_parts.append(f"Found {positive_count} positive cultural marker(s)")
        if negative_count > 0:
            justification_parts.append(f"WARNING: {negative_count} potentially harmful pattern(s) detected")
        if sensitive_count > 0:
            justification_parts.append(f"{sensitive_count} context-sensitive reference(s) — requires human review")

        return EthicalScore(
            overall=round(overall, 3),
            cultural_resilience=round(resilience, 3),
            harmful_content_risk=round(harmful_risk, 3),
            authenticity=round(authenticity, 3),
            justification="; ".join(justification_parts) if justification_parts else "Clean cultural analysis — no markers of concern."
        )

    @classmethod
    def suggest_archetype(cls, text: str) -> Dict[str, Any]:
        """Suggest narrative archetype based on content analysis."""
        text_lower = text.lower()
        archetypes = []

        if any(w in text_lower for w in ["love", "heart", "baby", "miss", "kiss", "hold"]):
            archetypes.append({
                "type": "star_crossed_lover",
                "confidence": 0.85,
                "description": "Barrio Romeo & Juliet — love across boundaries",
                "motif": "forbidden love, yearning, devotion"
            })

        if any(w in text_lower for w in ["rise", "fight", "never give", "strong", "survive"]):
            archetypes.append({
                "type": "resilient_warrior",
                "confidence": 0.8,
                "description": "Overcoming through strength — the Chicano fighter spirit",
                "motif": "resilience, pride, community rising"
            })

        if any(w in text_lower for w in ["street", "barrio", "block", "hood", "gang"]):
            archetypes.append({
                "type": "barrio_chronicler",
                "confidence": 0.75,
                "description": "Street narrative — authentic barrio storytelling",
                "motif": "lived experience, survival, code of the streets"
            })

        if any(w in text_lower for w in ["gold", "shine", "crown", "king", "queen"]):
            archetypes.append({
                "type": "coronation",
                "confidence": 0.7,
                "description": "Ascension narrative — from nothing to royalty",
                "motif": "self-made royalty, dignity, triumph"
            })

        if any(w in text_lower for w in ["memory", "remember", "used to", "back when", "old days"]):
            archetypes.append({
                "type": "nostalgic_muse",
                "confidence": 0.8,
                "description": "Memory lane — the power of looking back",
                "motif": "nostalgia, first love, innocence lost"
            })

        if not archetypes:
            archetypes.append({
                "type": "everyday_poet",
                "confidence": 0.5,
                "description": "Daily life as art — the mundane made profound",
                "motif": "observation, reflection, quiet beauty"
            })

        return {
            "primary": archetypes[0] if archetypes else None,
            "secondary": archetypes[1] if len(archetypes) > 1 else None,
            "all_detected": archetypes,
        }

    @classmethod
    def map_genre(cls, genre: str) -> Optional[Dict[str, Any]]:
        """Map a genre to its cultural context."""
        genre_key = genre.lower().replace(" ", "_").replace("-", "_")
        mapping = GENRE_TO_CULTURE_MAP.get(genre_key)

        if mapping:
            return {
                "genre": genre,
                "culture": mapping["culture"],
                "region": mapping["region"],
                "vibe": mapping["vibe"],
                "typical_bpm_range": mapping["typical_bpm"],
                "emotional_palette": mapping["emotional_palette"],
                "provider": "ccna_genre_map",
            }
        return None

    @classmethod
    def build_intent_trace(cls, markers: List[CulturalMarker],
                           ethics: EthicalScore,
                           genre_map: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Build the creative intent trace — cultural justification + poetic divergence.

        This is what shows up in the Soulfire payload as creative_intent_trace.
        """
        sgv_markers = [m for m in markers if "sgv" in m.category]
        chicano_markers = [m for m in markers if "chicano" in m.category]

        culture_name = "SGV"
        if chicano_markers:
            culture_name = "Chicano"
        if sgv_markers:
            culture_name = "SGV"

        justification = f"CCNA selected {culture_name}"
        if genre_map:
            justification += f" {genre_map['genre']}"

        marker_descs = [m.marker for m in markers[:5]]
        if marker_descs:
            justification += f" because your request carries {', '.join(marker_descs[:3])} energy"
        else:
            justification += " based on cultural markers detected in your input"

        poetic_divergence = "EPD will break clean rhyme grids on purpose"
        if ethics.authenticity > 0.7:
            poetic_divergence += " — off-grid breaths, mid-word cracks, and non-symmetric phrasing kill robotic feel"

        return {
            "cultural_justification": justification,
            "poetic_divergence": poetic_divergence,
            "ethical_gradient_applied": ethics.overall,
            "cultural_resilience_score": ethics.cultural_resilience,
            "markers_detected": len(markers),
            "provider": "ccna_engine",
        }

    @classmethod
    def cultural_muse(cls, theme: str) -> Dict[str, Any]:
        """Proactively suggest narrative directions based on a theme."""
        suggestions = {
            "love": [
                {"archetype": "First Love", "angle": "Chicana femininity reclaiming the narrative"},
                {"archetype": "Forbidden", "angle": "Barrio Romeo & Juliet — families against it"},
                {"archetype": "Long Distance", "angle": "Cruising solo, missing you on every corner"},
            ],
            "loss": [
                {"archetype": "Grief as Growth", "angle": "Losing abuela, finding yourself"},
                {"archetype": "End of an Era", "angle": "Gentrification taking the barrio"},
                {"archetype": "Heartbreak", "angle": "The one that got away — Art Laboe dedication style"},
            ],
            "pride": [
                {"archetype": "Roots", "angle": "First gen story — parents' sacrifice, your success"},
                {"archetype": "Community", "angle": "Barrio made me — collective pride"},
                {"archetype": "Resilience", "angle": "They counted us out, look at us now"},
            ],
            "struggle": [
                {"archetype": "Grind", "angle": "Late nights, early mornings, making something from nothing"},
                {"archetype": "System", "angle": "Fighting a system never built for us"},
                {"archetype": "Survival", "angle": "Every day is a battle — but we're still here"},
            ],
        }

        theme_key = theme.lower()
        suggestions_list = suggestions.get(theme_key, [
            {"archetype": "Everyday Poetry", "angle": "Finding magic in the mundane"}
        ])

        return {
            "theme": theme,
            "suggestions": suggestions_list,
            "provider": "ccna_cultural_muse",
        }


__all__ = ["CCNAEngine", "CulturalMarker", "EthicalScore"]
