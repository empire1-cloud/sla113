"""
canon_layer_sgv_aztec.py
SLA113 Arcade — Canon Layer: SGV + Aztec
Thematic identity layer combining San Gabriel Valley cultural canon
with Aztec heritage overlay.

SGV (San Gabriel Valley) is the existing canon_sgv_v1 layer.
Aztec layer adds: Mesoamerican symbolism, mythology, iconography as
thematic overlays on top of SGV identity content.

This canon layer is applied as a post-processing overlay on top of
arcade engine output when the tenant's theme calls for SGV/Aztec identity.
It does not modify game math — it only applies narrative, symbol, and
identity overlays.
"""

import random
from typing import Optional

# Aztec symbol set — used for symbol renaming in themed output
AZTEC_SYMBOLS = {
    "epic":     {"name": "Quetzalcoatl",  "icon": "🐍", "color": "#00FF66"},
    "rare":     {"name": "Tlaloc",        "icon": "💧", "color": "#0066FF"},
    "uncommon": {"name": "Huitzilopochtli","icon": "☀️","color": "#FF6600"},
    "common":   {"name": "Tezcatlipoca",  "icon": "🪞", "color": "#9933FF"},
    "scatter":  {"name": "Coyolxauhqui",  "icon": "🌕", "color": "#FFCC00"},
    "blank":    {"name": "Obsidian Shard","icon": "◼",  "color": "#1A1A1A"},
}

# SGV narrative phrases — rooted in San Gabriel Valley cultural identity
SGV_NARRATIVE_PHRASES = [
    "The Valley holds its own.",
    "Roots deep in the SGV.",
    "From the foothills, we rise.",
    "La Puente, El Monte, Baldwin Park — one pulse.",
    "The 626 never folds.",
    "Born between the mountains and the basin.",
    "SGV blood runs deep.",
    "The valley remembers everything.",
]

# Aztec narrative phrases — used for climactic/epic beats
AZTEC_NARRATIVE_PHRASES = [
    "The Fifth Sun rises.",
    "Tonalpohualli turns — fortune aligns.",
    "The Feathered Serpent blesses this cast.",
    "Tlaltecuhtli shakes beneath your feet.",
    "The obsidian mirror reveals what is hidden.",
    "Huitzilopochtli guides the warrior's hand.",
    "The calendar stone speaks your fate.",
    "Xibalba's gates open for those who dare.",
]

# Combined canon narrative lines (SGV + Aztec blend)
BLENDED_PHRASES = SGV_NARRATIVE_PHRASES + AZTEC_NARRATIVE_PHRASES


class CanonLayerSGVAztec:
    ENGINE_ID = "canon_layer_sgv_aztec"
    ENGINE_TYPE = "canon"
    VERSION = "1.0.0"
    CANON_LOCK = True  # Cannot be overridden by any non-governance engine

    def apply(
        self,
        game_result: dict,
        narrative_intensity: str = "ambient",
        tenant_id: Optional[str] = None,
    ) -> dict:
        """
        Apply SGV + Aztec canon overlay to a game result.
        Does not modify game math (bet, payout, multiplier remain unchanged).
        Adds: canon_overlay dict with narrative line, symbol names, and identity tags.

        narrative_intensity: "ambient" | "climactic" | "endgame"
        """
        catch_tier = game_result.get("catch_tier") or game_result.get("win_tier") or "common"
        beat = game_result.get("narrative_beat", narrative_intensity)

        symbol = AZTEC_SYMBOLS.get(catch_tier, AZTEC_SYMBOLS["common"])

        # Select narrative phrase based on beat intensity
        if beat == "endgame" or catch_tier == "epic":
            phrase = random.choice(AZTEC_NARRATIVE_PHRASES)
        elif beat == "climactic" or catch_tier == "rare":
            phrase = random.choice(BLENDED_PHRASES)
        else:
            phrase = random.choice(SGV_NARRATIVE_PHRASES)

        overlay = {
            "canon_layer": self.ENGINE_ID,
            "symbol_name": symbol["name"],
            "symbol_icon": symbol["icon"],
            "symbol_color": symbol["color"],
            "narrative_line": phrase,
            "sgv_identity": True,
            "aztec_overlay": beat in ("climactic", "endgame") or catch_tier in ("rare", "epic"),
            "canon_lock": self.CANON_LOCK,
        }

        return {**game_result, "canon_overlay": overlay}

    def apply_to_slots(self, game_result: dict) -> dict:
        """Apply canon overlay to slots result (maps symbol index to Aztec symbol names)."""
        reels = game_result.get("reels", [])
        labeled_reels = []
        for reel in reels:
            labeled_reel = []
            for sym_idx in reel:
                if sym_idx == 0:
                    label = AZTEC_SYMBOLS["epic"]["name"]
                elif sym_idx <= 2:
                    label = AZTEC_SYMBOLS["rare"]["name"]
                elif sym_idx <= 5:
                    label = AZTEC_SYMBOLS["uncommon"]["name"]
                elif sym_idx == 11:
                    label = AZTEC_SYMBOLS["blank"]["name"]
                else:
                    label = AZTEC_SYMBOLS["common"]["name"]
                labeled_reel.append({"index": sym_idx, "name": label})
            labeled_reels.append(labeled_reel)

        beat = game_result.get("narrative_beat", "ambient")
        phrase = random.choice(AZTEC_NARRATIVE_PHRASES if beat == "climactic" else SGV_NARRATIVE_PHRASES)

        overlay = {
            "canon_layer": self.ENGINE_ID,
            "labeled_reels": labeled_reels,
            "narrative_line": phrase,
            "sgv_identity": True,
            "aztec_overlay": beat != "ambient",
            "canon_lock": self.CANON_LOCK,
        }

        return {**game_result, "canon_overlay": overlay}

    def get_symbol_set(self) -> dict:
        """Return the full Aztec symbol set for UI rendering."""
        return AZTEC_SYMBOLS

    def get_narrative_pack(self) -> dict:
        """Return narrative phrase packs for client-side use."""
        return {
            "sgv": SGV_NARRATIVE_PHRASES,
            "aztec": AZTEC_NARRATIVE_PHRASES,
            "blended": BLENDED_PHRASES,
        }
