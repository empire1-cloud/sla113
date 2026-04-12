# SLA113 — Universal AI Game Studio Operator OS

## Product Overview
SLA113 is the **sovereign root OS** for AI-powered game creation. All universes are routers under SLA113.

## Game Type Taxonomy (29 types, 5 categories + Audio Middleware)
- **Arcade & Action** (10): Arcade Classic, Fish Shooting, Battle Royale, Tactical FPS, COD Warfare, Platformer, Fighting, Puzzle, Adventure, Open World
- **Casino & Gambling** (8): Slot Machine, Video Poker, Casino Suite, Pachinko, Lottery, Bingo, Sportsbook, Card Games
- **RPG & Narrative** (7): Open World RPG, Dungeon Crawler, Fantasy RPG, Cyberpunk, Horror, Southern Barrio, Sandbox
- **Racing & Simulation** (1): Racing Sim
- **Hybrid & Custom** (3): Hybrid Mix, Generic Game Asset, Custom Partner Games
- **Audio Middleware** (8): SFX, Ambience, Foley, Music Cues, Stems, Loops, TTS, Voice Routing
- **Audio Engines**: FMOD, SonicForge, AudioKing, VoiceKing

## Completed Features
- [x] Vision Smith v2 (Gemini 3 Pro, no watermarks)
- [x] Logic Engine (RTP, RNG, paytable, mechanics)
- [x] Composer Engine (game bundle assembly)
- [x] AI Terminal (Sovereign Overseer)
- [x] Night Queue (asyncio background worker + dependencies)
- [x] Build Pipeline — Real HTML5/PixiJS compilation + downloadable ZIP bundles
- [x] Real Compliance Engine + Auto-Certify
- [x] Deploy Engine (simulated CDN push)
- [x] Sprite Cutter + Animation Preview
- [x] Boss Bestiary
- [x] Universe Registry (auto-discovery, interactive cards)
- [x] WebSocket Frontline (real-time metrics)
- [x] Full 29-type game taxonomy with categorized dropdowns
- [x] Standalone project export (sla113_standalone.zip)
- [x] Audio Forge Engine — Real AI-enhanced DSP via GPT-4o-mini with physical modeling, waveform viz, FMOD event paths
- [x] Admin Control Vault — ArtTech Nexus Generator (8 pipeline archetypes + OS Module Functional Map)
- [x] Admin Control Vault — Matrix Parameters (5 engine configs + FModel Utility Status + Compilation Readiness)

## Backlog
- [ ] Upgrade Deploy Engine from simulated to real CDN pushes for HTML5 bundles (P2)
- [ ] Refactor SLA113Page.jsx into sub-components (Foundry, Vault, Factory, Empire) (P3)
- [ ] Audio Forge — wire actual Vertex AI sound generation once SDK supports audio output (P2)
- [ ] Build Pipeline — APK compilation path (P3)

## Architecture
```
/app
├── backend/
│   ├── routers/sla113.py         # SLA113 router (~2000 lines)
│   ├── sla113/
│   │   ├── models.py             # Pydantic models + game taxonomy
│   │   ├── vision_engine.py      # Gemini 3 Pro image gen
│   │   ├── logic_engine.py       # Game math/RTP generation
│   │   ├── composer_engine.py    # Bundle composition
│   │   └── audio_forge.py        # NEW: Audio asset generation with AI DSP
│   └── server.py                 # FastAPI + WebSocket mounts
├── frontend/src/sla113/
│   ├── SLA113Page.jsx            # Main dashboard (~2300 lines)
│   ├── FrontlinePanel.jsx        # WebSocket real-time panel
│   ├── SpriteCutter.jsx          # Sprite sheet cutter
│   └── DependencyGraph.jsx       # Job dependency visualization
```

## Key Integrations
- **OpenAI GPT-4o-mini** — Emergent LLM Key (AI Terminal + Audio DSP enhancement)
- **Gemini 3 Pro** — User GEMINI_API_KEY (Vision Smith, no watermarks)
- **Vertex AI** — User VERTEX_AI_KEY stored (Audio Forge credential ready)
