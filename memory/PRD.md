# SLA113 — Universal AI Game Studio Operator OS

## Product Overview
SLA113 is the **sovereign root OS** for AI-powered game creation. All universes (Empire1, Southern, Soulfire/Lyrica 3 Pro) are routers/modules under SLA113.

## Architecture
- SLA113 = sovereign root (owns everything)
- Empire 1 = universe router under SLA113
- Southern = universe router under SLA113  
- Soulfire Ecosystem (ASW + El Coro + Sentinel + SL Universal) = single domain → Lyrica 3 Pro

## Completed Features
- [x] Vision Smith v2 (Gemini 3 Pro direct API, no watermarks)
- [x] Logic Engine (AI game math, RTP, paytables, RNG)
- [x] Composer Engine (game bundle assembly)
- [x] AI Terminal (Sovereign Overseer)
- [x] Night Queue (asyncio background worker + job dependencies)
- [x] Build Pipeline (simulated)
- [x] **Real Compliance Engine** — pulls actual RTP from Logic Engine, checks RNG/Paytable specs
- [x] Deploy Engine (simulated)
- [x] Sprite Cutter + Animation Preview
- [x] Boss Bestiary gallery
- [x] Cinematic splash screen
- [x] Revenue Pipeline Pulse
- [x] **Universe Registry** — auto-discovery, dynamic registration/deregistration, visual dashboard
- [x] **WebSocket Frontline** — real-time metrics via WebSocket (CPU, RAM, jobs, projects, revenue, universes)
- [x] SLA113 removed from Empire 1 nav (decontaminated)
- [x] Standalone SLA113 project export matching production layout

## Key Endpoints (50+)
- Universe Registry: `/api/sla113/universes`, `/register`, `/universes/{id}`
- Frontline: `/api/sla113/frontline/ws` (WebSocket), `/frontline/snapshot` (REST)
- Compliance: `/api/sla113/compliance/check` (real RTP verification)
- All CRUD for projects, jobs, tenants, pipelines, builds, deploys

## Backlog
- [ ] Wire Audio Forge to Vertex AI
- [ ] Upgrade Build/Deploy from simulated to real
- [ ] Refactor SLA113Page.jsx into sub-components
