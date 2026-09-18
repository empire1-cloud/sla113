"""Audio domain definitions — shared creative vocabulary for music generation."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

_DOMAIN_DIR = Path(__file__).parent

_cache: Dict[str, Any] = {}


def _load(name: str) -> List[Dict[str, Any]]:
    """Load a domain definition file, with caching."""
    if name in _cache:
        return _cache[name]
    path = _DOMAIN_DIR / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Domain definition not found: {name} at {path}")
    with open(path) as f:
        data = json.load(f)
    items = data.get(name, data.get("matrices", data.get("scales", data.get("presets", data.get("instruments", data.get("archetypes", []))))))
    _cache[name] = items
    return items


def get_genres() -> List[Dict[str, Any]]:
    return _load("genres")

def get_tones() -> List[Dict[str, Any]]:
    return _load("tones")

def get_scales() -> List[Dict[str, Any]]:
    return _load("melodies")  # scales are in melodies.json

def get_chord_progressions() -> List[Dict[str, Any]]:
    data = _load_raw("melodies")
    return data.get("chord_progressions", [])

def get_cultural_matrices() -> List[Dict[str, Any]]:
    return _load("cultural-matrices")

def get_vocal_archetypes() -> List[Dict[str, Any]]:
    return _load("vocal-archetypes")

def get_instruments() -> List[Dict[str, Any]]:
    return _load("instruments")

def get_mastering_presets() -> List[Dict[str, Any]]:
    return _load("mastering-presets")


def _load_raw(name: str) -> Dict[str, Any]:
    cache_key = f"raw_{name}"
    if cache_key in _cache:
        return _cache[cache_key]
    path = _DOMAIN_DIR / f"{name}.json"
    with open(path) as f:
        data = json.load(f)
    _cache[cache_key] = data
    return data


def get_genre(id: str) -> Optional[Dict[str, Any]]:
    for g in get_genres():
        if g["id"] == id:
            return g
    return None


def get_cultural_matrix(id: str) -> Optional[Dict[str, Any]]:
    for m in get_cultural_matrices():
        if m["id"] == id:
            return m
    return None


def get_mastering_preset_for_genre(genre_id: str) -> Optional[Dict[str, Any]]:
    for p in get_mastering_presets():
        if genre_id in p.get("genres", []):
            return p
    return None


def get_tone(id: str) -> Optional[Dict[str, Any]]:
    for t in get_tones():
        if t["id"] == id:
            return t
    return None


def get_instrument(id: str) -> Optional[Dict[str, Any]]:
    for i in get_instruments():
        if i["id"] == id:
            return i
    return None


def get_vocal_archetype(id: str) -> Optional[Dict[str, Any]]:
    for a in get_vocal_archetypes():
        if a["id"] == id:
            return a
    return None


def clear_cache():
    _cache.clear()
