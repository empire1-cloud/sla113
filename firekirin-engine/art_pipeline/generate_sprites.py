#!/usr/bin/env python3
"""Generate consistent transparent sprite frames from a JSON roster contract.

This pipeline keeps model/provider settings configurable, preserves undecorated
reference frames for edit-chain consistency, normalizes finished frames to a
stable canvas, verifies transparency, applies optional Empire badge branding,
and writes an audit-friendly manifest consumed by pack_sprite_sheet.py.
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from PIL import Image

DEFAULT_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1.5")
DEFAULT_QUALITY = os.getenv("OPENAI_IMAGE_QUALITY", "medium")
DEFAULT_SIZE = os.getenv("OPENAI_IMAGE_SIZE", "1024x1024")
DEFAULT_FORMAT = "png"
DEFAULT_ESTIMATE = float(os.getenv("OPENAI_IMAGE_ESTIMATE_USD", "0.034"))
DEFAULT_ROSTER = Path(__file__).with_name("aztec_roster.json")
DEFAULT_OUTPUT = Path("output/sprites")
DEFAULT_MANIFEST = Path("output/manifest.json")
DEFAULT_BADGE = Path("ASSETS/shield_badge.png")

GLYPH_PROMPT = (
    "The creature carries the Empire-1 sigil as an integrated body marking, not "
    "a sticker: a gold stepped square-spiral glyph with a complementary gold "
    "step-fret pattern flowing naturally along the body. Keep the mark stable, "
    "tasteful, readable, and in the same location across every frame."
)


def fail(message: str) -> "NoReturn":
    raise SystemExit(message)


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"Missing JSON file: {path}")
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON in {path}: {exc}")


def validate_roster(roster: dict[str, Any]) -> list[dict[str, Any]]:
    creatures = roster.get("creatures")
    if not isinstance(creatures, list) or not creatures:
        fail("Roster must contain a non-empty 'creatures' array")

    seen: set[str] = set()
    for creature in creatures:
        cid = creature.get("id")
        if not isinstance(cid, str) or not cid.strip():
            fail("Every creature needs a non-empty string id")
        if cid in seen:
            fail(f"Duplicate creature id: {cid}")
        seen.add(cid)
        if creature.get("logo_mode", "overlay") not in {"overlay", "inworld", "none"}:
            fail(f"{cid}: logo_mode must be overlay, inworld, or none")
        frames = creature.get("frames")
        if not isinstance(frames, list) or not frames:
            fail(f"{cid}: frames must be a non-empty array")
        for index, frame in enumerate(frames):
            if not frame.get("state") or not frame.get("desc"):
                fail(f"{cid}: frame {index} needs state and desc")
    return creatures


def get_client():
    if not os.getenv("OPENAI_API_KEY"):
        fail("OPENAI_API_KEY is not set")
    try:
        from openai import OpenAI
    except ImportError:
        fail("Missing dependency: pip install openai Pillow")
    return OpenAI()


def decode_image_result(result: Any) -> bytes:
    data = getattr(result, "data", None)
    if not data:
        fail("Image API returned no data")
    b64 = getattr(data[0], "b64_json", None)
    if not b64:
        fail("Image API response did not include b64_json")
    return base64.b64decode(b64)


def transparent_ok(image: Image.Image) -> bool:
    alpha = image.convert("RGBA").getchannel("A")
    low, high = alpha.getextrema()
    return low < 255 and high > 0


def normalize_canvas(image: Image.Image, canvas_size: int = 1024, padding_ratio: float = 0.07) -> Image.Image:
    """Trim transparent overflow, fit without distortion, and center consistently."""
    rgba = image.convert("RGBA")
    bbox = rgba.getchannel("A").getbbox()
    if not bbox:
        return Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    subject = rgba.crop(bbox)
    max_side = int(canvas_size * (1 - 2 * padding_ratio))
    scale = min(max_side / subject.width, max_side / subject.height)
    target = (
        max(1, round(subject.width * scale)),
        max(1, round(subject.height * scale)),
    )
    subject = subject.resize(target, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    x = (canvas_size - subject.width) // 2
    y = (canvas_size - subject.height) // 2
    canvas.alpha_composite(subject, (x, y))
    return canvas


def apply_badge(image: Image.Image, badge_path: Path, scale_ratio: float, position: str) -> tuple[Image.Image, bool]:
    if not badge_path.exists():
        return image, False
    badge = Image.open(badge_path).convert("RGBA")
    target_w = max(16, int(image.width * scale_ratio))
    ratio = target_w / badge.width
    badge = badge.resize((target_w, max(1, round(badge.height * ratio))), Image.Resampling.LANCZOS)
    margin = int(image.width * 0.025)
    positions = {
        "bottom-right": (image.width - badge.width - margin, image.height - badge.height - margin),
        "bottom-left": (margin, image.height - badge.height - margin),
        "top-right": (image.width - badge.width - margin, margin),
        "top-left": (margin, margin),
        "center": ((image.width - badge.width) // 2, (image.height - badge.height) // 2),
    }
    result = image.copy()
    result.alpha_composite(badge, positions.get(position, positions["bottom-right"]))
    return result, True


def build_prompt(style_bible: str, creature: dict[str, Any], frame_desc: str | None = None) -> str:
    prompt = f"{style_bible} {creature['base_prompt']}"
    if frame_desc:
        prompt += (
            " Keep the exact same creature design, anatomy, proportions, colors, "
            f"markings, lighting, and camera angle as the reference. Change only the pose to: {frame_desc}."
        )
    if creature.get("logo_mode") == "inworld":
        prompt += " " + GLYPH_PROMPT
    return prompt


def generate_concept(client: Any, *, model: str, quality: str, size: str, prompt: str) -> bytes:
    result = client.images.generate(
        model=model,
        prompt=prompt,
        size=size,
        quality=quality,
        background="transparent",
        output_format=DEFAULT_FORMAT,
        n=1,
    )
    return decode_image_result(result)


def generate_edit(client: Any, *, model: str, quality: str, size: str, prompt: str, reference: Path) -> bytes:
    with reference.open("rb") as ref:
        result = client.images.edit(
            model=model,
            image=ref,
            prompt=prompt,
            size=size,
            quality=quality,
            background="transparent",
            output_format=DEFAULT_FORMAT,
        )
    return decode_image_result(result)


def read_image(raw: bytes, label: str) -> Image.Image:
    try:
        return Image.open(io.BytesIO(raw)).convert("RGBA")
    except Exception as exc:
        fail(f"Could not decode {label}: {exc}")


def select_creatures(creatures: list[dict[str, Any]], requested: list[str]) -> list[dict[str, Any]]:
    if not requested:
        return creatures
    wanted = set(requested)
    selected = [c for c in creatures if c["id"] in wanted]
    missing = sorted(wanted - {c["id"] for c in selected})
    if missing:
        fail(f"Unknown creature id(s): {', '.join(missing)}")
    return selected


def estimate(selected: list[dict[str, Any]], per_image: float) -> dict[str, Any]:
    rows = []
    total = 0
    for creature in selected:
        count = len(creature["frames"])
        total += count
        rows.append({"id": creature["id"], "images": count, "estimate_usd": round(count * per_image, 2)})
    return {"creatures": rows, "total_images": total, "estimate_usd": round(total * per_image, 2)}


def load_existing_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"creatures": {}}
    data = load_json(path)
    if not isinstance(data.get("creatures"), dict):
        data["creatures"] = {}
    return data


def run_creature(
    client: Any,
    roster: dict[str, Any],
    creature: dict[str, Any],
    manifest: dict[str, Any],
    *,
    output_dir: Path,
    badge_path: Path,
    badge_scale: float,
    badge_position: str,
    model: str,
    quality: str,
    size: str,
    resume: bool,
) -> None:
    cid = creature["id"]
    frames_spec = creature["frames"]
    creature_dir = output_dir / cid
    creature_dir.mkdir(parents=True, exist_ok=True)
    manifest_entry = {
        "name": creature["name"],
        "role": creature.get("role"),
        "engine_key": creature.get("engine_key", cid),
        "engine_animation": creature.get("engine_animation"),
        "aggregate": bool(creature.get("aggregate", False)),
        "frame_size": int(creature.get("frame_size", 256)),
        "logo_mode": creature.get("logo_mode", "overlay"),
        "frames": [],
    }

    style_bible = roster.get("style_bible", "")
    prior_reference: Path | None = None

    for index, frame_spec in enumerate(frames_spec):
        state = frame_spec["state"]
        out_path = creature_dir / f"{cid}_{index:02d}_{state}.png"
        ref_path = creature_dir / f"_reference_{index:02d}.png"

        if resume and out_path.exists() and ref_path.exists():
            image = Image.open(out_path).convert("RGBA")
            prior_reference = ref_path
            manifest_entry["frames"].append({
                "index": index,
                "state": state,
                "desc": frame_spec["desc"],
                "file": str(out_path),
                "reference_file": str(ref_path),
                "loop": bool(frame_spec.get("loop", state in {"idle", "swim", "walk"})),
                "frame_rate": int(frame_spec.get("frame_rate", 8)),
                "transparency_verified": transparent_ok(image),
                "branding": "resumed",
            })
            print(f"  resume {index:02d} [{state}] {out_path}")
            continue

        if index == 0:
            prompt = build_prompt(style_bible, creature)
            raw = generate_concept(client, model=model, quality=quality, size=size, prompt=prompt)
        else:
            if prior_reference is None or not prior_reference.exists():
                fail(f"{cid}: missing prior reference before frame {index}")
            prompt = build_prompt(style_bible, creature, frame_spec["desc"])
            raw = generate_edit(
                client,
                model=model,
                quality=quality,
                size=size,
                prompt=prompt,
                reference=prior_reference,
            )

        raw_image = read_image(raw, f"{cid} frame {index}")
        raw_image.save(ref_path)
        prior_reference = ref_path
        normalized = normalize_canvas(raw_image)
        alpha_ok = transparent_ok(normalized)
        if not alpha_ok:
            print(f"  [WARN] {cid} frame {index}: transparency verification failed")

        logo_mode = creature.get("logo_mode", "overlay")
        if logo_mode == "overlay":
            finalized, applied = apply_badge(normalized, badge_path, badge_scale, badge_position)
            branding = "overlay" if applied else "overlay-missing-badge"
            if not applied:
                print(f"  [WARN] {badge_path} missing; frame saved without badge")
        elif logo_mode == "inworld":
            finalized, branding = normalized, "inworld"
        else:
            finalized, branding = normalized, "none"

        finalized.save(out_path, optimize=True)
        manifest_entry["frames"].append({
            "index": index,
            "state": state,
            "desc": frame_spec["desc"],
            "file": str(out_path),
            "reference_file": str(ref_path),
            "loop": bool(frame_spec.get("loop", state in {"idle", "swim", "walk"})),
            "frame_rate": int(frame_spec.get("frame_rate", 8)),
            "transparency_verified": alpha_ok,
            "branding": branding,
        })
        print(f"  saved {index:02d} [{state}] {out_path}")

    manifest["creatures"][cid] = manifest_entry


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate SLA113 Aztec sprite frames")
    parser.add_argument("--roster", type=Path, default=DEFAULT_ROSTER)
    parser.add_argument("--creature", action="append", default=[], help="Creature id; repeat to select several")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--badge", type=Path, default=DEFAULT_BADGE)
    parser.add_argument("--badge-scale", type=float, default=0.14)
    parser.add_argument("--badge-position", default="bottom-right")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--quality", default=DEFAULT_QUALITY)
    parser.add_argument("--size", default=DEFAULT_SIZE)
    parser.add_argument("--estimate-per-image", type=float, default=DEFAULT_ESTIMATE)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    roster = load_json(args.roster)
    creatures = validate_roster(roster)
    selected = select_creatures(creatures, args.creature)
    cost = estimate(selected, args.estimate_per_image)

    print(f"Roster: {roster.get('collection', args.roster.name)}")
    print(f"Model: {args.model} | quality={args.quality} | size={args.size}")
    for row in cost["creatures"]:
        print(f"  {row['id']}: {row['images']} images (~${row['estimate_usd']:.2f} planning estimate)")
    print(f"TOTAL: {cost['total_images']} images (~${cost['estimate_usd']:.2f} planning estimate)")

    if args.validate_only or args.dry_run:
        print("No API calls made.")
        return

    client = get_client()
    manifest = load_existing_manifest(args.manifest) if args.resume else {"creatures": {}}
    manifest.update({
        "schema_version": 2,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": args.model,
        "quality": args.quality,
        "size": args.size,
        "roster": str(args.roster),
        "aggregate_sheet": roster.get("aggregate_sheet", {}),
    })
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)

    for creature in selected:
        print(f"\n== {creature['id']} — {creature['name']} ==")
        run_creature(
            client,
            roster,
            creature,
            manifest,
            output_dir=args.output_dir,
            badge_path=args.badge,
            badge_scale=args.badge_scale,
            badge_position=args.badge_position,
            model=args.model,
            quality=args.quality,
            size=args.size,
            resume=args.resume,
        )
        args.manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"\nManifest written: {args.manifest}")


if __name__ == "__main__":
    main()
