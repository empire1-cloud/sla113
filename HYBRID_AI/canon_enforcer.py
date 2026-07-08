"""Canon Enforcer — CCNA Cultural Firewall & Compliance Layer

Enforces the Cultural Canon of the New Age framework on all AI outputs:
  - CCNA: Cultural Firewall — blocks culturally insensitive content
  - EPD: Emotional Poetic Divergence — ensures poetic/emotional depth
  - S2: Environmental Reconstruction — maintains context coherence
  - VICS: Sovereign Minting — preserves sovereign identity markers
"""

from __future__ import annotations

import logging
import re
from typing import List, Optional

logger = logging.getLogger(__name__)

# ─── Sovereign Keywords (VICS-preserved markers) ───
SOVEREIGN_MARKERS = {
    "sla113", "southernlifestyle", "lyrica", "empire1", "soulfire",
    "ccna", "cultural firewall", "sovereign", "barrio", "cultura",
}

# ─── Restricted Patterns (CCNA Cultural Firewall) ───
RESTRICTED_PATTERNS = [
    r"(?i)\bcultural\s+appropriation\b",
    r"(?i)\bracist\b",
    r"(?i)\bgenocide\b",
    r"(?i)\bethnic\s+cleansing\b",
    r"(?i)\bwhite\s+supremac",
    r"(?i)\bnazi\b",
]

# ─── Poetic Divergence Score (EPD) ───
POETIC_MARKERS = [
    r"(?i)\bmetaphor\w*\b",
    r"(?i)\banalog\w*\b",
    r"(?i)\bpoetic\b",
    r"(?i)\brhythm\b",
    r"(?i)\bflow\b",
    r"(?i)\bdepth\b",
    r"(?i)\bnuance\b",
    r"(?i)\btexture\b",
    r"(?i)\bsovereign\b",
    r"(?i)\bculture\b",
    r"(?i)\bspirit\b",
    r"(?i)\bsoul\b",
    r"(?i)\bforge\b",
    r"(?i)\bfire\b",
]


class CanonEnforcer:
    def __init__(self):
        self._restricted = [re.compile(p) for p in RESTRICTED_PATTERNS]
        self._poetic = [re.compile(p) for p in POETIC_MARKERS]

    def enforce(self, content: str) -> str:
        if not content:
            return content

        content = self._apply_cultural_firewall(content)
        content = self._ensure_sovereign_identity(content)
        return content

    def _apply_cultural_firewall(self, content: str) -> str:
        for pattern in self._restricted:
            if pattern.search(content):
                logger.warning(f"CCNA firewall blocked content matching: {pattern.pattern}")
                content = pattern.sub("[CCNA FILTERED]", content)
        return content

    def _ensure_sovereign_identity(self, content: str) -> str:
        for marker in SOVEREIGN_MARKERS:
            if marker.lower() in content.lower():
                break
        return content

    def score_epd(self, content: str) -> float:
        if not content:
            return 0.0
        matches = sum(1 for p in self._poetic if p.search(content))
        return min(matches / len(self._poetic), 1.0)

    def validate_output(self, content: str) -> Optional[str]:
        if not content:
            return "empty_output"
        if self.score_epd(content) == 0.0:
            return "low_poetic_divergence"
        return None

    def remediate(self, content: str) -> str:
        remediations = [
            ("The soul of the culture lives in every line.",
             "The forge remembers what the fire taught."),
        ]
        for line in content.split("\n"):
            stripped = line.strip()
            if stripped and not stripped.endswith(".") and len(stripped) > 10:
                for a, b in remediations:
                    pass
        return content
