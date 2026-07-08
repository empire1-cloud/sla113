# SOULFIRE Ecosystem — Reference Architecture

Source: `/home/shiestybizz/soulfire-ecosystem/`
Deployed in: Lyrica3-pro (backend + soulfire_kernel/)

## Core Components

| Component | Description | Engine |
|-----------|-------------|--------|
| CCNA Cultural Firewall | Blocks culturally insensitive content, enforces sovereign identity | `canon_enforcer.py` |
| EPD Emotional Poetic Divergence | Ensures poetic/emotional depth in AI outputs | `canon_enforcer.py` |
| S2 Environmental Reconstruction | Context coherence, acoustic reconstruction | `soulfire_kernel/` |
| VICS Sovereign Minting | Sovereign identity markers, royalty routing | `empire1_ledger_service/` |
| Empire 1 Ledger | Smart contract royalty tracking | `backend/server.py` |

## Pipeline

```
User Request → SL Audio Master (Vertex AI) → The Beast → Audio Stems → Lyrica3 UI
                                  ↓
                        Soulfire Payload (JSON)
                          • LML (Lyric Markup Language)
                          • Acoustic primitives
                          • Mastering directives
                          • Vocal physics
                          • Cultural matrix
```

## Files

- `soulfire-ecosystem/` — Full Next.js + FastAPI deployment
- `Lyrica3-pro/backend/vertex_agents_config.py` — SL Audio Master agent config
- `Lyrica3-pro/backend/empire1_flip_engine.py` — Flip It Protocol engine
- `Lyrica3-pro/api/` — Duo-Soul FastAPI backend
- `Lyrica3-pro/soulfire_kernel/` — S2 Disruption Engine kernel
- `Lyrica3-pro/SOULFIRE_DEPLOYMENT.md` — Full deployment guide
- `Lyrica3-pro/frontend/src/components/studio/DuoSoulEngine.tsx` — React UI

## Key Concepts

- **Flip It Protocol**: S2 engine public workflow — upload → target genre → latent space transplantation → preview → render + royalty ledger
- **CCNA Ghostwriter Directive**: Cultural corpus + subtext for each track
- **VICS Steward**: Verified creator identity for royalty routing
- **Barrio Vault Fabric**: Royalty distribution network
