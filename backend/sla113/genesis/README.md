# SLA113 Genesis Engine

Deterministic, no-LLM game generation for the SLA113 studio. One call runs:

`SPECIFIED → CALCULATED → VERIFIED → GENERATED → COMPOSED → PACKAGED → DESCRIBED`

| Endpoint | What it does |
|---|---|
| `GET  /api/sla113/genesis/status` | Engine info |
| `POST /api/sla113/genesis/verify` | Math only: exact RTP + seeded simulation for a `GameSpec` |
| `POST /api/sla113/genesis/generate` | Full pipeline; returns manifest, verification, artifact list |
| `GET  /api/sla113/genesis/jobs/{job_id}/download` | The packaged web build (zip) |

## Why it exists next to Logic / Composer

The existing `logic_engine.py` asks an LLM to write `calculated_rtp` and
`simulation_results`; those numbers are generated text, not computed. Genesis
computes RTP exactly from the paytable and hit weights, re-checks it with a
fixed-seed simulation, and ships a playable build that spawns and pays using
those same numbers. The LLM engines are untouched — this is an additional path.

## Evidence state

- **VERIFIED (in-process tests, `backend/tests/test_sla113_genesis.py`)**: exact RTP
  math, reproducibility, target-mismatch flagging, spec validation, every artifact
  written, zip contents, markup-injection guard, API contract, download path-safety.
- **VERIFIED (headless Chromium, once, by hand)**: playable build loads with no JS
  errors, sprites render, hits pay from the verified paytable.
- **BUILT, NOT LIVE-VERIFIED**: not yet exercised on the deployed Render backend.
- **NOT BUILT**: miss-rate modelling (RTP is per resolved target), game types other
  than `fish_shooter`, persisted jobs (workspaces live in a temp dir and do not
  survive a restart), real deployment (only a descriptor is written; `deployed: false`),
  art/audio beyond deterministic placeholders.
- **Not a regulatory certification.** Every artifact says so.

Ported from `hybrid-intelligence-core` PR #16, where it was first built in the wrong repo.
