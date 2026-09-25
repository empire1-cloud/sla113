"""Deterministic placeholder SVG sprites — one per paytable target."""
from __future__ import annotations

import hashlib
import html
import re
from pathlib import Path
from typing import Any, Dict, List

PALETTE = ["#48bfe3", "#64dfdf", "#ffd166", "#ef476f", "#06d6a0", "#e8b923", "#e6007a", "#007aff"]


def _slug(key: str) -> str:
    return re.sub(r"[^a-z0-9_-]+", "_", key.lower()).strip("_") or "target"


def color_for(key: str, index: int) -> str:
    return PALETTE[index % len(PALETTE)]


def build_assets(spec: Any, root: Path) -> List[Dict[str, Any]]:
    out = root / "web" / "assets"
    out.mkdir(parents=True, exist_ok=True)
    ordered = sorted(spec.paytable.items(), key=lambda kv: kv[1])
    assets = []
    for i, (key, payout) in enumerate(ordered):
        size = 96 + int(144 * i / max(1, len(ordered) - 1))
        color = color_for(key, i)
        label = html.escape(str(key))
        path = out / f"fish_{_slug(key)}.svg"
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size // 2}" viewBox="0 0 240 120">'
            f'<ellipse cx="110" cy="60" rx="78" ry="42" fill="{color}"/>'
            f'<polygon points="180,60 235,25 235,95" fill="{color}"/>'
            f'<circle cx="70" cy="48" r="7" fill="#071018"/>'
            f'<text x="120" y="66" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#071018">{label}</text></svg>'
        )
        path.write_text(svg, encoding="utf-8")
        assets.append({
            "id": "sprite_" + hashlib.sha256(f"{spec.name}:{key}".encode()).hexdigest()[:12],
            "type": "sprite",
            "target": key,
            "payout": payout,
            "color": color,
            "path": str(path.relative_to(root)),
            "dimensions": {"width": size, "height": size // 2},
            "source": "genesis_deterministic_placeholder",
        })
    return assets
