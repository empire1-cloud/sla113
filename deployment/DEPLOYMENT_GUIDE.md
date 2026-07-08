# Empire1 Ecosystem — Cloud Run Deployment Guide

## Tee Architecture — Domain Map

| Domain | Universe | Cloud Run Service |
|--------|----------|-------------------|
| `sla113.southernlifestyle.org` | SLA113 (Core OS) | `sla113-api` + `sla113-frontend` |
| `empire1.cloud` | E1 (Creator SaaS) | `empire1-api` (future) |
| `lyrica3.com` | L3 (Music Universe) | `lyrica3-api` (future) |
| `sluniversal.lyrica3.com` | UL (Meta-Router) | `universal-router` (future) |
| `arcade.southernlifestyle.org` | AR (Game Portal) | `arcade-frontend` (future) |
| `southernlifestyle.org` | SL (Brand Root) | static / DNS |

---

## Prerequisites

- **Google Cloud** project with billing enabled
- **gcloud CLI** installed and authenticated (`gcloud auth login`)
- **Docker** installed locally (for building images)
- **MongoDB Atlas** cluster with connection string
- **Domain DNS** access for `southernlifestyle.org` subdomains

### GCP APIs to Enable
```bash
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com
```

---

## Quick Deploy

```bash
# Set your GCP project
gcloud config set project YOUR_PROJECT_ID

# Export required env vars
export MONGO_URL="mongodb+srv://user:pass@cluster.mongodb.net/hybrid_intelligence?retryWrites=true&w=majority"
export DB_NAME="hybrid_intelligence"

# Optional API keys
export EMERGENT_LLM_KEY="your-key"
export GEMINI_API_KEY="your-key"
export STRIPE_SECRET_KEY="sk_live_..."

# Deploy
bash deployment/deploy.sh
```

---

## Step-by-Step

### 1. Create Artifact Registry

```bash
gcloud artifacts repositories create empire1 \
    --repository-format=docker \
    --location=us-central1 \
    --description="Empire1 container images"
```

### 2. Build & Push Backend Image

```bash
# From repo root
gcloud auth configure-docker us-central1-docker.pkg.dev --quiet
docker build -t us-central1-docker.pkg.dev/PROJECT/empire1/sla113-api:latest -f Dockerfile .
docker push us-central1-docker.pkg.dev/PROJECT/empire1/sla113-api:latest
```

### 3. Deploy Backend to Cloud Run

```bash
gcloud run deploy sla113-api \
    --image us-central1-docker.pkg.dev/PROJECT/empire1/sla113-api:latest \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --set-env-vars "MONGO_URL=...,DB_NAME=hybrid_intelligence"
```

### 4. Build & Push Frontend Image

```bash
docker build -t us-central1-docker.pkg.dev/PROJECT/empire1/sla113-frontend:latest \
    --build-arg REACT_APP_BACKEND_URL=https://sla113.southernlifestyle.org \
    -f frontend/Dockerfile frontend/
docker push us-central1-docker.pkg.dev/PROJECT/empire1/sla113-frontend:latest
```

### 5. Deploy Frontend to Cloud Run

```bash
gcloud run deploy sla113-frontend \
    --image us-central1-docker.pkg.dev/PROJECT/empire1/sla113-frontend:latest \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 256Mi
```

### 6. Map Custom Domains

```bash
# Backend API
gcloud run domain-mappings create \
    --service sla113-api \
    --domain sla113.southernlifestyle.org \
    --region us-central1

# Get the DNS target
gcloud run domain-mappings describe \
    --domain sla113.southernlifestyle.org \
    --region us-central1
```

Then add a CNAME record in your DNS:
```
sla113.southernlifestyle.org  →  ghs.googlehosted.com
```

Cloud Run auto-provisions SSL certificates once DNS propagates.

---

## Environment Variables

### Required
| Variable | Description |
|----------|-------------|
| `MONGO_URL` | MongoDB Atlas connection string |
| `DB_NAME` | Database name (default: `hybrid_intelligence`) |

### Auto-generated
| Variable | Description |
|----------|-------------|
| `JWT_SECRET_KEY` | Generated if not provided |
| `CORS_ORIGINS` | Set by deploy script to frontend domain |

### Optional
| Variable | Description |
|----------|-------------|
| `EMERGENT_LLM_KEY` | Powers AI engines (strategy, analysis, terminal) |
| `GEMINI_API_KEY` | Vision Smith image generation |
| `STRIPE_SECRET_KEY` | Subscription billing |
| `RESEND_API_KEY` | Transactional email |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | Google OAuth |
| `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET` | GitHub OAuth |

### Setting Secrets via Cloud Run

```bash
# Using --set-env-vars (simple)
gcloud run services update sla113-api --region us-central1 \
    --set-env-vars "STRIPE_SECRET_KEY=sk_live_..."

# Using Secret Manager (recommended for production)
echo -n "sk_live_..." | gcloud secrets create STRIPE_SECRET_KEY --data-file=-
gcloud run services update sla113-api --region us-central1 \
    --set-secrets "STRIPE_SECRET_KEY=STRIPE_SECRET_KEY:latest"
```

---

## OAuth Callback URLs

When setting up OAuth providers, use these callback URLs:

- **Google**: `https://sla113.southernlifestyle.org/api/auth/oauth/google/callback`
- **GitHub**: `https://sla113.southernlifestyle.org/api/auth/oauth/github/callback`
- **Stripe Webhook**: `https://sla113.southernlifestyle.org/api/billing/webhook`

---

## Verification

```bash
# Health check
curl https://sla113.southernlifestyle.org/api/health

# Universe registry (should show 6 universes)
curl https://sla113.southernlifestyle.org/api/sla113/universes

# Game types (should show 29)
curl https://sla113.southernlifestyle.org/api/sla113/game-types | python3 -c "import sys,json; print(json.load(sys.stdin)['total_types'])"
```

---

## Monitoring

```bash
# View logs
gcloud run services logs read sla113-api --region us-central1 --limit 50

# View metrics
gcloud run services describe sla113-api --region us-central1

# List revisions
gcloud run revisions list --service sla113-api --region us-central1
```

---

## Updating

```bash
# Rebuild and push new image
docker build -t us-central1-docker.pkg.dev/PROJECT/empire1/sla113-api:latest -f Dockerfile .
docker push us-central1-docker.pkg.dev/PROJECT/empire1/sla113-api:latest

# Cloud Run auto-deploys latest image, or force:
gcloud run deploy sla113-api \
    --image us-central1-docker.pkg.dev/PROJECT/empire1/sla113-api:latest \
    --region us-central1
```

---

## Future Services (Tee Architecture Expansion)

| Service | Domain | Notes |
|---------|--------|-------|
| `empire1-api` | `empire1.cloud` | Creator SaaS backend |
| `lyrica3-api` | `lyrica3.com` | Music/emotional engine backend |
| `arcade-frontend` | `arcade.southernlifestyle.org` | Player game portal |
| `universal-router` | `sluniversal.lyrica3.com` | Cross-universe routing |
