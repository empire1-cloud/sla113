"""
sprite_placeholder.py
SLA113 Arcade — Placeholder Sprite Generator

Generates simple procedural spritesheet/background PNGs for bosses and
backgrounds referenced by the seeded lobbies but with no real art yet.
Not meant to be final art — a stand-in so the FireKirin/Juwa pipeline
renders something coherent instead of blank shapes, until real sprite
sheets are registered through /sprites/register.
"""

import io
from PIL import Image, ImageDraw, ImageFont


def _font(size: int):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _label_lines(label: str) -> list:
    words = label.replace("_", " ").title().split(" ")
    lines, cur = [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if len(trial) > 12 and cur:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines[:3]


def generate_boss_spritesheet(label: str, color: str, frame_size: int = 128, grid: int = 2) -> bytes:
    """4-frame placeholder spritesheet (grid x grid) — a simple pulsing emblem per frame."""
    sheet = Image.new("RGBA", (frame_size * grid, frame_size * grid), (0, 0, 0, 0))
    base_rgb = tuple(int(color.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    font = _font(max(10, frame_size // 10))
    lines = _label_lines(label)

    for idx in range(grid * grid):
        pulse = 0.75 + 0.25 * (idx / max(1, grid * grid - 1))
        rgb = tuple(min(255, int(c * pulse)) for c in base_rgb)
        frame = Image.new("RGBA", (frame_size, frame_size), (0, 0, 0, 0))
        d = ImageDraw.Draw(frame)
        pad = int(frame_size * 0.08)
        d.ellipse([pad, pad, frame_size - pad, frame_size - pad], fill=rgb + (255,), outline=(10, 10, 10, 255), width=3)
        inner = int(frame_size * 0.22)
        d.ellipse([inner, inner, frame_size - inner, frame_size - inner], outline=(0, 0, 0, 90), width=2)
        total_h = len(lines) * (font.size + 2)
        y = (frame_size - total_h) / 2
        for line in lines:
            bbox = d.textbbox((0, 0), line, font=font)
            w = bbox[2] - bbox[0]
            d.text(((frame_size - w) / 2, y), line, fill=(0, 0, 0, 230), font=font)
            y += font.size + 2
        row, col = divmod(idx, grid)
        sheet.paste(frame, (col * frame_size, row * frame_size))

    buf = io.BytesIO()
    sheet.save(buf, format="PNG")
    return buf.getvalue()


def generate_background(label: str, color: str, size: tuple = (800, 450)) -> bytes:
    """Single-frame placeholder background — radial gradient in the theme color."""
    w, h = size
    base_rgb = tuple(int(color.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    img = Image.new("RGB", (w, h), (8, 6, 4))
    d = ImageDraw.Draw(img)
    cx, cy = w / 2, h * 0.4
    max_r = max(w, h) * 0.75
    steps = 60
    for i in range(steps, 0, -1):
        t = i / steps
        r = max_r * t
        rgb = tuple(int(8 + (c - 8) * (1 - t) * 0.5) for c in base_rgb)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgb)
    font = _font(28)
    label_text = label.replace("_", " ").title()
    bbox = d.textbbox((0, 0), label_text, font=font)
    tw = bbox[2] - bbox[0]
    d.text(((w - tw) / 2, h - 50), label_text, fill=(212, 175, 55, 255), font=font)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def generate_loader(color: str = "#d4af37", size: int = 400) -> bytes:
    img = Image.new("RGB", (size, size), (5, 5, 5))
    d = ImageDraw.Draw(img)
    base_rgb = tuple(int(color.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    d.ellipse([size * 0.3, size * 0.3, size * 0.7, size * 0.7], outline=base_rgb, width=6)
    font = _font(24)
    text = "SLA113"
    bbox = d.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    d.text(((size - tw) / 2, size / 2 - 12), text, fill=base_rgb, font=font)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
