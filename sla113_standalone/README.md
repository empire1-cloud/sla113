# SLA113 — Universal AI Game Studio Operator OS

## Architecture

SLA113 is the **sovereign root** — all universes (Empire1, Southern, Soulfire/Lyrica) are routers/modules under it.

```
sla113_standalone/
├── backend/
│   └── app/
│       ├── main.py                      # FastAPI entrypoint (all routers registered)
│       ├── core/
│       │   ├── config.py                # Pydantic Settings from .env
│       │   ├── database.py              # MongoDB Motor connection
│       │   └── sla113_constants.py      # Game types, job stages, compliance checks
│       ├── models/
│       │   └── schemas.py               # All Pydantic request/response models
│       ├── routers/
│       │   ├── sla113_admin.py          # Tenant CRUD (White Label Mint)
│       │   ├── sla113_billing.py        # Revenue Pipelines
│       │   ├── sla113_dashboard_context.py  # Stats, Game Types, Projects CRUD
│       │   ├── sla113_engine_dashboard.py   # Vision, Logic, Composer, Terminal
│       │   ├── sla113_factory.py        # Build Pipeline
│       │   ├── sla113_foundry.py        # Vision Smith (Gemini 3 Pro image gen)
│       │   ├── sla113_health.py         # Health/status
│       │   ├── sla113_orchestration.py  # Night Queue Worker, Jobs, Dependencies
│       │   ├── sla113_regulatory.py     # Compliance Engine
│       │   ├── sla113/
│       │   │   └── factory.py           # Deploy Engine
│       │   ├── empire1.py               # Empire1 universe (stub)
│       │   ├── southern.py              # Southern universe (stub)
│       │   └── soulfire.py              # Soulfire / Lyrica 3 Pro (stub)
│       ├── services/
│       │   ├── vision_engine.py         # Vision asset spec generation (LLM)
│       │   ├── logic_engine.py          # Game math generation (LLM)
│       │   └── composer_engine.py       # Game bundle composition (LLM)
│       └── vertexai/
│           └── music_client.py          # Vertex AI music (placeholder)
├── docker-compose.yml
└── README.md
```

## Quick Start

### Docker
```bash
cp backend/.env.example backend/.env
# Fill in EMERGENT_LLM_KEY and GEMINI_API_KEY
docker-compose up --build
```

### Local Development
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Fill in keys
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Core SLA113
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/sla113/health` | System status |
| GET | `/api/sla113/stats` | Platform statistics |
| GET | `/api/sla113/game-types` | List 16 supported game types |

### Projects
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/sla113/projects` | Create game project |
| GET | `/api/sla113/projects` | List all projects |
| GET | `/api/sla113/projects/{id}` | Get project details |
| DELETE | `/api/sla113/projects/{id}` | Delete project |

### Engines
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/sla113/vision/generate` | Generate asset specs (LLM) |
| POST | `/api/sla113/vision/generate-image` | Generate actual images (Gemini 3 Pro) |
| GET | `/api/sla113/vision/styles` | List styles & asset types |
| POST | `/api/sla113/logic/generate` | Generate game math/mechanics |
| POST | `/api/sla113/compose` | Compose game bundle |
| POST | `/api/sla113/terminal` | AI Terminal (Sovereign Overseer) |

### Night Queue (Orchestration)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/sla113/jobs` | Create job (with dependencies) |
| GET | `/api/sla113/jobs` | List jobs |
| GET | `/api/sla113/jobs/graph` | Dependency graph |
| POST | `/api/sla113/jobs/{id}/process` | Advance job one step |
| POST | `/api/sla113/jobs/{id}/link` | Add dependency |
| GET | `/api/sla113/worker/status` | Worker status |

### Build / Compliance / Deploy
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/sla113/builds` | Create build |
| POST | `/api/sla113/builds/{id}/advance` | Advance build |
| POST | `/api/sla113/compliance/check` | Run compliance check |
| POST | `/api/sla113/deploy` | Deploy build to CDN |
| POST | `/api/sla113/deploy/{id}/advance` | Advance deployment |

### Universes
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/empire1/status` | Empire1 status |
| GET | `/api/southern/status` | Southern status |
| GET | `/api/soulfire/status` | Soulfire/Lyrica status |

## Key Integrations

- **Emergent LLM Key** — Powers Logic Engine, Composer, Terminal (via `emergentintegrations`)
- **Gemini 3 Pro API** — Powers Vision Smith image generation (direct, no proxy)
- **Vertex AI** — Will power Audio Forge / Lyrica 3 Pro (placeholder)

## White-label / Standalone Usage

SLA113 is designed to run both as a sovereign standalone operator OS and as an integrated route inside the main hybrid app.

- Use `sla113_standalone/` when you want a fully isolated, white-label deployment.
- The standalone project includes its own backend at `sla113_standalone/backend` and a separate frontend project at `sla113_standalone/frontend`.
- Your existing internal SLA113 feature in the main repo remains intact and can continue to run at `/sla113/*` inside `frontend/src/sla113`.
- For white-label export, run `./sla113_standalone/split_repo.sh` to copy the standalone backend, frontend, and deployment files into a clean new repo.
- After export:
  1. edit `backend/.env` in the exported repo,
  2. use `docker-compose up --build` for the standalone service,
  3. or use `cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload`.

This means you can keep your current SLA113 integration in the main app while also building/deploying a separate white-label SLA113 experience.

## Environment Variables

| Variable | Required | Used By |
|----------|----------|---------|
| `MONGO_URL` | Yes | Database |
| `DB_NAME` | Yes | Database |
| `EMERGENT_LLM_KEY` | Yes | Logic, Composer, Terminal |
| `GEMINI_API_KEY` | Yes | Vision Smith |
| `CORS_ORIGINS` | No | CORS config |
