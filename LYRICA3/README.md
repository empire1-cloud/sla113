# LYRICA3 — Universe 1

**Role:** Creative Intelligence product surface  
**Owner:** lyrica / sla113  
**Domains:** lyrica3.com, www.lyrica3.com, api.lyrica3.com, sluniversal.lyrica3.com  
**Repo:** shiestybizz113-cell/Lyrica3-pro

## What It Is

Lyrica3 is the SLA-113 Empire's flagship music AI platform. Three modes in one app:

| Mode | Domain/Route | Sub-Universe |
|---|---|---|
| Sonance Pro | lyrica3.com (default) | U8 |
| SL Universal | sluniversal.lyrica3.com | U7 |
| Orchestrator (SL Audio Studio) | Tab within app | — |

## Architecture

- **Frontend:** Next.js / React (Emergent build), deployed to Cloud Run `lyrica3-frontend`
- **Backend:** FastAPI + Python, deployed to Cloud Run `lyrica3-backend`
- **Agent Pipeline:** AURA → EFL → ASE → ECHO → EFAD (Vertex AI ADK, Gemini 2.5 Pro)
- **Sub-agents:** PFA (vocal biometrics), MMA (MIDI/groove), PDA (texture/mastering)
- **Flip Engine:** `empire1_flip_engine.py` (S2 Disruption, latent space transplant)
- **Ledger:** CockroachDB micro-royalty ledger with territory multipliers

## Key Files (Lyrica3-pro repo)

- `frontend/src/App.tsx` — mode switcher (sonance / universal / orchestrator)
- `backend/server.py` — FastAPI main server
- `backend/vertex_agent_class.py` — Vertex AI ADK agent class (from sl-universal)
- `backend/empire1_flip_engine.py` — S2 Disruption Engine
- `backend/agents/` — AURA, EFL, ASE, ECHO, EFAD, PFA, MMA, PDA markdown specs
- `backend/schemas/soulfire_payload.json` — canonical output schema

## Sub-Universes

- `LYRICA3/SL_UNIVERSAL/` — U7 streaming engine, remix economy, payout engine
- `LYRICA3/SONANCE_PRO/` — U8 pro studio, mastering tools, subscription layer
