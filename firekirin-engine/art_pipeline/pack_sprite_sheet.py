#!/usr/bin/env python3
"""Pack generated sprite frames into Phaser- and SLA113-ready sheets.

Outputs per creature:
  output/sheets/{id}.png
  output/sheets/{id}.phaser.js
  output/sheets/{id}.sla113.json
  output/sheets/{id}.packed-manifest.json

Also supports one legacy-compatible aggregate sheet keyed as
aztec_fish_species_v2, using each creature's engine_animation name so the
existing SLA113 PIXI engine can consume the roster without hand-authored frame
ranges.
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
from collections import OrderedDict
from pathlib import Path
from typing import Any

from PIL import Image

DEFAULT_MANIFEST = Path("output/manifest.json")
DEFAULT_OUTPUT = Path("output/sheets")
LOOP_STATES = {"idle", "swim", "walk", "hover", "run"}


def fail(message: str) -> "NoReturn":
    raise SystemExit(message)


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"Missing JSON file: {path}")
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON in {path}: {exc}")


def ordered_groups(frames: list[dict[str, Any]]) -> OrderedDict[str, list[int]]:
    groups: OrderedDict[str, list[int]] = OrderedDict()
    for packed_index, frame in enumerate(frames):
        state = frame.get("state")
        if not isinstance(state, str) or not state:
            fail(f"Packed frame {packed_index} has no state")
        groups.setdefault(state, []).append(packed_index)
    return groups


def validate_frames(creature_id: str, frames: list[dict[str, Any]]) -> None:
    if not frames:
        fail(f"{creature_id}: no frames in manifest")
    seen_source: set[int] = set()
    for position, frame in enumerate(frames):
        index = frame.get("index")
        if not isinstance(index, int):
            fail(f"{creature_id}: frame {position} has invalid index")
        if index in seen_source:
            fail(f"{creature_id}: duplicate source frame index {index}")
        seen_source.add(index)
        file_path = Path(frame.get("file", ""))
        if not file_path.exists():
            fail(f"{creature_id}: missing frame file {file_path}")
        if not frame.get("state"):
            fail(f"{creature_id}: frame {index} missing state")


def fit_to_cell(image: Image.Image, frame_size: int, padding_ratio: float) -> Image.Image:
    rgba = image.convert("RGBA")
    bbox = rgba.getchannel("A").getbbox()
    if not bbox:
        return Image.new("RGBA", (frame_size, frame_size), (0, 0, 0, 0))
    subject = rgba.crop(bbox)
    max_side = max(1, int(frame_size * (1 - 2 * padding_ratio)))
    scale = min(max_side / subject.width, max_side / subject.height)
    target = (
        max(1, round(subject.width * scale)),
        max(1, round(subject.height * scale)),
    )
    subject = subject.resize(target, Image.Resampling.LANCZOS)
    cell = Image.new("RGBA", (frame_size, frame_size), (0, 0, 0, 0))
    cell.alpha_composite(subject, ((frame_size - subject.width) // 2, (frame_size - subject.height) // 2))
    return cell


def make_sheet(frames: list[dict[str, Any]], frame_size: int, columns: int, padding_ratio: float) -> tuple[Image.Image, int, int]:
    columns = max(1, min(columns, len(frames)))
    rows = math.ceil(len(frames) / columns)
    sheet = Image.new("RGBA", (columns * frame_size, rows * frame_size), (0, 0, 0, 0))
    for packed_index, frame in enumerate(frames):
        image = Image.open(frame["file"]).convert("RGBA")
        cell = fit_to_cell(image, frame_size, padding_ratio)
        col, row = packed_index % columns, packed_index // columns
        sheet.alpha_composite(cell, (col * frame_size, row * frame_size))
    return sheet, columns, rows


def state_metadata(frames: list[dict[str, Any]], state: str) -> tuple[int, bool]:
    state_frames = [f for f in frames if f["state"] == state]
    frame_rate = int(state_frames[0].get("frame_rate", 8))
    loop = bool(state_frames[0].get("loop", state in LOOP_STATES))
    return frame_rate, loop


def phaser_snippet(creature_id: str, png_name: str, frame_size: int, groups: OrderedDict[str, list[int]], frames: list[dict[str, Any]], asset_prefix: str) -> str:
    url = f"{asset_prefix.rstrip('/')}/{png_name}" if asset_prefix else png_name
    lines = [
        "// Auto-generated. Packed indices are derived from the actual cell order.",
        "// preload():",
        f"this.load.spritesheet('{creature_id}', '{url}', {{ frameWidth: {frame_size}, frameHeight: {frame_size} }});",
        "",
        "// create():",
    ]
    for state, indices in groups.items():
        rate, loop = state_metadata(frames, state)
        index_list = json.dumps(indices)
        lines.append(
            "this.anims.create({ "
            f"key: '{creature_id}_{state}', "
            f"frames: this.anims.generateFrameNumbers('{creature_id}', {{ frames: {index_list} }}), "
            f"frameRate: {rate}, repeat: {-1 if loop else 0} "
            "});"
        )
    return "\n".join(lines) + "\n"


def sla113_config(engine_key: str, sprite_url: str, frame_size: int, columns: int, rows: int, total: int, animations: dict[str, list[int]]) -> dict[str, Any]:
    return {
        engine_key: {
            "sprite_url": sprite_url,
            "frame_width": frame_size,
            "frame_height": frame_size,
            "columns": columns,
            "rows": rows,
            "total_frames": total,
            "animations": animations,
        }
    }


def write_per_creature(
    creature_id: str,
    creature: dict[str, Any],
    *,
    output_dir: Path,
    frame_size: int | None,
    columns: int,
    padding_ratio: float,
    sprite_url_prefix: str,
    phaser_asset_prefix: str,
    install_dir: Path | None,
) -> dict[str, Any]:
    frames = creature["frames"]
    validate_frames(creature_id, frames)
    selected_size = frame_size or int(creature.get("frame_size", 256))
    sheet, actual_columns, rows = make_sheet(frames, selected_size, columns, padding_ratio)
    png_name = f"{creature_id}.png"
    png_path = output_dir / png_name
    sheet.save(png_path, optimize=True)

    groups = ordered_groups(frames)
    animations = dict(groups)
    engine_key = creature.get("engine_key") or creature_id
    sprite_url = f"{sprite_url_prefix.rstrip('/')}/{png_name}" if sprite_url_prefix else png_name
    config = sla113_config(engine_key, sprite_url, selected_size, actual_columns, rows, len(frames), animations)

    (output_dir / f"{creature_id}.phaser.js").write_text(
        phaser_snippet(creature_id, png_name, selected_size, groups, frames, phaser_asset_prefix),
        encoding="utf-8",
    )
    (output_dir / f"{creature_id}.sla113.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    packed_manifest = {
        "creature_id": creature_id,
        "engine_key": engine_key,
        "source_frame_indices": [f["index"] for f in frames],
        "packed_cells": [
            {"packed_index": i, "source_index": f["index"], "state": f["state"], "file": f["file"]}
            for i, f in enumerate(frames)
        ],
        "animations": animations,
        "frame_size": selected_size,
        "columns": actual_columns,
        "rows": rows,
    }
    (output_dir / f"{creature_id}.packed-manifest.json").write_text(json.dumps(packed_manifest, indent=2), encoding="utf-8")

    if install_dir:
        install_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(png_path, install_dir / png_name)

    print(f"packed {creature_id}: {len(frames)} frames -> {png_path} ({sheet.width}x{sheet.height})")
    return config


def aggregate_frames(manifest: dict[str, Any], preferred_states: list[str]) -> tuple[list[dict[str, Any]], dict[str, list[int]]]:
    packed: list[dict[str, Any]] = []
    animations: dict[str, list[int]] = OrderedDict()
    for creature_id, creature in manifest["creatures"].items():
        if not creature.get("aggregate"):
            continue
        animation_key = creature.get("engine_animation")
        if not animation_key:
            fail(f"{creature_id}: aggregate creature missing engine_animation")
        frames = creature.get("frames", [])
        validate_frames(creature_id, frames)
        selected: list[dict[str, Any]] = []
        for state in preferred_states:
            selected = [f for f in frames if f["state"] == state]
            if selected:
                break
        if not selected:
            selected = [frames[0]]
        indices: list[int] = []
        for frame in selected:
            indices.append(len(packed))
            packed.append({**frame, "creature_id": creature_id, "engine_animation": animation_key})
        animations[animation_key] = indices
    if not packed:
        fail("No aggregate=true creatures found in manifest")
    return packed, animations


def write_aggregate(
    manifest: dict[str, Any],
    *,
    output_dir: Path,
    frame_size: int | None,
    columns: int | None,
    padding_ratio: float,
    sprite_url_prefix: str,
    install_dir: Path | None,
) -> dict[str, Any]:
    cfg = manifest.get("aggregate_sheet") or {}
    engine_key = cfg.get("engine_key", "aztec_fish_species_v2")
    filename = cfg.get("filename", f"{engine_key}.png")
    selected_size = frame_size or int(cfg.get("frame_size", 256))
    selected_columns = columns or int(cfg.get("columns", 6))
    preferred_states = list(cfg.get("preferred_states", ["swim", "idle"]))
    frames, animations = aggregate_frames(manifest, preferred_states)
    sheet, actual_columns, rows = make_sheet(frames, selected_size, selected_columns, padding_ratio)
    png_path = output_dir / filename
    sheet.save(png_path, optimize=True)
    sprite_url = f"{sprite_url_prefix.rstrip('/')}/{filename}" if sprite_url_prefix else filename
    config = sla113_config(engine_key, sprite_url, selected_size, actual_columns, rows, len(frames), animations)
    (output_dir / f"{engine_key}.sla113.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    packed_manifest = {
        "engine_key": engine_key,
        "preferred_states": preferred_states,
        "packed_cells": [
            {
                "packed_index": i,
                "creature_id": f["creature_id"],
                "source_index": f["index"],
                "state": f["state"],
                "engine_animation": f["engine_animation"],
                "file": f["file"],
            }
            for i, f in enumerate(frames)
        ],
        "animations": animations,
        "frame_size": selected_size,
        "columns": actual_columns,
        "rows": rows,
    }
    (output_dir / f"{engine_key}.packed-manifest.json").write_text(json.dumps(packed_manifest, indent=2), encoding="utf-8")
    if install_dir:
        install_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(png_path, install_dir / filename)
    print(f"packed aggregate {engine_key}: {len(frames)} frames -> {png_path} ({sheet.width}x{sheet.height})")
    return config


def main() -> None:
    parser = argparse.ArgumentParser(description="Pack SLA113 sprite sheets")
    parser.add_argument("creature_id", nargs="?", help="Pack one creature; omit with --all or --aggregate")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--frame-size", type=int)
    parser.add_argument("--columns", type=int, default=6)
    parser.add_argument("--padding", type=float, default=0.06)
    parser.add_argument("--sprite-url-prefix", default="/static/sprites")
    parser.add_argument("--phaser-asset-prefix", default="assets")
    parser.add_argument("--install-dir", type=Path)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--aggregate", action="store_true")
    args = parser.parse_args()

    if not 0 <= args.padding < 0.45:
        fail("--padding must be between 0 and 0.45")
    manifest = load_json(args.manifest)
    creatures = manifest.get("creatures")
    if not isinstance(creatures, dict) or not creatures:
        fail("Manifest has no creatures")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    aggregate_config: dict[str, Any] = {}
    if args.creature_id:
        if args.creature_id not in creatures:
            fail(f"Unknown creature: {args.creature_id}")
        aggregate_config.update(write_per_creature(
            args.creature_id,
            creatures[args.creature_id],
            output_dir=args.output_dir,
            frame_size=args.frame_size,
            columns=args.columns,
            padding_ratio=args.padding,
            sprite_url_prefix=args.sprite_url_prefix,
            phaser_asset_prefix=args.phaser_asset_prefix,
            install_dir=args.install_dir,
        ))
    elif args.all:
        for creature_id, creature in creatures.items():
            aggregate_config.update(write_per_creature(
                creature_id,
                creature,
                output_dir=args.output_dir,
                frame_size=args.frame_size,
                columns=args.columns,
                padding_ratio=args.padding,
                sprite_url_prefix=args.sprite_url_prefix,
                phaser_asset_prefix=args.phaser_asset_prefix,
                install_dir=args.install_dir,
            ))
    elif not args.aggregate:
        fail("Provide creature_id, --all, or --aggregate")

    if args.aggregate:
        aggregate_config.update(write_aggregate(
            manifest,
            output_dir=args.output_dir,
            frame_size=args.frame_size,
            columns=args.columns,
            padding_ratio=args.padding,
            sprite_url_prefix=args.sprite_url_prefix,
            install_dir=args.install_dir,
        ))

    (args.output_dir / "sla113_sprites.json").write_text(json.dumps(aggregate_config, indent=2), encoding="utf-8")
    print(f"wrote {args.output_dir / 'sla113_sprites.json'}")


if __name__ == "__main__":
    main()
