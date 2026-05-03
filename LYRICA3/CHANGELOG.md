# LYRICA3 Changelog

## [Unreleased]

### Added
- Agent pipeline (AURA→EFL→ASE→ECHO→EFAD) merged from sl-universal into Lyrica3-pro backend
- `vertex_agent_class.py` (Vertex AI ADK) merged into Lyrica3-pro backend
- `empire1_flip_engine.py` (S2 Disruption Engine) merged from soulfire-ecosystem
- `mma_worker.py`, `pfa_worker.py` merged from sl-universal lyrica_workers
- `agents/` and `prompts/` directories (AURA, EFL, ASE, ECHO, EFAD, PFA, MMA, PDA specs) merged
- `schemas/soulfire_payload.json` canonical output schema merged
- Full canon directory scaffold in sla113 repo

### Fixed
- `middleware.ts` in Empire-1: lyrica3.com tenant detection was missing, causing fallthrough to Empire-1 homepage (commit f4e1f24)
- `next.config.mjs` in Empire-1: split foundry/backend API rewrites restored

### Pending
- Cloud Run redeploy of Empire-1 to activate middleware fix
- Orchestrator mode panel build-out in App.tsx
- Flip engine API endpoint wiring in server.py
