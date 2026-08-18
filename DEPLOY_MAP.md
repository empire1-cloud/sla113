# Deploy Map — SLA-113 Empire (Source of Truth)

> Hosting source of truth: Vercel. Cloud Run is retired for SLA113 deployment.

## Domain → Logical Service → Universe

| Domain | Logical Service | Universe | Purpose | Owner |
|---|---|---|---|---|
| lyrica3.com | lyrica3-frontend | LYRICA3 (U1) | Sonance Pro studio — default mode | lyrica |
| www.lyrica3.com | lyrica3-frontend | LYRICA3 (U1) | Lyrica alias | lyrica |
| sluniversal.lyrica3.com | lyrica3-frontend | LYRICA3 (U1) | SL Universal Pulse Stream — /universal mode | lyrica |
| api.lyrica3.com | lyrica3-backend | LYRICA3 (U1) | Lyrica API / Auth | sla113 |
| empire1.cloud | empire1-frontend | EMPIREONE (U4) | Empire public app | empire1 |
| api.empire1.cloud | empire1-backend | EMPIREONE (U4) | Empire API | empire1 |
| southernlifestyle.org | empire1-frontend | SOUTHERN (U3) | Southern public home | southern |
| www.southernlifestyle.org | empire1-frontend | SOUTHERN (U3) | Southern alias | southern |
| arcade.southernlifestyle.org | empire1-frontend | SOUTHERN (U3) | Arcade surface | southern |
| sla113.southernlifestyle.org | sla113 | SLA113 (U0) | SLA113 operator entry | sla113 |

## SLA113 Hosting

- Platform: Vercel
- Project: `sla113`
- Backend root: `backend/`
- Health route: `/api/health`
- Cloud Run deployment script: retired
- GCP Secret Manager: migration source only until values are copied to Vercel Environment Variables

## Required Environment Variables

| Variable | Required | Notes |
|---|---|---|
| MONGO_URL | yes | MongoDB connection |
| DB_NAME | yes | SLA113 database name |
| JWT_SECRET_KEY | yes | Auth token signing key |
| CORS_ORIGINS | yes | Allowed frontend origins |
| FRONTEND_URL | yes | SLA113 frontend origin |
| EMERGENT_LLM_KEY | no | Optional legacy/provider path; not required for Vercel build |

Provider, OAuth, Stripe, email, and operator secrets belong in Vercel Environment Variables. Secret values must never be committed.

## Release Gates

- [ ] Vercel build resolves public dependencies successfully
- [ ] Backend health check passes (`/api/health` → 200)
- [ ] Required secrets exist in Vercel production environment
- [ ] Login endpoint returns token for expected auth mode
- [ ] Domain mappings remain correct
- [ ] If music release: checksums + `release_receipt.json` present in `RELEASES/`

## Change Control

Domain changes still require a PR and registry update. Hosting changes must update this file, `SHARED/universe_registry.yaml`, and a verification note under `OPS/incidents/`.
