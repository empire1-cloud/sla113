# SLA113 Creature Atlas Contract

This is the spec every creature — placeholder or real art — must satisfy to drop into
the animation system with zero code changes. Treat this as canon: additive only,
never break the contract to fix one creature.

## 1. File pair per creature

Every creature ships as exactly two files, same basename:

```
assets/atlases/<creature_id>.png     (or .webp)
assets/atlases/<creature_id>.json    (Phaser 3 texture atlas, "TexturePacker JSON Hash" style)
```

`<creature_id>` is lowercase snake_case, e.g. `gold_wolf`, `fire_jaguar`, `aztec_wolf_god`.

## 2. Frame grid rules

- All frames for a single creature share **one fixed cell size** (`frameWidth` x `frameHeight`),
  defined per-creature in `CreatureRegistry` (see `src/CreatureRegistry.js`).
- Frames are packed left-to-right, top-to-bottom, no rotation, 2px padding between cells
  to prevent bleed.
- Background is transparent (alpha 0), not white or checkerboard.
- Anchor point is identical across every frame of a creature: **bottom-center** of the
  visual silhouette sits at a fixed pixel offset from the cell's bottom-center. This is
  what the pose-sheet references you uploaded (img 3, img 5) got wrong — poses drift
  left/right/up/down cell to cell, which causes jitter. The contract forbids that.
- Frame count per animation is flexible (4–12 typical) but every animation must have
  **at least 2 frames** — a single-frame "animation" is a static state, not an animation,
  and the state machine will warn (not silently accept it) if it detects one.

## 3. Required animation states (per creature)

| State      | Purpose                                  | Loop? | Min frames |
|------------|-------------------------------------------|-------|------------|
| `idle`     | resting / default                         | yes   | 2           |
| `swim`     | locomotion (swim for fish-shooter, run ok)| yes   | 4           |
| `attack`   | active attack windup + release            | no    | 4           |
| `hit`      | reaction to taking damage                 | no    | 2           |
| `enraged`  | idle variant once enrage threshold hit    | yes   | 2           |
| `death`    | terminal state, does not loop             | no    | 4           |

Anything below the min frame count is a contract violation — the packer tool
(`tools/pack_atlas.py`) refuses to emit a JSON atlas for a creature that fails this,
so a broken export can never silently ship.

## 4. JSON atlas shape (Phaser 3 "Texture Packer JSON Hash")

```json
{
  "frames": {
    "gold_wolf__idle__0": {
      "frame": { "x": 0, "y": 0, "w": 128, "h": 128 },
      "sourceSize": { "w": 128, "h": 128 },
      "spriteSourceSize": { "x": 0, "y": 0, "w": 128, "h": 128 }
    }
  },
  "meta": {
    "app": "SLA113 atlas contract v1",
    "image": "gold_wolf.png",
    "size": { "w": 1024, "h": 1024 },
    "scale": "1"
  }
}
```

Frame key naming is load-bearing: `<creature_id>__<state>__<index>`. The animation
builder (`src/AnimationBuilder.js`) parses this key to auto-register Phaser animations —
no per-creature animation code required, ever. This is what makes the system
character-agnostic: add a creature, follow the naming rule, done.

## 5. Non-creature atlas assets (shared, not per-creature)

Same JSON-atlas mechanism, one shared sheet each:

- `projectiles.png/json` — bullet/harpoon frames, keyed `projectile__<type>__<index>`
- `impacts.png/json` — hit-spark/explosion frames, keyed `impact__<type>__<index>`
- `coins.png/json` — coin spin + multiplier burst, keyed `coin__<type>__<index>`
- `cannon.png/json` — cannon idle/fire frames, keyed `cannon__<index>`
- `ui.png/json` — boss health-bar end caps, fill segment, frame chrome

## 6. Swapping placeholder art for real art

1. Real art is exported obeying sections 2–4 above (same `frameWidth`/`frameHeight`
   per creature as declared in `CreatureRegistry`, same key naming).
2. Drop the two files into `assets/atlases/`, overwriting the placeholder pair.
3. No code changes. `CreatureRegistry` entry stays the same unless the real art
   changes cell size, in which case update `frameWidth`/`frameHeight` there only.

This is the entire contract. If a future creature can't satisfy it, that's a signal
to extend the contract (additively) — not to special-case the loader.
