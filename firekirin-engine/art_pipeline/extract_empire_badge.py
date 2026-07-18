#!/usr/bin/env python3
"""Extract the circular Empire-1 coin from a logo image as a transparent PNG.

Unlike a simple global warm-pixel bounding box, this implementation closes the
threshold mask, finds connected components, and selects the largest compact,
near-square gold component. That prevents gold wordmark letters from widening
the crop. The final alpha is a supersampled circle so the badge stays crisp at
small in-game sizes.
"""
from __future__ import annotations

import argparse
import math
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


def fail(message: str) -> "NoReturn":
    raise SystemExit(message)


def gold_mask(image: Image.Image, brightness: int, warm_delta: int) -> np.ndarray:
    arr = np.asarray(image.convert("RGB"), dtype=np.int16)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    mask = (r > b + warm_delta) & (g > b + max(3, warm_delta // 3)) & ((r + g + b) > brightness)
    mask_img = Image.fromarray((mask.astype(np.uint8) * 255), mode="L")
    mask_img = mask_img.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.MinFilter(5))
    return np.asarray(mask_img) > 0


def connected_components(mask: np.ndarray) -> list[dict]:
    height, width = mask.shape
    visited = np.zeros_like(mask, dtype=bool)
    components: list[dict] = []
    for y in range(height):
        for x in range(width):
            if not mask[y, x] or visited[y, x]:
                continue
            queue = deque([(x, y)])
            visited[y, x] = True
            xs: list[int] = []
            ys: list[int] = []
            while queue:
                cx, cy = queue.popleft()
                xs.append(cx)
                ys.append(cy)
                for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
                    if 0 <= nx < width and 0 <= ny < height and mask[ny, nx] and not visited[ny, nx]:
                        visited[ny, nx] = True
                        queue.append((nx, ny))
            x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
            box_w, box_h = x1 - x0 + 1, y1 - y0 + 1
            area = len(xs)
            fill = area / max(1, box_w * box_h)
            aspect = box_w / max(1, box_h)
            squareness = max(0.0, 1.0 - abs(math.log(max(aspect, 1e-6))))
            compact_score = area * (0.35 + fill) * (0.25 + squareness)
            components.append({
                "bbox": (x0, y0, x1 + 1, y1 + 1),
                "area": area,
                "fill": fill,
                "aspect": aspect,
                "score": compact_score,
            })
    return components


def choose_coin(components: list[dict], image_size: tuple[int, int]) -> dict:
    width, height = image_size
    min_area = width * height * 0.002
    candidates = [
        c for c in components
        if c["area"] >= min_area and 0.58 <= c["aspect"] <= 1.72
    ]
    if not candidates:
        fail("No compact gold component found; try lowering --brightness or --warm-delta")
    return max(candidates, key=lambda c: c["score"])


def circular_alpha(size: int, feather: float = 1.5, supersample: int = 4) -> Image.Image:
    ss_size = size * supersample
    yy, xx = np.ogrid[:ss_size, :ss_size]
    center = (ss_size - 1) / 2
    radius = center - supersample
    dist = np.sqrt((xx - center) ** 2 + (yy - center) ** 2)
    edge = feather * supersample
    alpha = np.clip((radius + edge - dist) / max(edge, 1), 0, 1) * 255
    return Image.fromarray(alpha.astype(np.uint8), mode="L").resize((size, size), Image.Resampling.LANCZOS)


def extract(src: Path, out: Path, output_size: int, brightness: int, warm_delta: int, padding: float, debug_mask: Path | None) -> None:
    if not src.exists():
        fail(f"Source image not found: {src}")
    image = Image.open(src).convert("RGB")
    mask = gold_mask(image, brightness, warm_delta)
    if debug_mask:
        debug_mask.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray((mask.astype(np.uint8) * 255), mode="L").save(debug_mask)
    components = connected_components(mask)
    coin = choose_coin(components, image.size)
    x0, y0, x1, y1 = coin["bbox"]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    radius = max(x1 - x0, y1 - y0) / 2
    half = math.ceil(radius * (1 + padding))
    left, top = round(cx - half), round(cy - half)
    right, bottom = round(cx + half), round(cy + half)

    crop_size = right - left
    canvas = Image.new("RGB", (crop_size, crop_size), (0, 0, 0))
    src_box = (max(0, left), max(0, top), min(image.width, right), min(image.height, bottom))
    region = image.crop(src_box)
    canvas.paste(region, (max(0, -left), max(0, -top)))

    result = canvas.convert("RGBA")
    result.putalpha(circular_alpha(crop_size))
    result = result.resize((output_size, output_size), Image.Resampling.LANCZOS)
    out.parent.mkdir(parents=True, exist_ok=True)
    result.save(out, optimize=True)
    print(
        f"selected bbox={coin['bbox']} area={coin['area']} aspect={coin['aspect']:.2f}; "
        f"saved {out} ({output_size}x{output_size}, RGBA)"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract Empire-1 circular coin badge")
    parser.add_argument("src", type=Path)
    parser.add_argument("--out", type=Path, default=Path("ASSETS/shield_badge.png"))
    parser.add_argument("--size", type=int, default=256)
    parser.add_argument("--brightness", type=int, default=90)
    parser.add_argument("--warm-delta", type=int, default=15)
    parser.add_argument("--padding", type=float, default=0.05)
    parser.add_argument("--debug-mask", type=Path)
    args = parser.parse_args()
    if args.size < 32:
        fail("--size must be at least 32")
    if not 0 <= args.padding <= 0.5:
        fail("--padding must be between 0 and 0.5")
    extract(args.src, args.out, args.size, args.brightness, args.warm_delta, args.padding, args.debug_mask)


if __name__ == "__main__":
    main()
