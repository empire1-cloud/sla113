from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import extract_empire_badge as badge
import pack_sprite_sheet as pack


class PipelineTests(unittest.TestCase):
    def test_fit_to_cell_preserves_aspect_ratio(self):
        image = Image.new("RGBA", (400, 100), (0, 0, 0, 0))
        ImageDraw.Draw(image).rectangle((20, 20, 380, 80), fill=(255, 0, 0, 255))
        cell = pack.fit_to_cell(image, 256, 0.05)
        alpha_box = cell.getchannel("A").getbbox()
        self.assertIsNotNone(alpha_box)
        width = alpha_box[2] - alpha_box[0]
        height = alpha_box[3] - alpha_box[1]
        self.assertGreater(width / height, 4.5)

    def test_ordered_groups_use_packed_positions_not_source_indices(self):
        frames = [
            {"index": 10, "state": "idle"},
            {"index": 30, "state": "swim"},
            {"index": 50, "state": "idle"},
        ]
        groups = pack.ordered_groups(frames)
        self.assertEqual(groups["idle"], [0, 2])
        self.assertEqual(groups["swim"], [1])

    def test_badge_component_prefers_compact_coin_over_wordmark(self):
        image = Image.new("RGB", (800, 400), "black")
        draw = ImageDraw.Draw(image)
        draw.ellipse((40, 40, 340, 340), fill=(210, 160, 45))
        for x in range(400, 760, 55):
            draw.rectangle((x, 250, x + 35, 300), fill=(210, 160, 45))
        mask = badge.gold_mask(image, brightness=90, warm_delta=15)
        components = badge.connected_components(mask)
        selected = badge.choose_coin(components, image.size)
        x0, y0, x1, y1 = selected["bbox"]
        self.assertLess(x0, 100)
        self.assertGreater(x1, 300)
        self.assertLess(abs((x1 - x0) - (y1 - y0)), 30)

    def test_aggregate_uses_engine_animation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            frames = []
            for idx, state in enumerate(["idle", "swim", "swim"]):
                path = root / f"f{idx}.png"
                Image.new("RGBA", (32, 32), (255, 0, 0, 255)).save(path)
                frames.append({"index": idx, "state": state, "file": str(path)})
            manifest = {
                "creatures": {
                    "fish": {
                        "aggregate": True,
                        "engine_animation": "blue_school",
                        "frames": frames,
                    }
                }
            }
            packed, animations = pack.aggregate_frames(manifest, ["swim", "idle"])
            self.assertEqual(len(packed), 2)
            self.assertEqual(animations["blue_school"], [0, 1])


if __name__ == "__main__":
    unittest.main()
