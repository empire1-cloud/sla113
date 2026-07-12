#!/usr/bin/env python3
"""
pack_atlas.py — SLA113 placeholder atlas generator.

Generates procedurally-drawn, CLEARLY-LABELED placeholder sprite sheets and
their matching Phaser 3 JSON atlas, obeying docs/ATLAS_CONTRACT.md exactly.

This is not disguised as real art. Every frame is drawn with primitive shapes
(circles, polygons, rects) so nobody mistakes it for a finished asset. Its only
job is to prove the animation system end-to-end so real art can drop into the
exact same slots later with zero code changes.

Usage:
    python3 pack_atlas.py --creature gold_wolf --color1 "#1a1a1a" --color2 "#c9a227"
    python3 pack_atlas.py --shared          # generates projectiles/impacts/coins/cannon/ui
    python3 pack_atlas.py --all-demo        # generates 3 demo creatures + all shared sheets

Refuses to emit a JSON atlas for any creature/state that doesn't meet the
contract's minimum frame counts — see CONTRACT_MIN_FRAMES below.
"""

import argparse
import json
import math
import os

from PIL import Image, ImageDraw

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "atlases")

# Mirrors docs/ATLAS_CONTRACT.md section 3 — the contract is enforced here, not just documented.
CONTRACT_MIN_FRAMES = {
    "idle": 2,
    "swim": 4,
    "attack": 4,
    "hit": 2,
    "enraged": 2,
    "death": 4,
}

CONTRACT_LOOP = {
    "idle": True,
    "swim": True,
    "attack": False,
    "hit": False,
    "enraged": True,
    "death": False,
}

CELL = 128       # frameWidth == frameHeight for every creature (contract section 2)
PADDING = 2
COLS = 6         # sheet layout width in cells; height grows as needed


def hex_to_rgba(h, alpha=255):
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (r, g, b, alpha)


def draw_creature_frame(draw, cx, cy, state, frame_idx, total_frames, color1, color2):
    """
    Draws one placeholder creature frame centered at (cx, cy) — a body blob +
    a direction/limb indicator so animation phase is visually readable, not
    just a static circle every frame. Anchor = bottom-center of the cell,
    per contract section 2.
    """
    t = frame_idx / max(total_frames - 1, 1)  # 0..1 phase through the animation
    base_r = 34

    if state == "idle":
        bob = int(3 * math.sin(t * 2 * math.pi))
        body_cy = cy + bob
        draw.ellipse([cx - base_r, body_cy - base_r, cx + base_r, body_cy + base_r], fill=color1, outline=color2, width=3)
        eye_y = body_cy - 8
        draw.ellipse([cx - 6, eye_y - 4, cx + 6, eye_y + 4], fill=color2)

    elif state == "swim":
        wag = int(14 * math.sin(t * 2 * math.pi))
        body_cy = cy
        draw.ellipse([cx - base_r, body_cy - base_r + 4, cx + base_r, body_cy + base_r - 4], fill=color1, outline=color2, width=3)
        tail_x = cx - base_r - 6
        draw.polygon([(tail_x, body_cy - 12 + wag), (tail_x - 18, body_cy + wag), (tail_x, body_cy + 12 + wag)], fill=color2)
        draw.ellipse([cx - 6, body_cy - 12, cx + 6, body_cy - 4], fill=color2)

    elif state == "attack":
        lunge = int(20 * math.sin(min(t, 0.5) * math.pi))  # forward then hold
        body_cx = cx + lunge
        draw.ellipse([body_cx - base_r, cy - base_r, body_cx + base_r, cy + base_r], fill=color1, outline=color2, width=4)
        if t > 0.4:
            spike_len = 10 + int(20 * min((t - 0.4) / 0.6, 1))
            draw.polygon(
                [(body_cx + base_r, cy - 10), (body_cx + base_r + spike_len, cy), (body_cx + base_r, cy + 10)],
                fill=color2,
            )

    elif state == "hit":
        shake = int(8 * math.sin(t * 4 * math.pi))
        flash = color2 if frame_idx % 2 == 0 else color1
        draw.ellipse([cx - base_r + shake, cy - base_r, cx + base_r + shake, cy + base_r], fill=flash, outline=(255, 60, 60, 255), width=4)

    elif state == "enraged":
        pulse = int(6 * abs(math.sin(t * 2 * math.pi)))
        glow_r = base_r + pulse
        draw.ellipse([cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r], outline=(255, 80, 40, 200), width=5)
        draw.ellipse([cx - base_r, cy - base_r, cx + base_r, cy + base_r], fill=color1, outline=(255, 120, 40, 255), width=3)
        draw.ellipse([cx - 7, cy - 9, cx + 7, cy + 5], fill=(255, 80, 40, 255))

    elif state == "death":
        shrink = 1.0 - 0.6 * t
        fade_alpha = int(255 * (1.0 - t))
        r = int(base_r * shrink)
        rot = t * 35
        fill = (color1[0], color1[1], color1[2], fade_alpha)
        outline = (color2[0], color2[1], color2[2], fade_alpha)
        offset_y = int(18 * t)
        draw.ellipse([cx - r, cy - r + offset_y, cx + r, cy + r + offset_y], fill=fill, outline=outline, width=3)


def draw_fx_frame(draw, cx, cy, kind, sub, frame_idx, total_frames):
    t = frame_idx / max(total_frames - 1, 1)

    if kind == "projectile":
        if sub == "harpoon":
            length = 30
            draw.line([cx - length, cy, cx + length, cy], fill=hex_to_rgba("#8a5a2a"), width=6)
            draw.polygon(
                [(cx + length, cy - 10), (cx + length + 14, cy), (cx + length, cy + 10)],
                fill=hex_to_rgba("#e0392b"),
            )
        else:
            r = 10
            trail_alpha = 255
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=hex_to_rgba("#66d9ff", trail_alpha))
            draw.ellipse([cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4], outline=hex_to_rgba("#ffffff", 180), width=2)

    elif kind == "impact":
        r = int(6 + 34 * t)
        alpha = int(255 * (1 - t))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=hex_to_rgba("#ffdd55", alpha), width=4)
        for i in range(6):
            ang = i * (2 * math.pi / 6) + t * 2
            x2 = cx + math.cos(ang) * r
            y2 = cy + math.sin(ang) * r
            draw.line([cx, cy, x2, y2], fill=hex_to_rgba("#ff8844", alpha), width=3)

    elif kind == "coin":
        squash = abs(math.cos(t * 2 * math.pi))
        w = 26
        h = int(26 * max(squash, 0.15))
        draw.ellipse([cx - w, cy - h, cx + w, cy + h], fill=hex_to_rgba("#ffcc33"), outline=hex_to_rgba("#7a5210"), width=3)

    elif kind == "cannon":
        recoil = -6 if frame_idx == total_frames - 1 else 0
        draw.rectangle([cx - 14, cy - 40 + recoil, cx + 14, cy + 20], fill=hex_to_rgba("#3a3a3a"), outline=hex_to_rgba("#c9a227"), width=3)
        draw.ellipse([cx - 18, cy + 10, cx + 18, cy + 40], fill=hex_to_rgba("#222222"), outline=hex_to_rgba("#c9a227"), width=3)
        if frame_idx == total_frames - 1:
            draw.polygon([(cx - 10, cy - 40), (cx, cy - 60), (cx + 10, cy - 40)], fill=hex_to_rgba("#ffaa33"))


def pack_creature(creature_id, color1_hex, color2_hex, frame_counts=None):
    frame_counts = frame_counts or {
        "idle": 4, "swim": 6, "attack": 5, "hit": 2, "enraged": 4, "death": 6,
    }

    # Enforce contract minimums (docs/ATLAS_CONTRACT.md section 3) — refuse, don't clamp silently.
    violations = [
        f"{state}: {n} < min {CONTRACT_MIN_FRAMES[state]}"
        for state, n in frame_counts.items()
        if n < CONTRACT_MIN_FRAMES[state]
    ]
    if violations:
        raise ValueError(f"[{creature_id}] Contract violation, refusing to emit atlas:\n  " + "\n  ".join(violations))

    color1 = hex_to_rgba(color1_hex)
    color2 = hex_to_rgba(color2_hex)

    states = ["idle", "swim", "attack", "hit", "enraged", "death"]
    all_frame_keys = []
    for state in states:
        for i in range(frame_counts[state]):
            all_frame_keys.append((state, i, frame_counts[state]))

    total_frames = len(all_frame_keys)
    rows = math.ceil(total_frames / COLS)
    sheet_w = COLS * (CELL + PADDING) + PADDING
    sheet_h = rows * (CELL + PADDING) + PADDING

    sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))
    atlas_frames = {}

    for idx, (state, frame_idx, total_in_state) in enumerate(all_frame_keys):
        col = idx % COLS
        row = idx // COLS
        x = PADDING + col * (CELL + PADDING)
        y = PADDING + row * (CELL + PADDING)

        cell_img = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
        d = ImageDraw.Draw(cell_img)
        # Anchor: bottom-center sits at fixed offset (contract section 2) —
        # every state draws around the same (cx, cy) reference point.
        cx, cy = CELL // 2, CELL - 40
        draw_creature_frame(d, cx, cy, state, frame_idx, total_in_state, color1, color2)

        sheet.paste(cell_img, (x, y), cell_img)

        key = f"{creature_id}__{state}__{frame_idx}"
        atlas_frames[key] = {
            "frame": {"x": x, "y": y, "w": CELL, "h": CELL},
            "sourceSize": {"w": CELL, "h": CELL},
            "spriteSourceSize": {"x": 0, "y": 0, "w": CELL, "h": CELL},
        }

    os.makedirs(OUT_DIR, exist_ok=True)
    png_path = os.path.join(OUT_DIR, f"{creature_id}.png")
    json_path = os.path.join(OUT_DIR, f"{creature_id}.json")
    sheet.save(png_path)

    atlas = {
        "frames": atlas_frames,
        "meta": {
            "app": "SLA113 atlas contract v1 (PLACEHOLDER — procedurally generated, not final art)",
            "image": f"{creature_id}.png",
            "size": {"w": sheet_w, "h": sheet_h},
            "scale": "1",
        },
    }
    with open(json_path, "w") as f:
        json.dump(atlas, f, indent=2)

    print(f"[ok] {creature_id}: {total_frames} frames -> {png_path} ({sheet_w}x{sheet_h}) + {json_path}")
    return png_path, json_path


def pack_shared_fx():
    specs = [
        ("projectiles", "projectile", {"bolt": 3, "harpoon": 4}),
        ("impacts", "impact", {"spark": 5}),
        ("coins", "coin", {"spin": 8, "burst": 6}),
        ("cannon", "cannon", {"fire": 4}),
    ]
    for sheet_name, kind, subtypes in specs:
        all_keys = []
        for sub, count in subtypes.items():
            for i in range(count):
                all_keys.append((sub, i, count))

        total = len(all_keys)
        rows = math.ceil(total / COLS)
        sheet_w = COLS * (CELL + PADDING) + PADDING
        sheet_h = rows * (CELL + PADDING) + PADDING
        sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))
        atlas_frames = {}

        for idx, (sub, frame_idx, total_in_sub) in enumerate(all_keys):
            col = idx % COLS
            row = idx // COLS
            x = PADDING + col * (CELL + PADDING)
            y = PADDING + row * (CELL + PADDING)
            cell_img = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
            d = ImageDraw.Draw(cell_img)
            draw_fx_frame(d, CELL // 2, CELL // 2, kind, sub, frame_idx, total_in_sub)
            sheet.paste(cell_img, (x, y), cell_img)

            key = f"{kind}__{sub}__{frame_idx}"
            atlas_frames[key] = {
                "frame": {"x": x, "y": y, "w": CELL, "h": CELL},
                "sourceSize": {"w": CELL, "h": CELL},
                "spriteSourceSize": {"x": 0, "y": 0, "w": CELL, "h": CELL},
            }

        os.makedirs(OUT_DIR, exist_ok=True)
        png_path = os.path.join(OUT_DIR, f"{sheet_name}.png")
        json_path = os.path.join(OUT_DIR, f"{sheet_name}.json")
        sheet.save(png_path)
        atlas = {
            "frames": atlas_frames,
            "meta": {
                "app": "SLA113 atlas contract v1 (PLACEHOLDER — procedurally generated, not final art)",
                "image": f"{sheet_name}.png",
                "size": {"w": sheet_w, "h": sheet_h},
                "scale": "1",
            },
        }
        with open(json_path, "w") as f:
            json.dump(atlas, f, indent=2)
        print(f"[ok] {sheet_name}: {total} frames -> {png_path} ({sheet_w}x{sheet_h}) + {json_path}")


def pack_ui():
    """Boss health-bar pieces: left cap, fill segment (tileable), right cap, frame chrome corner."""
    w, h = 160, 32
    sheet = Image.new("RGBA", (COLS * (CELL + PADDING) + PADDING, CELL + PADDING * 2), (0, 0, 0, 0))
    atlas_frames = {}
    pieces = ["healthbar_left_cap", "healthbar_fill", "healthbar_right_cap", "healthbar_bg", "frame_corner"]

    for idx, piece in enumerate(pieces):
        col = idx % COLS
        x = PADDING + col * (CELL + PADDING)
        y = PADDING
        cell_img = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
        d = ImageDraw.Draw(cell_img)

        if piece == "healthbar_left_cap":
            d.pieslice([10, 40, 60, 90], 90, 270, fill=hex_to_rgba("#c9a227"))
        elif piece == "healthbar_fill":
            d.rectangle([0, 50, 128, 78], fill=hex_to_rgba("#e0392b"))
        elif piece == "healthbar_right_cap":
            d.pieslice([68, 40, 118, 90], 270, 90, fill=hex_to_rgba("#c9a227"))
        elif piece == "healthbar_bg":
            d.rounded_rectangle([4, 46, 124, 82], radius=14, fill=hex_to_rgba("#050505"), outline=hex_to_rgba("#c9a227"), width=3)
        elif piece == "frame_corner":
            d.arc([20, 20, 108, 108], 180, 270, fill=hex_to_rgba("#007AFF"), width=6)

        sheet.paste(cell_img, (x, y), cell_img)
        atlas_frames[f"ui__{piece}"] = {
            "frame": {"x": x, "y": y, "w": CELL, "h": CELL},
            "sourceSize": {"w": CELL, "h": CELL},
            "spriteSourceSize": {"x": 0, "y": 0, "w": CELL, "h": CELL},
        }

    os.makedirs(OUT_DIR, exist_ok=True)
    png_path = os.path.join(OUT_DIR, "ui.png")
    json_path = os.path.join(OUT_DIR, "ui.json")
    sheet.save(png_path)
    atlas = {
        "frames": atlas_frames,
        "meta": {
            "app": "SLA113 atlas contract v1 (PLACEHOLDER — procedurally generated, not final art)",
            "image": "ui.png",
            "size": {"w": sheet.width, "h": sheet.height},
            "scale": "1",
        },
    }
    with open(json_path, "w") as f:
        json.dump(atlas, f, indent=2)
    print(f"[ok] ui: {len(pieces)} pieces -> {png_path} + {json_path}")


DEMO_CREATURES = [
    ("gold_wolf", "#1a1a1a", "#c9a227"),
    ("fire_jaguar", "#3a1a0a", "#ff7a1a"),
    ("aztec_wolf_boss", "#0a1a1f", "#22d9c9"),
    ("obsidian_serpent", "#0a0a0a", "#7a2fd1"),
    ("stone_turtle", "#3a3a2a", "#8a9a6a"),
    ("eagle_warrior", "#5a2a0a", "#f2c14e"),
    ("tlaltecuhtli_boss", "#1a0a1a", "#e0392b"),
    ("jade_treasure_fish", "#0a3a2a", "#33ffcc"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--creature", type=str, help="creature_id to generate")
    ap.add_argument("--color1", type=str, default="#1a1a1a")
    ap.add_argument("--color2", type=str, default="#c9a227")
    ap.add_argument("--shared", action="store_true", help="generate shared FX + UI sheets")
    ap.add_argument("--all-demo", action="store_true", help="generate 3 demo creatures + shared + ui")
    args = ap.parse_args()

    if args.all_demo:
        for cid, c1, c2 in DEMO_CREATURES:
            pack_creature(cid, c1, c2)
        pack_shared_fx()
        pack_ui()
    elif args.creature:
        pack_creature(args.creature, args.color1, args.color2)
    elif args.shared:
        pack_shared_fx()
        pack_ui()
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
