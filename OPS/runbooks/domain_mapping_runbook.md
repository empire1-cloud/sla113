# Domain Mapping Runbook

**Owner:** sla113  
**Last updated:** 2026-05-03

## Adding a New Domain

1. Update `SHARED/universe_registry.yaml` — add domain to the correct universe's `domains:` list
2. Update `DEPLOY_MAP.md` — add row to the domain table
3. Update `Empire-1/middleware.ts` — add hostname detection block for the new domain
4. Update `Empire-1/next.config.mjs` — add rewrite rule if needed
5. Add Cloud Run domain mapping:
   ```bash
   gcloud run domain-mappings create \
     --service <SERVICE_NAME> \
     --domain <NEW_DOMAIN> \
     --project disco-amphora-490606-n8 \
     --region us-central1
   ```
6. Add DNS CNAME record pointing to `ghs.googlehosted.com`
7. Open PR — tag with domain mapping change label
8. Post-deploy: verify with `curl -I https://<NEW_DOMAIN>`

## Known Issue — lyrica3.com Fallthrough Bug

**Root cause:** `middleware.ts` in Empire-1 had unresolved merge conflict markers. The stashed version was missing the lyrica3.com detection block entirely, causing lyrica3.com to fall through to the empire1 tenant and render Empire-1's homepage.

**Fix:** Commit `f4e1f24` on `shiestybizz113-cell/Empire-1` — merged correct middleware + next.config.mjs.

**Status:** Fix pushed. Cloud Run redeploy still needed to go live.
