# ADR 0003 — Lyrica Surface Routing

**Status:** Accepted  
**Date:** 2026-05-03  
**Owner:** lyrica / sla113

## Context

Lyrica3 has three modes in one app: Sonance Pro (default), SL Universal (streaming), and Orchestrator (DAW bridge). Early implementations had separate repos per mode, causing drift and deployment conflicts. Additionally, `lyrica3.com` was incorrectly falling through to the Empire-1 homepage due to missing middleware tenant detection.

## Decision

Lyrica3 is a single deployed app (`lyrica3-frontend` Cloud Run service) with mode-based routing:
- `lyrica3.com` → Sonance Pro mode (default)
- `sluniversal.lyrica3.com` → SL Universal mode (`/universal` route)
- Orchestrator mode is a tab/panel within the same app, not a separate domain

The Next.js middleware (`middleware.ts`) is the single source of truth for tenant detection. The fix is in commit `f4e1f24` on `shiestybizz113-cell/Empire-1`.

SL Universal repo (`sl-universal`) remains a separate repo as the agent pipeline source of truth (vertex_agent_class, prompts, agents, lyrica_workers). Its Python backend is mirrored into `Lyrica3-pro/backend/`.

## Consequences

- Never deploy SL Universal as a separate frontend — it is a mode of Lyrica3
- Any new Lyrica domain must be added to both `middleware.ts` and `DEPLOY_MAP.md`
- Agent pipeline changes originate in `sl-universal` and are mirrored to `Lyrica3-pro/backend/`
