# Aztec Abyss art pipeline

Production tooling for replacing SLA113's programmer art with an original Aztec-inspired cabinet skin.

## What this builds

- 12 animated fish species packed into the existing `aztec_fish_species_v2` SLA113 sheet contract
- Per-creature full animation sheets for Phaser or future PIXI state-aware animation
- Two separate boss sheets
- Empire-1 coin badge extraction from the source logo
- Six turret skins
- Underwater temple background
- Jade/obsidian HUD pieces
- Target-lock, net, projectile, and boss VFX assets
- Machine-readable manifests and ready-to-merge SLA113 sprite config JSON

## Install

```bash
python3 -m pip install -r firekirin-engine/art_pipeline/requirements.txt
```

## 1. Extract the Empire badge

```bash
python3 firekirin-engine/art_pipeline/extract_empire_badge.py \
  /path/to/empire1_logo.jpeg \
  --out ASSETS/shield_badge.png \
  --debug-mask output/badge-mask.png
```

The extractor isolates the largest compact gold component rather than taking a global gold bounding box, which prevents the wordmark from contaminating the coin crop.

## 2. Validate before spending

```bash
python3 firekirin-engine/art_pipeline/generate_sprites.py \
  --roster firekirin-engine/art_pipeline/aztec_roster.json \
  --validate-only

python3 firekirin-engine/art_pipeline/generate_static_art.py \
  --contract firekirin-engine/art_pipeline/aztec_static_assets.json \
  --dry-run
```

Cost output is a planning estimate only. Verify current OpenAI pricing and your project limits before generating.

## 3. Generate one hero creature first

```bash
export OPENAI_API_KEY='...'
export OPENAI_IMAGE_MODEL='gpt-image-1.5'

python3 firekirin-engine/art_pipeline/generate_sprites.py \
  --roster firekirin-engine/art_pipeline/aztec_roster.json \
  --creature ocelotl_jaguar_shark

python3 firekirin-engine/art_pipeline/pack_sprite_sheet.py \
  ocelotl_jaguar_shark \
  --install-dir backend/static/sprites
```

Inspect the hero fish at real game scale before generating the entire roster.

## 4. Generate and pack the full roster

```bash
python3 firekirin-engine/art_pipeline/generate_sprites.py \
  --roster firekirin-engine/art_pipeline/aztec_roster.json \
  --resume

python3 firekirin-engine/art_pipeline/pack_sprite_sheet.py \
  --all --aggregate \
  --install-dir backend/static/sprites
```

Important outputs:

```text
output/sheets/aztec_fish_species_v2.png
output/sheets/aztec_fish_species_v2.sla113.json
output/sheets/sla113_sprites.json
backend/static/sprites/aztec_fish_species_v2.png
```

The aggregate sheet uses these existing engine animation keys:

```text
gold_pair
blue_school
gold_school
blue_school_dense
gold_school_dense
silver_school
cyan_serpent
cursed_black
cursed_school
cyan_serpent_alt
treasure_fish
golden_puffer
```

This is intentional: the generated sheet can replace the current `aztec_fish_species_v2` asset without hand-writing frame arrays.

## 5. Generate the cabinet skin

```bash
python3 firekirin-engine/art_pipeline/generate_static_art.py \
  --contract firekirin-engine/art_pipeline/aztec_static_assets.json
```

Generate individual pieces during review:

```bash
python3 firekirin-engine/art_pipeline/generate_static_art.py \
  --asset aztec_abyss_background \
  --asset sun_cannon
```

## Fast command

```bash
bash firekirin-engine/art_pipeline/build_art_pipeline.sh
```

The default is validation-only. API generation requires:

```bash
bash firekirin-engine/art_pipeline/build_art_pipeline.sh --generate
```

## Design and safety rules

- All generated subjects are original Aztec-inspired fantasy designs, not copies of another cabinet game's characters or UI.
- The generation model, quality, and estimated cost are configurable; none are treated as permanent facts.
- Raw undecorated `_reference_*.png` files remain isolated from branded output frames so the corner badge cannot bleed into later edits.
- Packed animation indices are based on actual cell order, not assumed to equal potentially sparse manifest indices.
- Frames are alpha-trimmed, aspect-ratio preserved, and centered. They are never stretched into squares.
- Static and creature manifests record whether transparency was actually present.
