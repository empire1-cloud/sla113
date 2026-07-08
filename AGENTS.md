# AGENTS.md

## Cursor Cloud specific instructions

### Empire1 Ecosystem Overview

Empire1 is a multi-universe AI entertainment ecosystem built on a hybrid Operator OS (SLA113).

| Universe | Domain | Role |
|----------|--------|------|
| **E1 — Empire 1** | `empire1.cloud` | Creator SaaS dashboard — onboarding, universe selection, account management, billing, studio tools |
| **SL — SouthernLifestyle** | `southernlifestyle.org` | Brand root & identity — corporate identity, compliance, admin identity, brand gateway |
| **L3 — Lyrica 3** | `lyrica3.com` | Music universe — AI music creation, duet engine, emotional grammar, vocal logic, Lyrica 3 Pro |
| **UL — Universal** | `sluniversal.lyrica3.com` | Universe portal — registry, cross-universe identity, multi-universe routing |
| **SLA113 — Core OS** | `sla113.southernlifestyle.org` | Sovereign Operator OS — admin console, engine dashboard, factory + foundry, compliance, orchestration |
| **AR — Arcade** | `arcade.southernlifestyle.org` | Player-facing game portal — previews, dashboards, fish shooter + slots, frontline UI |

**This repo** deploys the SLA113 Operator OS backend + the Empire 1 frontend (which includes both the Empire 1 dashboard at `/` and the SLA113 admin at `/sla113`).

### Technical Stack
- **Backend**: FastAPI (Python 3.12) on port 8001 — 19 AI engines, auth, teams, billing, SLA113 game studio
- **Frontend**: React 19 (CRA + CRACO) on port 3000 — Empire 1 dashboard + SLA113 operator UI
- **Database**: MongoDB (required) — used by backend via Motor (async driver)

### Starting Services

1. **MongoDB**: `sudo mongod --dbpath /data/db --fork --logpath /var/log/mongod.log`
2. **Backend**: `cd backend && uvicorn server:app --reload --port 8001` (requires `MONGO_URL` and `DB_NAME` in `backend/.env`)
3. **Frontend**: `cd frontend && yarn start` (requires `REACT_APP_BACKEND_URL` in `frontend/.env`)

### Key Gotchas

- **`emergentintegrations` module**: The code imports from `emergentintegrations` but the pip package is removed. A local backup exists at `backend/emergentintegrations_local_backup/`. A symlink `backend/emergentintegrations -> emergentintegrations_local_backup` must exist for imports to work. The update script creates this automatically.
- **Backend `.env`**: Must contain at minimum `MONGO_URL=mongodb://localhost:27017` and `DB_NAME=hybrid_intelligence`. The backend will crash on startup without these.
- **Frontend `.env`**: Must contain `REACT_APP_BACKEND_URL=http://localhost:8001`. Without this, all API calls go to `undefined/api/...`.
- **CRACO**: The frontend uses `@craco/craco` instead of plain `react-scripts`. The `@` alias resolves to `src/`. Use `yarn start` / `yarn build` (which invoke craco via package.json scripts).
- **Frontend build vs dev**: `yarn build` (production) works cleanly. Dev mode (`yarn start`) enables a visual-edits babel plugin that can occasionally crash; restarting the dev server resolves it.
- **No frontend tests**: The frontend has no test files. `yarn test` exits with code 1 (no tests found).
- **Backend tests**: Run with `REACT_APP_BACKEND_URL=http://localhost:8001 pytest tests/` from `backend/`. Some tests make live HTTP requests to the running backend. ~214 pass, ~28 fail (mostly due to missing external API keys), ~40 error.

### Lint/Test/Build Commands
- **Backend lint**: `flake8 --max-line-length=120 --exclude=emergentintegrations_local_backup,emergentintegrations` (from `backend/`)
- **Backend tests**: `pytest tests/` (from `backend/`, with backend running)
- **Frontend build**: `yarn build` (from `frontend/`)
- **Frontend dev**: `yarn start` (from `frontend/`)

### SLA113 Operator OS (Core OS)

The SLA113 admin is a full operator dashboard accessible at `/sla113` in the frontend. It runs **outside** the Empire 1 auth wrapper (no login required to view the dashboard). Production domain: `sla113.southernlifestyle.org`.

- **Frontend entry**: `/sla113` → `SLA113App.jsx` → title screen (4s auto-advance) → `SLA113Page.jsx`
- **Backend router**: All endpoints under `/api/sla113/` in `backend/routers/sla113.py` (single large router)
- **Engines**: `backend/sla113/` — `vision_engine.py`, `logic_engine.py`, `composer_engine.py`, `audio_forge.py`, `fish_multiplayer.py`
- **Dashboard partitions**: Factory, Empire 1, Foundry, Vault, Tech — each with multiple tabs (Frontline, White Label Mint, Deploy Center, OS Builder, Vision Smith, Audio Forge, Build Pipeline, Compliance, Night Queue, Terminal, etc.)
- **29 game types** across 5 categories: arcade (10 types incl. fish shooting, battle royale, tactical FPS, COD warfare), casino (8 types incl. slots, video poker, pachinko, sportsbook), RPG (7 types incl. open world, dungeon crawler, cyberpunk, southern barrio), racing (1), hybrid/custom (3). Plus 8 audio middleware types (SFX, ambience, foley, music cues, stems, loops, TTS, voice routing) and 4 audio engines (FMOD, SonicForge, AudioKing, VoiceKing).
- **Universe registry**: 6 universes auto-registered on startup with live domains — accessible via `/api/sla113/universes`
- **Key endpoints**: `/api/sla113/tenants` (CRUD), `/api/sla113/projects` (CRUD), `/api/sla113/builds` (create/compile/download), `/api/sla113/deployments`, `/api/sla113/compliance`, `/api/sla113/fish/lobbies`, `/api/sla113/worker/status`, `/api/sla113/game-types` (full catalog)
- **WebSockets**: `/api/sla113/frontline/ws` (live metrics), `/api/sla113/fish/play/{lobby_id}` (multiplayer fish game)
- **Standalone variant**: `sla113_standalone/` has its own Docker Compose and split routers — not used when running the main monorepo

### Optional External API Keys
AI engine endpoints require `EMERGENT_LLM_KEY`; image generation requires `GEMINI_API_KEY`; billing requires `STRIPE_SECRET_KEY`. These are not needed for basic startup, auth, or structural testing.

### Production Deployment (Cloud Run)
All services deploy to **Google Cloud Run**. See `deployment/DEPLOYMENT_GUIDE.md` for full instructions.
- **Backend Dockerfile**: `Dockerfile` (repo root) → deploys as `sla113-api`
- **Frontend Dockerfile**: `frontend/Dockerfile` → deploys as `sla113-frontend`
- **Deploy script**: `bash deployment/deploy.sh` (builds, pushes, deploys both services)
- **Domain mapping**: `gcloud run domain-mappings create --service sla113-api --domain sla113.southernlifestyle.org`
- **DNS**: CNAME `sla113.southernlifestyle.org` → `ghs.googlehosted.com` (SSL auto-provisioned)
- **Checklist**: `deployment/LAUNCH_CHECKLIST.md`
