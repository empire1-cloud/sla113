#!/usr/bin/env python3
"""Generate backgrounds, weapon skins, HUD pieces, and VFX from a JSON contract."""
from __future__ import annotations

import argparse
import base64
import io
import json
import os
import time
from pathlib import Path
from typing import Any

from PIL import Image

DEFAULT_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1.5")
DEFAULT_QUALITY = os.getenv("OPENAI_IMAGE_QUALITY", "high")
DEFAULT_CONTRACT = Path(__file__).with_name("aztec_static_assets.json")
DEFAULT_OUTPUT = Path("output/static_art")
DEFAULT_MANIFEST = Path("output/static_art_manifest.json")
DEFAULT_ESTIMATE = float(os.getenv("OPENAI_IMAGE_ESTIMATE_USD", "0.034"))


def fail(message: str) -> "NoReturn":
    raise SystemExit(message)


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"Missing contract: {path}")
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON in {path}: {exc}")


def get_client():
    if not os.getenv("OPENAI_API_KEY"):
        fail("OPENAI_API_KEY is not set")
    try:
        from openai import OpenAI
    except ImportError:
        fail("Missing dependency: pip install openai Pillow")
    return OpenAI()


def validate(contract: dict[str, Any]) -> list[dict[str, Any]]:
    assets = contract.get("assets")
    if not isinstance(assets, list) or not assets:
        fail("Contract must contain a non-empty assets array")
    seen: set[str] = set()
    for asset in assets:
        aid = asset.get("id")
        if not aid or aid in seen:
            fail(f"Invalid or duplicate asset id: {aid}")
        seen.add(aid)
        if asset.get("background") not in {"transparent", "opaque"}:
            fail(f"{aid}: background must be transparent or opaque")
        if not asset.get("prompt") or not asset.get("size"):
            fail(f"{aid}: prompt and size are required")
    return assets


def decode(result: Any) -> Image.Image:
    data = getattr(result, "data", None)
    if not data or not getattr(data[0], "b64_json", None):
        fail("Image API returned no b64_json data")
    raw = base64.b64decode(data[0].b64_json)
    return Image.open(io.BytesIO(raw)).convert("RGBA")


def alpha_status(image: Image.Image) -> bool:
    return image.getchannel("A").getextrema()[0] < 255


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Aztec Abyss static game art")
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--asset", action="append", default=[], help="Asset id; repeat to select several")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--quality", default=DEFAULT_QUALITY)
    parser.add_argument("--estimate-per-image", type=float, default=DEFAULT_ESTIMATE)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    contract = load_json(args.contract)
    assets = validate(contract)
    if args.asset:
        wanted = set(args.asset)
        assets = [a for a in assets if a["id"] in wanted]
        missing = wanted - {a["id"] for a in assets}
        if missing:
            fail(f"Unknown asset id(s): {', '.join(sorted(missing))}")

    estimate = len(assets) * args.estimate_per_image
    print(f"{len(assets)} assets (~${estimate:.2f} planning estimate, verify current pricing)")
    for asset in assets:
        print(f"  {asset['id']} [{asset['category']}] {asset['size']} {asset['background']}")
    if args.dry_run:
        print("No API calls made.")
        return

    client = get_client()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": 1,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": args.model,
        "quality": args.quality,
        "assets": {},
    }
    style = contract.get("style_bible", "")
    for asset in assets:
        aid = asset["id"]
        background = asset["background"]
        prompt = f"{style} {asset['prompt']}"
        print(f"generating {aid}...")
        result = client.images.generate(
            model=args.model,
            prompt=prompt,
            size=asset["size"],
            quality=args.quality,
            background=background,
            output_format="png",
            n=1,
        )
        image = decode(result)
        out = args.output_dir / f"{aid}.png"
        image.save(out, optimize=True)
        transparent = alpha_status(image)
        if background == "transparent" and not transparent:
            print(f"  [WARN] {aid}: requested transparency but output is fully opaque")
        manifest["assets"][aid] = {
            "category": asset["category"],
            "file": str(out),
            "size": list(image.size),
            "background_requested": background,
            "transparency_verified": transparent,
        }
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(f"  saved {out}")

    print(f"Manifest written: {args.manifest}")


if __name__ == "__main__":
    main()
