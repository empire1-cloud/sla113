# Rollback Runbook

**Owner:** sla113  
**Last updated:** 2026-05-03

## When to Roll Back

- Health check fails after deploy
- Login broken for any universe
- Wrong homepage rendering on any domain
- Royalty ledger writes failing

## Rollback via Cloud Run Revision

```bash
# List recent revisions
gcloud run revisions list \
  --service <SERVICE_NAME> \
  --project disco-amphora-490606-n8 \
  --region us-central1

# Route 100% traffic to a previous revision
gcloud run services update-traffic <SERVICE_NAME> \
  --project disco-amphora-490606-n8 \
  --region us-central1 \
  --to-revisions <REVISION_NAME>=100
```

## Rollback via Git

```bash
git revert <BAD_COMMIT_SHA>
git push origin main
# Then trigger redeploy per deploy_runbook.md
```

## Post-Rollback

- Log incident in `OPS/incidents/`
- Open postmortem in `OPS/postmortems/`
- Update ADR if architectural change caused the issue
