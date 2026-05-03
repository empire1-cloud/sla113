# Deploy Map — SLA-113 Empire (Source of Truth)

> Any change to this file requires: PR note + updated `SHARED/universe_registry.yaml` + post-change verification log.

## Domain → Service → Universe

| Domain | Cloud Run Service | Universe | Purpose | Owner |
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
| sla113.southernlifestyle.org | empire1-frontend | SLA113 (U0) | SLA113 operator entry | sla113 |

## Required Environment Variables

| Variable | Required | Notes |
|---|---|---|
| BACKEND_URL | yes | Lyrica backend URL |
| SLA113_BACKEND_URL | yes | SLA113 control plane URL |
| ARCADE_EXTERNAL_URL | no | Temporary arcade redirect |
| MONGO_URL | yes | CockroachDB / MongoDB connection |
| JWT_SECRET | yes | Auth token signing key |
| EMERGENT_LLM_KEY | yes | Gemini / Vertex AI key |

## Release Gates (must pass before status = published)

- [ ] Backend health check passes (`/api/health` → 200)
- [ ] Login endpoint returns token for expected auth mode
- [ ] Domain mappings match this table exactly
- [ ] Lyrica and Empire surfaces render correct host-specific home
- [ ] If music release: checksums + `release_receipt.json` present in `RELEASES/`
- [ ] `SHARED/universe_registry.yaml` version bumped

## Change Control

Any change to domain mapping requires:
1. PR with description of change
2. Updated `SHARED/universe_registry.yaml`
3. Updated this file
4. Post-change verification output logged in `OPS/incidents/` or PR comments
