# SLA113 — Universal AI Game Studio

## Product Overview
SLA113 is a sovereign AI-powered game creation platform that generates complete game packages — from AAA titles (COD, GTA, Mortal Kombat style) to casino/arcade games — using AI engines for vision, logic, and composition. It sits alongside "Empire 1" (the existing Hybrid Intelligence Core SaaS) as its own domain page.

## Architecture
- **Frontend**: React + Tailwind CSS + lucide-react, isolated micro-frontend at `/sla113/*`
- **SLA113 has its own app shell** (`/app/frontend/src/sla113/`) — zero Empire 1 bleed, no shared AuthProvider, own CSS scope
- **Backend**: FastAPI, routes at `/api/sla113/*`
- **Database**: MongoDB (`sla113_projects`, `sla113_tenants`, `sla113_jobs`, `sla113_pipelines` collections)
- **AI**: Emergent LLM Key via `emergentintegrations` pip package (OpenAI GPT-4o-mini for terminal, GPT Image 1 for Vision Smith)

## Partitions (UI)
| Partition | Theme | Tabs |
|-----------|-------|------|
| FACTORY | Cyan (#00C8FF) | Frontline (live feed), White Label Mint |
| EMPIRE 1 | Indigo (#6366f1) | Mint Ledger, Revenue Pipelines |
| FOUNDRY | Gold (#D4AF37) | OS Builder, Vision Smith, Audio Forge |
| VAULT | Deep Red (#8B0000) | System Core, Night Queue |

## Supported Game Types (16)
### Casino/Arcade
- Fish Shooter, Slot Machine, Crash Game, Card Game

### AAA / Universal
- Open World (GTA Style), Tactical FPS (COD Style), Fighting Game (MK Style), Fantasy RPG, Survival Horror

### Action/Casual
- Platformer, Puzzle, Tower Defense, Endless Runner, Battle Royale, Racing, Sports

## AI Engines
1. **Vision Engine** (`/api/sla113/vision/generate`) — Generates sprite/asset specs
2. **Vision Smith Image Gen** (`/api/sla113/vision/generate-image`) — Generates actual game art via GPT Image 1
3. **Logic Engine** (`/api/sla113/logic/generate`) — Generates game math, mechanics, RTP, paytables
4. **Composer Engine** (`/api/sla113/compose`) — Assembles game bundles
5. **AI Terminal** (`/api/sla113/terminal`) — Sovereign Overseer with platform context + session persistence

## API Endpoints
- `GET /api/sla113/game-types` — List all 16 game types
- `GET /api/sla113/stats` — Platform stats
- `POST /api/sla113/projects` — Create game project
- `GET /api/sla113/projects` — List projects
- `GET /api/sla113/projects/{id}` — Get project
- `DELETE /api/sla113/projects/{id}` — Delete project
- `POST /api/sla113/vision/generate` — Generate visual asset specs
- `POST /api/sla113/vision/generate-image` — Generate real image via GPT Image 1
- `POST /api/sla113/logic/generate` — Generate game logic
- `POST /api/sla113/compose` — Compose game bundle
- `POST /api/sla113/terminal` — AI Terminal command
- `GET /api/sla113/tenants` — List tenants
- `POST /api/sla113/tenants` — Create tenant
- `DELETE /api/sla113/tenants/{id}` — Delete tenant
- `PUT /api/sla113/tenants/{id}/credits` — Update tenant credits
- `PUT /api/sla113/tenants/{id}/rtp` — Set tenant RTP mode
- `GET /api/sla113/jobs` — List jobs
- `POST /api/sla113/jobs` — Create job
- `PUT /api/sla113/jobs/{id}/progress` — Update job progress
- `POST /api/sla113/jobs/{id}/process` — Advance job (simulate)
- `DELETE /api/sla113/jobs/{id}` — Delete job
- `GET /api/sla113/pipelines` — List pipelines
- `POST /api/sla113/pipelines` — Create pipeline
- `PUT /api/sla113/pipelines/{id}/pulse` — Trigger pipeline heartbeat
- `DELETE /api/sla113/pipelines/{id}` — Delete pipeline

## What's Implemented (Apr 2026)
- [x] Full multi-partition UI (Factory, Empire 1, Foundry, Vault) — 12 tabs across 4 partitions
- [x] Backend CRUD for game projects
- [x] Backend CRUD for tenants, jobs, pipelines, builds, compliance, deployments
- [x] AI Vision Engine (real LLM calls)
- [x] AI Logic Engine (real LLM calls)
- [x] AI Composer Engine (real LLM calls)
- [x] AI Terminal — Sovereign Overseer (real GPT with platform context + session persistence)
- [x] Vision Smith — GPT Image 1 real image generation
- [x] **Sprite Cutter Tool** — Canvas-based sprite sheet slicing with grid overlay, cell selection, cut/download
- [x] **Sprite Animation Preview** — Frame-by-frame playback (play/pause, FPS control, forward/reverse/pingpong)
- [x] **Revenue Pipeline Pulse** — Individual + Pulse All triggers, real revenue generation ($50-500 per pulse)
- [x] **Build Pipeline** — Compile Engine with WebGL/APK/Both targets, 5-stage build process, optimization modes
- [x] **Compliance Engine** — Certification scans for GLI, MGA, UKGC, CURACAO jurisdictions with pass/fail results
- [x] **Deploy Engine** — CDN deployment (Cloudflare/AWS/GCP/Custom) with region selection, SSL, live URLs
- [x] **Night Queue Background Worker** — Auto-processes jobs through named stages every 3s, worker start/stop toggle, 10 game presets with unique stage sequences, frontend auto-polls
- [x] Critical Drift overlay
- [x] Daemon Uplink heartbeat
- [x] 16 game types (casino + AAA)
- [x] LLM integration (emergentintegrations pip package)
- [x] 6 seeded revenue pipelines
- [x] White Label Mint tenant creation
- [x] Night Queue job management

## Backlog
- [ ] Audio Forge — wire to real audio generation API (Vertex API later)
- [ ] Real-time Frontline via WebSocket

## Key Files
- `/app/frontend/src/sla113/SLA113App.jsx` — Standalone micro-frontend shell
- `/app/frontend/src/sla113/SLA113Page.jsx` — Main SLA113 UI (all partitions)
- `/app/frontend/src/sla113/SpriteCutter.jsx` — Canvas-based sprite slicing tool
- `/app/frontend/src/App.js` — Root router (splits traffic: /sla113 -> SLA113App, else -> Empire 1)
- `/app/backend/routers/sla113.py` — API router (all endpoints)
- `/app/backend/sla113/` — Engine modules (vision, logic, composer)
- `/app/backend/sla113/models.py` — Data models

## Credentials
- Test user (Empire 1): `newuser@example.com` / `NewPass123!`
- SLA113: No auth required
