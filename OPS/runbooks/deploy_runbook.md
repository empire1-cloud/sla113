# Deploy Runbook

**Owner:** sla113  
**Last updated:** 2026-05-03

## Pre-Deploy Checklist

- [ ] `SHARED/universe_registry.yaml` is current
- [ ] `DEPLOY_MAP.md` matches intended domain routing
- [ ] All required ENV vars present in Cloud Run service (see INFRA/env_templates/)
- [ ] Tests pass in target repo
- [ ] Release receipt created in `RELEASES/` if shipping a track

## Deploy Order (always in this order)

1. `lyrica3-backend` (Cloud Run — GCP project disco-amphora-490606-n8)
2. `lyrica3-frontend` (Cloud Run)
3. `empire1-backend` (Cloud Run)
4. `empire1-frontend` (Cloud Run)

## Trigger Cloud Run Redeploy (manual)

```bash
gcloud run deploy <SERVICE_NAME> \
  --project disco-amphora-490606-n8 \
  --region us-central1 \
  --image gcr.io/disco-amphora-490606-n8/<SERVICE_NAME>:latest
```

Or trigger via Cloud Build:
```bash
gcloud builds submit --config cloudbuild.frontend.yaml \
  --project disco-amphora-490606-n8
```

## Post-Deploy Verification

```bash
curl https://lyrica3.com/api/health
curl https://empire1.cloud/api/health
# Check middleware routing:
curl -I https://lyrica3.com   # Should return Lyrica homepage, not Empire homepage
curl -I https://sluniversal.lyrica3.com  # Should return SL Universal mode
```

## Rollback

See `OPS/runbooks/rollback_runbook.md`
