#!/bin/bash
# Copy SLA113 secret values from Google Secret Manager into Vercel.
# Values are piped directly; they are never echoed or written to disk.

set -euo pipefail

VERCEL_SCOPE="${VERCEL_SCOPE:-monieqs-projects}"
VERCEL_PROJECT="${VERCEL_PROJECT:-sla113}"
VERCEL_ENV="${VERCEL_ENV:-production}"
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

command -v gcloud >/dev/null 2>&1 || {
  echo "ERROR: gcloud CLI is required and must be authenticated." >&2
  exit 1
}
command -v vercel >/dev/null 2>&1 || {
  echo "ERROR: Vercel CLI is required (npm i -g vercel)." >&2
  exit 1
}

SECRETS=(
  MONGO_URL
  DB_NAME
  JWT_SECRET_KEY
  SLA113_TOKEN_SECRET
  SLA113_OPERATOR_HANDLE
  SLA113_OPERATOR_PASSWORD
  CORS_ORIGINS
  FRONTEND_URL
  ANTHROPIC_API_KEY
  OPENAI_API_KEY
  GEMINI_API_KEY
  GOOGLE_API_KEY
  VERTEX_AI_KEY
  GITHUB_CLIENT_ID
  GITHUB_CLIENT_SECRET
  GOOGLE_CLIENT_ID
  GOOGLE_CLIENT_SECRET
  STRIPE_SECRET_KEY
  STRIPE_API_KEY
  STRIPE_WEBHOOK_SECRET
  STRIPE_PRO_PRICE_ID
  STRIPE_ENTERPRISE_PRICE_ID
  RESEND_API_KEY
  SENDER_EMAIL
  APP_ENV
  APP_VERSION
  DEBUG
  LOG_LEVEL
)

cd "$ROOT/backend"
vercel link --yes --project "$VERCEL_PROJECT" --scope "$VERCEL_SCOPE" >/dev/null

existing="$(vercel env ls "$VERCEL_ENV" 2>/dev/null || true)"

copied=0
skipped=0
missing=0

for key in "${SECRETS[@]}"; do
  if ! gcloud secrets describe "$key" >/dev/null 2>&1; then
    echo "missing in GCP: $key"
    missing=$((missing + 1))
    continue
  fi

  if printf '%s\n' "$existing" | grep -Eq "(^|[[:space:]])${key}([[:space:]]|$)"; then
    echo "already in Vercel: $key"
    skipped=$((skipped + 1))
    continue
  fi

  echo "copying: $key"
  gcloud secrets versions access latest --secret="$key" \
    | vercel env add "$key" "$VERCEL_ENV" --sensitive >/dev/null
  copied=$((copied + 1))
done

echo "Migration complete: copied=$copied existing=$skipped missing_in_gcp=$missing"
echo "No secret values were printed or written to the repository."
