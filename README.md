# SLA113 Creature Animation System

A character-agnostic Phaser 3 sprite/animation engine for a fish-shooter/arcade
game. Built to a defined atlas contract so **placeholder art today swaps for
real art later with zero code changes.**

## What this actually is

None of the 9 images you supplied (`soverignslam.png`, `xochitl.png`,
`ocula.png`, etc.) were true sprite sheets — they were single static
illustrations, promo mockups, or pose-reference sheets with inconsistent
frame sizes and no transparent backgrounds. This build does **not** repurpose
those images as animation frames. Instead it:

1. Defines the exact atlas contract real art must follow (`docs/ATLAS_CONTRACT.md`)
2. Generates procedurally-drawn placeholder sprite sheets that obey that
   contract exactly (`tools/pack_atlas.py`)
3. Builds the full Phaser 3 engine on top of that contract (`src/`) — state
   machine, animation auto-registration, boss health bar, cannon, projectiles,
   impact/coin FX
4. Verifies the engine logic against the real generated atlas JSON (`tools/test_logic.mjs`)

## Verification status — read this before trusting "it works"

**Verified (ran, with real output shown):**
- `tools/pack_atlas.py` runs and emits real PNG + JSON atlas pairs obeying
  the contract (`assets/atlases/*.png/json` — 8 demo creatures + 5 shared sheets)
- Contract enforcement actually refuses under-minimum frame counts (tested,
  not just documented — see `[ok]`/`[FAIL]` output in the build log)
- All 9 `src/*.js` modules pass `node --check` (syntax-valid ES modules)
- `tools/test_logic.mjs`: 14/14 logic tests pass against the **real**
  `AnimationBuilder` and `CombatEntity` modules and the **real** generated
  atlas JSON for every registered creature — covering frame-key
  parsing/ordering, missing-state handling, the state machine's actual
  transition rules (death is terminal, hit-during-attack queues instead of
  interrupting, enrage is sticky), and registry lookups (`listBossIds`,
  `listTreasureIds`)
- Atlas JSON structural validation: every creature has all 6 required states
  with contiguous 0..N frame indices, matching the naming contract regex

**NOT verified — could not test in this environment:**
- **No in-browser render check.** Puppeteer's Chromium download was blocked
  (network egress to `storage.googleapis.com` isn't in this sandbox's
  allowlist, and no system browser binary is present). The logic tests above
  prove the *state machine and atlas-parsing logic* are correct; they do
  **not** prove the game visually renders, that click/tap firing works, that
  physics collisions resolve correctly, or that there are no console errors
  on load. **Open `index.html` in a real browser yourself before treating
  this as production-ready** — that's the one step I could not close out here.
- No test of `CannonController`, `ProjectileManager`, `BossHealthBar`, or
  `FxManagers` in isolation — they depend on Phaser's real physics/tween/
  container systems closely enough that a mock would mostly be testing the
  mock, not the code. `DemoScene.js` wires them together in a way that should
  work based on code review, but "should work based on code review" is not
  the same claim as "verified."

## Creatures and features (this pass)

Added on top of the original 3-creature proof (gold_wolf, fire_jaguar,
aztec_wolf_boss), all as pure `CreatureRegistry` entries + generated atlas
pairs — no per-creature code:

- `obsidian_serpent`, `stone_turtle`, `eagle_warrior` — three more minions,
  each tuned differently (fast/fragile, slow/tanky, flyer) via existing
  registry fields (`baseHealth`, `baseSpeed`) plus a new `movement` field
  (`'drift' | 'weave' | 'flee'`) that `DemoScene` dispatches on.
- `tlaltecuhtli_boss` — a second boss. `DemoScene` now rotates through
  `listBossIds()` on kill instead of spawning one boss once.
- `jade_treasure_fish` — a new `role: 'treasure'`. Flees the cannon's aim
  point (`movement: 'flee'`), pays out a large multiplier-boosted coin bonus
  if killed in time, otherwise fades out and escapes.

Engine features, all in `DemoScene.js` unless noted:
- **Minion attacks** — minions now windup an `attack()` on a randomized
  timer too (previously only the boss did), self-terminating on death.
- **Boss rotation** — clearing a boss advances `this.wave` and spawns the
  next boss in `listBossIds()` after a short delay.
- **Wave scaling** — `_statsForWave()` scales health/speed upward per wave
  for every newly spawned minion/boss/treasure.
- **Combo multiplier** — kills within 1.5s of each other chain a combo
  (capped at x5), boosting coin payout and, at x3+, upgrading the cannon's
  shot type to `harpoon` via `CannonController`'s new `getProjectileType`
  hook and `ProjectileManager`'s new per-type speed/damage table.
- **Projectile variety** — `projectiles.json` now has a `harpoon` frame set
  (contract section 5 `projectile__<type>__<index>` naming, unchanged).
- **Score persistence** — total coins saved to `localStorage` on every
  payout and restored on load.

Verified the same way as the original build: `node --check` on every
`src/*.js` module, and `tools/test_logic.mjs` (14/14, including new checks
that every registered creature's atlas registers all 6 states, and that
`listBossIds`/`listTreasureIds` return what the new spawner logic expects).
**Not** browser-verified — same gap as before, see above.

## Running it

Needs a real browser (Puppeteer couldn't be used here — see above):

```bash
# regenerate placeholder atlases (optional — already generated)
python3 tools/pack_atlas.py --all-demo

# run logic tests
node tools/test_logic.mjs

# serve and open in a browser
python3 -m http.server 8000
# then open http://localhost:8000/index.html
```

Click/tap fires the cannon. Minions patrol and respawn after death. The boss
attacks every 3 seconds — watch it enrage (visual glow) once it drops below
35% health, and confirm a hit landing mid-attack-windup doesn't cancel the
attack animation (it should queue and play right after).

## File map

```
docs/ATLAS_CONTRACT.md      the spec — read this first
tools/pack_atlas.py         placeholder generator, enforces the contract
tools/test_logic.mjs        logic tests against real modules + real atlas JSON
assets/atlases/*.png,*.json generated placeholder sprite sheets + atlases
src/CreatureRegistry.js     single source of truth for creature stats/config
src/AnimationBuilder.js     atlas JSON -> Phaser animations, no per-creature code
src/CombatEntity.js         the idle/swim/attack/hit/enraged/death state machine
src/BossHealthBar.js        boss health bar from atlas UI pieces
src/CannonController.js     player aim + fire
src/ProjectileManager.js    pooled bullets + collision
src/FxManagers.js           impact spark + coin/multiplier pop
src/AssetLoader.js          preload wiring, one line per new creature
src/DemoScene.js            wires it all together, the runnable proof
index.html                  entry point, loads Phaser 3 + DemoScene
```

## Swapping in real art

Once you generate real per-frame art (Path A from our conversation):

1. Export frames obeying `docs/ATLAS_CONTRACT.md` sections 2–4 (same cell
   size per creature, transparent bg, bottom-center anchor, `<id>__<state>__<n>`
   naming)
2. Overwrite the matching `assets/atlases/<creature_id>.png` and `.json`
3. Nothing in `src/` changes. If cell size changes, update `frameWidth`/
   `frameHeight` in that creature's `CreatureRegistry.js` entry — that's the
   only code touch point.

## Adding a new creature

One entry in `src/CreatureRegistry.js` (`CREATURES.your_creature_id = {...}`)
plus a matching atlas pair. `AssetLoader.js`, `AnimationBuilder.js`,
`CombatEntity.js`, and `DemoScene.js` all read from the registry — none of
them hardcode a creature name, so nothing else needs to change.
