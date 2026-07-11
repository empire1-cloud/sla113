# Aztec Abyss — SLA113 vertical slice

An original virtual-credit fish-shooter prototype built beside the existing SLA113 generator. It does **not** replace or delete `backend/sla113/fish_engine.py`.

## Run

From the repository root:

```bash
python3 -m http.server 8080
```

Open:

```text
http://127.0.0.1:8080/firekirin-engine/aztec-abyss/
```

The page loads Phaser 3 from jsDelivr, so the browser needs network access the first time unless Phaser is vendored locally.

## Included gameplay

- Four-player table presentation with one human turret and three bot turrets
- Hold-to-fire mouse, touch, pen, keyboard, and auto-fire input
- Target lock with a rotating reticle
- Three weapons: Sun Bolt, Jade Net, and Obsidian Burst
- Five wave formations: line, wedge, arc, stair, and spiral
- Eight original Aztec-inspired aquatic species
- Three phased bosses with summoned adds
- Combo rewards, hit numbers, particle bursts, screen shake, slow/freeze effects
- Deterministic Sun Temple meter bonus
- Responsive, safe-area-aware HUD for desktop and mobile
- Virtual demo credits only; no cash-value or redemption behavior

## Controls

| Input | Action |
|---|---|
| Hold pointer / Space | Fire |
| Tap a creature / L | Lock target |
| A | Toggle auto-fire |
| 1 / 2 / 3 | Select weapon |
| Q / E | Decrease / increase power |
| F | Activate time relic |

## Production art hook

The vertical slice uses generated vector textures so it is immediately playable and legally clean. Replace those textures with owned transparent sprite sheets only after the species direction is approved.

Recommended production sheets:

- Standard fish: 256×256 frames, 8 swim frames, 2 hit frames, 4 capture/death frames
- Large fish: 384×384 frames with the same state layout
- Bosses: 512×512 frames, 6 idle/swim frames, 4 attack frames, 2 hit frames, 5 defeat frames
- Transparent PNG or lossless WebP
- Side-facing art designed to flip horizontally in-engine
- Consistent center point and padded silhouettes to prevent collision-box drift

## Promotion path

1. Approve the species and HUD direction.
2. Replace procedural textures with owned sprite sheets.
3. Port the target-lock, formation director, boss-phase, and HUD systems into `backend/sla113/fish_engine.py`.
4. Fix the existing asset-key drift by accepting both `aztec_fish_species` and `aztec_fish_species_v2` during migration.
5. Move credits, shot validation, outcomes, and progression to an authoritative backend before any production economy is considered.
