# Empire1 Ecosystem — Cloud Run Launch Checklist

## GCP Setup
- [ ] GCP project created with billing enabled
- [ ] `gcloud` CLI authenticated (`gcloud auth login`)
- [ ] APIs enabled: Cloud Run, Artifact Registry, Cloud Build
- [ ] Artifact Registry repo created (`empire1`)

## MongoDB Atlas
- [ ] Cluster created
- [ ] Database user created
- [ ] Network access: allow `0.0.0.0/0` (Cloud Run has dynamic IPs)
- [ ] Connection string ready

## DNS (Tee Architecture)
| Domain | Record | Value | Status |
|--------|--------|-------|--------|
| `sla113.southernlifestyle.org` | CNAME | `ghs.googlehosted.com` | [ ] |
| `arcade.southernlifestyle.org` | CNAME | `ghs.googlehosted.com` | [ ] (future) |
| `empire1.cloud` | CNAME | `ghs.googlehosted.com` | [ ] (future) |
| `sluniversal.lyrica3.com` | CNAME | `ghs.googlehosted.com` | [ ] (future) |

- [ ] DNS propagation complete (check: https://dnschecker.org)

## Deploy
- [ ] `MONGO_URL` exported
- [ ] `DB_NAME` exported
- [ ] `bash deployment/deploy.sh` completed
- [ ] Backend Cloud Run service running
- [ ] Frontend Cloud Run service running
- [ ] Custom domain mapped (`gcloud run domain-mappings create`)
- [ ] SSL certificate auto-provisioned by Cloud Run

## Verification
- [ ] `curl https://sla113.southernlifestyle.org/api/health` returns healthy
- [ ] `curl https://sla113.southernlifestyle.org/api/sla113/universes` shows 6 universes
- [ ] `curl https://sla113.southernlifestyle.org/api/sla113/game-types` shows 29 types
- [ ] Frontend loads at `https://sla113.southernlifestyle.org`
- [ ] SLA113 admin dashboard loads at `https://sla113.southernlifestyle.org/sla113`

## Auth
- [ ] Signup works
- [ ] Login works
- [ ] Google OAuth configured (optional)
- [ ] GitHub OAuth configured (optional)

## Optional Services
- [ ] `EMERGENT_LLM_KEY` set (AI engines)
- [ ] `GEMINI_API_KEY` set (Vision Smith)
- [ ] `STRIPE_SECRET_KEY` set (billing)
- [ ] `RESEND_API_KEY` set (email)
- [ ] Stripe webhook URL: `https://sla113.southernlifestyle.org/api/billing/webhook`

## Go Live
- [ ] All checks passed
- [ ] Monitoring configured (`gcloud run services logs read`)
- [ ] **LAUNCHED** 🚀
