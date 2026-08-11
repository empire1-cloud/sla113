# SL Universal — Sub-Universe 7 (inside Lyrica3)

**Role:** Consumer streaming radio, remix economy, payout engine  
**Route:** sluniversal.lyrica3.com → /universal mode in Lyrica3 app  
**Agent Repo:** shiestybizz113-cell/sl-universal (source of truth for agent pipeline)

## What It Is

SL Universal is the public-facing streaming surface of Lyrica3. Pulse Stream radio, remix economy, direct payouts to creators. Powered by the same Lyrica3 app — it is a mode, not a separate deployment.

## Agent Pipeline Source of Truth

The `sl-universal` repo is the canonical source for:
- `vertex_agent_class.py`
- `agents/` (PFA, MMA, PDA specs)
- `prompts/` (AURA, EFL, ASE, ECHO, EFAD specs)
- `lyrica_workers/` (demucs, mma, pfa workers)
- `schemas/soulfire_payload.json`

These are mirrored into `Lyrica3-pro/backend/` for deployment. The sl-universal repo is never deployed as a standalone frontend.
