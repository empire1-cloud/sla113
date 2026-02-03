# Hybrid Intelligence Core - PRD

## Original Problem Statement
Build a "Hybrid Intelligence Core," a sophisticated multi-model AI pipeline composed of specialized, single-purpose engines. The system uses GPT-5.2, Claude Sonnet 4.5, and Gemini 3 Flash via the `emergentintegrations` library with a universal key for seamless LLM access.

## Project Overview
A comprehensive backend system featuring 19 specialized AI engines orchestrated by a Hybrid Intelligence Core. Each engine is a distinct service responsible for a specific AI task, exposed via modular API endpoints.

## Architecture Summary
```
                    ┌─────────────────────────────┐
                    │  HYBRID INTELLIGENCE CORE   │
                    │    (Master Orchestrator)    │
                    └─────────────┬───────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│   GPT-5.2     │       │Claude Sonnet  │       │Gemini 3 Flash │
│   (Code)      │       │ 4.5 (Strategy)│       │   (Quick)     │
└───────────────┘       └───────────────┘       └───────────────┘
                                  │
                    ┌─────────────┴───────────────┐
                    │    19 SPECIALIZED ENGINES   │
                    └─────────────────────────────┘
```

## What's Been Implemented

| Date | Feature | Status |
|------|---------|--------|
| 2026-01-03 | Integration playbook (HYBRID_AI_STACK_PLAYBOOK.md) | ✅ Done |
| 2026-01-03 | Hybrid Intelligence Core | ✅ Done |
| 2026-01-03 | Core engines (Strategy, Plan, Analysis, Opportunity, Evaluator, Pricing, Blueprint, Persona) | ✅ Done |
| 2026-01-03 | Infrastructure (Canon Enforcer, Drift Monitor, Error Handler, Routing Engine) | ✅ Done |
| 2026-01-03 | Anime Character Engine | ✅ Done |
| 2026-01-03 | Pipeline Composer Engine | ✅ Done |
| 2026-02-03 | **Router Refactoring** - Split 1450-line monolithic router into 16 modular files | ✅ Done |
| 2026-02-03 | Anime Lore Engine + API endpoints | ✅ Done |
| 2026-02-03 | Anime Story Engine + API endpoints | ✅ Done |
| 2026-02-03 | Art Direction Engine + API endpoints | ✅ Done |
| 2026-02-03 | **Universal Money Pipeline Engine** | ✅ Done |
| 2026-02-03 | Pipeline Composer updated with all 13 engines + 7 templates | ✅ Done |

## Engine Inventory (19 Total)

### Business & Strategy Engines
| Engine | Purpose | Default Model |
|--------|---------|---------------|
| Strategy Engine | High-level strategy generation | Claude |
| Plan Builder Engine | Tactical execution planning | GPT-5.2 |
| Analysis Engine | Deep SWOT analysis | Claude |
| Opportunity Mapper | Identify high-leverage opportunities | Claude |
| Evaluator Engine | Score and evaluate with criteria | Claude |
| Pricing Engine | Generate pricing structures | Claude |
| Blueprint Engine | System architecture blueprints | GPT-5.2 |
| Persona Engine | User/customer persona generation | Claude |
| **Money Pipeline Engine** | Complete monetization system | Claude |

### Creative Engines
| Engine | Purpose | Default Model |
|--------|---------|---------------|
| Anime Character Engine | Original anime character creation | Claude |
| Anime Lore Engine | World-building, mythology, factions | Claude |
| Anime Story Engine | Narrative structure, story arcs | Claude |
| Art Direction Engine | Visual direction for creative projects | Claude |

### Infrastructure Engines
| Engine | Purpose |
|--------|---------|
| Hybrid Intelligence Core | Master orchestrator |
| Routing Engine | Task classification → model selection |
| Pipeline Composer Engine | Multi-engine workflow orchestration |
| Canon Enforcer | Output normalization |
| Drift Monitor | Behavioral tracking |
| Error Handler | Structured errors |

## API Endpoints (77 Total)

### Core Endpoints
- `POST /api/core/execute` - Unified execution via Hybrid Core
- `GET /api/core/status` - Core system status
- `GET /api/health` - Pipeline health check (lists all 19 engines)

### Money Pipeline Endpoints
- `POST /api/money-pipeline` - Full monetization pipeline
- `POST /api/money-pipeline/quick` - Quick monetization
- `POST /api/money-pipeline/saas` - SaaS-specific pipeline
- `POST /api/money-pipeline/service` - Service business pipeline
- `POST /api/money-pipeline/ecommerce` - E-commerce pipeline
- `POST /api/money-pipeline/api` - API product pipeline

### Pipeline Composer Endpoints
- `POST /api/pipeline/compose` - Compose multi-engine pipeline
- `GET /api/pipeline/engines` - List all 13 chainable engines
- `GET /api/pipeline/templates` - List 7 pre-built templates

### Creative Endpoints
- `POST /api/anime/character` - Generate anime character
- `POST /api/anime/lore` - Generate world lore
- `POST /api/anime/story` - Generate story structure
- `POST /api/art-direction` - Generate art direction

## Pipeline Templates (7)

| Template | Engines Chain |
|----------|---------------|
| full_business_plan | strategy → analysis → opportunity → plan → pricing → evaluator |
| product_launch | persona → strategy → pricing → plan |
| startup_validation | analysis → persona → opportunity → evaluator |
| system_design | strategy → blueprint → plan → evaluator |
| **idea_to_money** | money_pipeline → persona → blueprint → evaluator |
| **anime_full_concept** | lore → story → character → character → art_direction |
| **saas_monetization** | money_pipeline → blueprint → plan |

## Code Architecture
```
/app/backend/
├── services/                    # 19 engine service files
│   ├── hybrid_core.py
│   ├── strategy_engine.py
│   ├── money_pipeline_engine.py # NEW
│   ├── anime_lore_engine.py
│   ├── anime_story_engine.py
│   ├── art_direction_engine.py
│   └── ... (13 more)
├── routers/
│   ├── engines/                 # 16 modular router files
│   │   ├── __init__.py
│   │   ├── core.py
│   │   ├── money_pipeline.py    # NEW
│   │   ├── anime_lore.py
│   │   ├── anime_story.py
│   │   ├── art_direction.py
│   │   └── ... (10 more)
│   └── strategy.py              # Legacy (kept for reference)
├── server.py
├── requirements.txt
└── .env
```

## Key Technical Details
- **API Key**: Emergent Universal Key (EMERGENT_LLM_KEY)
- **Library**: emergentintegrations
- **Models**: 
  - OpenAI: gpt-5.2
  - Anthropic: claude-sonnet-4-5-20250929
  - Google: gemini-3-flash-preview

## Next Tasks
1. Build frontend dashboard for testing engines
2. Add monitoring dashboard for drift detection
3. Implement model performance analytics
4. Add engine execution metrics/logging

## Backlog
- Frontend interface for testing the hybrid AI
- Real-time pipeline execution visualization
- Engine performance comparison dashboard
- Custom pipeline builder UI
