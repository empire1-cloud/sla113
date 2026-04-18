# SLA113 — Universal AI Game Studio Operator OS

## Product Overview
SLA113 is the **sovereign root OS** for AI-powered game creation. Cultural backbone: Aztec myth + Chicano SGV + IELA roots. Target: surpass FireKirin/Juwa.

## Game Engines (FireKirin/Juwa Tier)

### Fish Shooter Engine (fish_engine.py) — v6 FireKirin Surpass
- **4-Player Table Layout**: 2 top + 2 bottom turrets (P1 YOU bottom-left, P2 BOT bottom-right, P3 BOT top-left, P4 BOT top-right)
- Per-player balance chips in matching corners, ornate rotating turrets with gear-tooth bases
- 6 weapons: Cannon, Laser, Chain Lightning, Bomb, Auto, Railgun (continuous rapid-fire, hold-to-shoot)
- 12 fish species (8 tiers), 5 Bosses (Jaguar Warrior, Quetzalcoatl, Tezcatlipoca, **Wolf Sovereign**, **Wolf Huntress**)
- Boss spawn: 8s initial, 30s recurring interval
- Progressive jackpot bar (MINI/MINOR/MAJOR/GRAND cycling), net mechanics, bullet trails + muzzle flash, multi-kill combo text, coin scatter on kill
- Sprite loader: loads registered spritesheets from Sprite Registry, animates idle/walk/run; proxies external URLs to bypass CORS

### Video Slots Engine (slots_engine.py)
- 5x3, 20 paylines, 4 progressive jackpots, cascading wins, hold & spin, bonus wheel
- Custom symbol support (Southern Lifestyle theme)
- **BACKLOG**: Juwa-tier upgrade (metallic 3D frame, side bonus wheels, game lobby thumbnails)

### Sprite Asset Registry
- CRUD API for spritesheet registration with frame dimensions, grid layout, animation maps
- Supports: fish, boss, special, weapon, background, ui entity types
- Registered bosses: Jaguar Warrior, Quetzalcoatl Fireborn, Ocelotl Voidmane, Mictlantecuilti Bone Sovereign, Quetzalflare Prismwing, **Aztec Wolf Male**, **Aztec Wolf Female**
- Registered env/fish: Aztec Fish Species, Three Worlds Pyramid (background), Aztec Temple Guardians

## Architecture
```
/app/backend/sla113/
  ├── fish_engine.py        # FireKirin-tier fish shooter (4-player, sprite bosses)
  ├── slots_engine.py       # Juwa-tier video slots
  ├── fish_multiplayer.py   # WebSocket multiplayer
  ├── game_templates.py     # Template router (aliases: fish_shooter, fish_shooting, slot_machine, slots, video_slots)
  ├── audio_forge.py, vision_engine.py, logic_engine.py, composer_engine.py, models.py
/app/frontend/src/sla113/panels/
  ├── AudioForgePanel.jsx, FishMultiplayerPanel.jsx, SlotSymbolsPanel.jsx
  ├── SpriteRegistryPanel.jsx  # Sprite asset management UI
  ├── VaultAdminPanels.jsx
```

## Build → Deploy Pipeline
- `POST /api/sla113/builds` → creates build record
- `POST /api/sla113/builds/{id}/compile` → injects all registered sprites into `GAME_CONFIG.sprites`, generates HTML5/PixiJS bundle, zips
- `POST /api/sla113/deploy` → extracts zip to `/app/backend/static/deploys/{deploy_id}/`, served at `/api/sla113/live/{deploy_id}/index.html`

## Changelog
- **2026-02-18** — Fish Engine v6 verified: 4-player 2-top+2-bottom layout live. Wolf Sovereign (male) + Wolf Huntress (female) registered & wired as bosses. Female spritesheet frame 19 excluded (Gemini watermark). Template map bug fixed (`fish_shooter` alias).
- 2026-02-18 — Sprite Asset Registry + CORS proxy; Aztec Fish, Three Worlds background, 5 boss sprites uploaded
- Earlier — Vision Smith (Gemini 3 Pro), Audio Forge (Vertex AI / Web Audio), Deploy Engine inline iframe preview, panel extraction

## Backlog (priority)
- [ ] (P1) **Juwa-tier Slots upgrade** — metallic 3D reel frame, side bonus wheels, 4 live jackpot tiers, game lobby with thumbnails
- [ ] (P1) **Mobile touch controls** — pointer/touch events for fish + slots (tablet/arcade use)
- [ ] (P1) **Game lobby with card thumbnails** (Wolf Warriors, Aztec Serpent, etc.)
- [ ] (P1) **Sound system** — Web Audio / Howler integration into compiled HTML5 engines
- [ ] (P2) **Agent/distributor cashier system**
- [ ] (P2) **Three Worlds triptych background** — crop/map each panel to a quadrant instead of tiling
- [ ] (P2) **Exportable standalone Arcade player portal** for arcade.southernlifestyle.org Cloud Run
- [ ] (P3) **Refactor** massive string-injected JS templates into separate `.js.tpl` files

## Known Issues
- Triptych background tiles awkwardly (3 panels side-by-side); needs per-quadrant mapping
- Gemini generated assets contain watermark in bottom-right — must exclude final frames or crop in post
