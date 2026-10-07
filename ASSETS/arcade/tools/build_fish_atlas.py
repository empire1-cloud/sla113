#!/usr/bin/env python3
"""Build web-ready fish-table art from the owner's source images.

Source art lives in ASSETS/arcade/fish/source/ (owner originals, untouched).
Output goes to frontend/public/arcade/fish/: one atlas per boss (frames in a
horizontal strip with a feathered aura alpha), the gold burst FX, the Empire
coin spin (checkerboard keyed out), the background, and atlas.json that the
game reads. Re-run after replacing any source file:

    python3 ASSETS/arcade/tools/build_fish_atlas.py
"""
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / 'ASSETS/arcade/fish/source'
OUT = ROOT / 'frontend/public/arcade/fish'
FRAME = 256


def sheet_frames(path, cols=4, rows=4):
    im = Image.open(path).convert('RGB')
    fw, fh = im.width // cols, im.height // rows
    return [im.crop((c * fw, r * fh, (c + 1) * fw, (r + 1) * fh)) for r in range(rows) for c in range(cols)]


def aura_mask(size, box, feather):
    """Feathered ellipse: the boss shows through a soft glowing window."""
    mask = Image.new('L', size, 0)
    ImageDraw.Draw(mask).ellipse(box, fill=255)
    return mask.filter(ImageFilter.GaussianBlur(feather))


def build_strip(frames, box, feather, name):
    mask = aura_mask((FRAME, FRAME), box, feather)
    strip = Image.new('RGBA', (FRAME * len(frames), FRAME))
    for i, f in enumerate(frames):
        f = f.resize((FRAME, FRAME), Image.LANCZOS).convert('RGBA')
        f.putalpha(mask)
        strip.paste(f, (i * FRAME, 0))
    strip.save(OUT / name, 'WEBP', quality=88, method=6)
    return {'src': f'/arcade/fish/{name}', 'frameW': FRAME, 'frameH': FRAME, 'frames': len(frames)}


def build_coin(path, name, cell=160):
    """Key out the baked-in checkerboard by saturation (coin is gold, checker is grey)."""
    im = Image.open(path).convert('RGB')
    hsv = im.convert('HSV')
    sat = hsv.getchannel('S').point(lambda s: 255 if s > 70 else 0)
    sat = sat.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5))
    # Coins sit in two rows; find each one's horizontal span per row band.
    boxes = []
    for y0, y1 in ((0, im.height // 2), (im.height // 2, im.height)):
        band = sat.crop((0, y0, im.width, y1))
        cols = [any(band.getpixel((x, y)) for y in range(0, band.height, 4)) for x in range(band.width)]
        x = 0
        while x < len(cols):
            if cols[x]:
                start = x
                while x < len(cols) and cols[x]:
                    x += 1
                if x - start > 60:
                    sub = band.crop((start, 0, x, band.height))
                    bb = sub.getbbox()
                    boxes.append((start, y0 + bb[1], x, y0 + bb[3]))
            x += 1
    alpha = sat.filter(ImageFilter.GaussianBlur(1.2))
    strip = Image.new('RGBA', (cell * len(boxes), cell))
    for i, b in enumerate(boxes):
        coin = im.crop(b).convert('RGBA')
        coin.putalpha(alpha.crop(b))
        coin.thumbnail((cell - 8, cell - 8), Image.LANCZOS)
        strip.paste(coin, (i * cell + (cell - coin.width) // 2, (cell - coin.height) // 2), coin)
    strip.save(OUT / name, 'WEBP', quality=90, method=6)
    return {'src': f'/arcade/fish/{name}', 'frameW': cell, 'frameH': cell, 'frames': len(boxes)}


def build_burst(frames, name):
    """Gold burst on black: brightness becomes alpha so it adds light over any scene."""
    strip = Image.new('RGBA', (FRAME * len(frames), FRAME))
    edge = aura_mask((FRAME, FRAME), (10, 10, FRAME - 10, FRAME - 10), 18)
    for i, f in enumerate(frames):
        f = f.resize((FRAME, FRAME), Image.LANCZOS)
        lum = f.convert('L').point(lambda v: max(0, min(255, (v - 18) * 2)))
        f = f.convert('RGBA')
        f.putalpha(ImageChops.multiply(lum, edge))
        strip.paste(f, (i * FRAME, 0))
    strip.save(OUT / name, 'WEBP', quality=88, method=6)
    return {'src': f'/arcade/fish/{name}', 'frameW': FRAME, 'frameH': FRAME, 'frames': len(frames)}


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    bg = Image.open(SRC / 'background_mictlan.jpg').convert('RGB')
    bg.save(OUT / 'bg_mictlan.webp', 'WEBP', quality=86, method=6)

    rooster = sheet_frames(SRC / 'boss1_rooster_sheet_4x4.webp')
    xolotl = sheet_frames(SRC / 'boss2_xolotl_sheet_4x4.webp')

    # Frame picks: skip cells with the baked-in inset thumbnail or UI badges.
    rooster_idle = [2, 5, 9, 11, 12, 13]
    rooster_rage = [6, 10]
    xolotl_idle = [0, 1, 2, 3, 4, 5, 7, 8, 9, 11, 12, 13, 14]
    xolotl_attack = [6, 10]

    r_box = (14, 6, FRAME - 14, FRAME - 6)
    x_box = (40, 6, FRAME - 40, FRAME - 4)
    atlas = {
        'background': {'src': '/arcade/fish/bg_mictlan.webp', 'width': bg.width, 'height': bg.height},
        'bosses': {
            'rooster': {
                **build_strip([rooster[i] for i in rooster_idle + rooster_rage], r_box, 16, 'boss_rooster.webp'),
                'clips': {'idle': list(range(len(rooster_idle))),
                          'hit': [len(rooster_idle) + i for i in range(len(rooster_rage))]},
            },
            'xolotl': {
                **build_strip([xolotl[i] for i in xolotl_idle + xolotl_attack], x_box, 14, 'boss_xolotl.webp'),
                'clips': {'idle': list(range(len(xolotl_idle))),
                          'hit': [len(xolotl_idle) + i for i in range(len(xolotl_attack))]},
            },
        },
        'fx': {'goldBurst': build_burst([rooster[14], rooster[15]], 'fx_gold_burst.webp')},
        'coin': build_coin(SRC / 'empire_coin_spin.webp', 'coin_empire.webp'),
    }
    (OUT / 'atlas.json').write_text(json.dumps(atlas, indent=2) + '\n')
    print(json.dumps(atlas, indent=2))


if __name__ == '__main__':
    main()
