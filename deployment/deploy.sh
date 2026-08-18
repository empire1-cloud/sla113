#!/bin/bash
# SLA113 backend deploy — Vercel
# Cloud Run deployment has been retired. This deploys the existing FastAPI
# backend to the canonical Vercel project.

set -euo pipefail

VERCEL_SCOPE="${VERCEL_SCOPE:-monieqs-projects}"
VERCEL_PROJECT="${VERCEL_PROJECT:-sla113}"
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

command -v vercel >/dev/null 2>&1 || {
  echo "ERROR: Vercel CLI is required (npm i -g vercel)." >&2
  exit 1
}

cd "$ROOT/backend"

echo "Linking SLA113 backend to Vercel project ${VERCEL_SCOPE}/${VERCEL_PROJECT}..."
vercel link --yes --project "$VERCEL_PROJECT" --scope "$VERCEL_SCOPE"

echo "Deploying SLA113 backend to Vercel production..."
vercel deploy --prod --yes

echo "SLA113 backend deployment submitted to Vercel."
echo "Health route: /api/health"
