#!/bin/bash
# ============================================
# Empire1 Ecosystem — Cloud Run Deployment
# ============================================
# Deploys SLA113 backend API + frontend to Google Cloud Run
#
# Prerequisites:
#   - gcloud CLI authenticated (gcloud auth login)
#   - GCP project set (gcloud config set project YOUR_PROJECT)
#   - Artifact Registry repo created
#   - MongoDB Atlas connection string ready
#
# Usage: bash deployment/deploy.sh
# ============================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ─── Configuration ───
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
REGION="us-central1"
REPO="empire1"

# Service names
BACKEND_SERVICE="sla113-api"
FRONTEND_SERVICE="sla113-frontend"

# Domains (Tee Architecture)
BACKEND_DOMAIN="sla113.southernlifestyle.org"
FRONTEND_DOMAIN="sla113.southernlifestyle.org"

# Image tags
BACKEND_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${BACKEND_SERVICE}"
FRONTEND_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${FRONTEND_SERVICE}"

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Empire1 Ecosystem — Cloud Run Deploy${NC}"
echo -e "${GREEN}============================================${NC}"
echo -e "${BLUE}Project: ${PROJECT_ID}${NC}"
echo -e "${BLUE}Region:  ${REGION}${NC}"
echo ""

# ─── Preflight checks ───
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}ERROR: No GCP project set. Run: gcloud config set project YOUR_PROJECT${NC}"
    exit 1
fi

if [ -z "$MONGO_URL" ]; then
    echo -e "${RED}ERROR: MONGO_URL not set. Export it before running this script.${NC}"
    echo "  export MONGO_URL='mongodb+srv://...'"
    exit 1
fi

if [ -z "$DB_NAME" ]; then
    export DB_NAME="hybrid_intelligence"
fi

# ─── Ensure Artifact Registry repo exists ───
echo -e "${YELLOW}[1/6] Ensuring Artifact Registry repo...${NC}"
gcloud artifacts repositories describe "$REPO" --location="$REGION" 2>/dev/null || \
    gcloud artifacts repositories create "$REPO" --repository-format=docker --location="$REGION" --description="Empire1 container images"
echo -e "${GREEN}✓ Artifact Registry ready${NC}"

# ─── Configure Docker auth ───
echo -e "${YELLOW}[2/6] Configuring Docker auth...${NC}"
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet
echo -e "${GREEN}✓ Docker auth configured${NC}"

# ─── Build & push backend ───
echo -e "${YELLOW}[3/6] Building backend image...${NC}"
docker build -t "${BACKEND_IMAGE}:latest" -f Dockerfile .
docker push "${BACKEND_IMAGE}:latest"
echo -e "${GREEN}✓ Backend image pushed${NC}"

# ─── Build & push frontend ───
echo -e "${YELLOW}[4/6] Building frontend image...${NC}"
docker build -t "${FRONTEND_IMAGE}:latest" \
    --build-arg REACT_APP_BACKEND_URL="https://${BACKEND_DOMAIN}" \
    -f frontend/Dockerfile frontend/
docker push "${FRONTEND_IMAGE}:latest"
echo -e "${GREEN}✓ Frontend image pushed${NC}"

# ─── Deploy backend to Cloud Run ───
echo -e "${YELLOW}[5/6] Deploying backend to Cloud Run...${NC}"
gcloud run deploy "$BACKEND_SERVICE" \
    --image "${BACKEND_IMAGE}:latest" \
    --region "$REGION" \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 10 \
    --concurrency 80 \
    --timeout 300 \
    --set-env-vars "MONGO_URL=${MONGO_URL},DB_NAME=${DB_NAME},CORS_ORIGINS=https://${FRONTEND_DOMAIN}" \
    --set-env-vars "JWT_SECRET_KEY=${JWT_SECRET_KEY:-$(openssl rand -hex 32)}" \
    ${EMERGENT_LLM_KEY:+--set-env-vars "EMERGENT_LLM_KEY=${EMERGENT_LLM_KEY}"} \
    ${GEMINI_API_KEY:+--set-env-vars "GEMINI_API_KEY=${GEMINI_API_KEY}"} \
    ${STRIPE_SECRET_KEY:+--set-env-vars "STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}"} \
    ${RESEND_API_KEY:+--set-env-vars "RESEND_API_KEY=${RESEND_API_KEY}"}

BACKEND_URL=$(gcloud run services describe "$BACKEND_SERVICE" --region "$REGION" --format 'value(status.url)')
echo -e "${GREEN}✓ Backend deployed: ${BACKEND_URL}${NC}"

# ─── Deploy frontend to Cloud Run ───
echo -e "${YELLOW}[6/6] Deploying frontend to Cloud Run...${NC}"
gcloud run deploy "$FRONTEND_SERVICE" \
    --image "${FRONTEND_IMAGE}:latest" \
    --region "$REGION" \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 256Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 5 \
    --concurrency 200

FRONTEND_URL=$(gcloud run services describe "$FRONTEND_SERVICE" --region "$REGION" --format 'value(status.url)')
echo -e "${GREEN}✓ Frontend deployed: ${FRONTEND_URL}${NC}"

# ─── Summary ───
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "${BLUE}Backend:  ${BACKEND_URL}${NC}"
echo -e "${BLUE}Frontend: ${FRONTEND_URL}${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Map custom domains:"
echo "     gcloud run domain-mappings create --service ${BACKEND_SERVICE} --domain ${BACKEND_DOMAIN} --region ${REGION}"
echo "     gcloud run domain-mappings create --service ${FRONTEND_SERVICE} --domain ${FRONTEND_DOMAIN} --region ${REGION}"
echo "  2. Update DNS CNAME records to point to ghs.googlehosted.com"
echo "  3. Verify: curl https://${BACKEND_DOMAIN}/api/health"
echo ""
echo -e "${YELLOW}TEE ARCHITECTURE — Domain Map:${NC}"
echo "  sla113-api           → sla113.southernlifestyle.org"
echo "  empire1-api           → empire1.cloud              (future)"
echo "  lyrica3-api           → lyrica3.com                (future)"
echo "  arcade-frontend       → arcade.southernlifestyle.org (future)"
echo ""
