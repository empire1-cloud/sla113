# SLA113 Hybrid Factory (Parent)

SLA113 is the parent factory layer for multi-universe routing. Empire is now treated as a routed downstream universe.

Multi-model AI pipeline system with GPT-5.2, Claude Sonnet 4.5, and Gemini 3 Flash.

## Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn server:app --reload --port 8001

# Frontend
cd frontend
yarn install
yarn start
```

## Google Cloud Run Deployment

SLA113 is configured for Cloud Run deployment with Cloud Build:

- Backend pipeline: `cloudbuild.backend.yaml`
- Frontend pipeline: `cloudbuild.frontend.yaml`

Build examples:

```bash
gcloud builds submit --config cloudbuild.backend.yaml
gcloud builds submit --config cloudbuild.frontend.yaml --substitutions _REACT_APP_BACKEND_URL=https://sla113-backend-<hash>-uc.a.run.app
```

## Features
- 19 specialized AI engines
- Pipeline composer for chaining engines
- Real-time monitoring & analytics dashboard
- Execution history with search/filter

## Deployment Requirements

### psutil (System Monitoring)
The analytics dashboard uses `psutil` for real system metrics. Install on your VPS:

```bash
pip install psutil
```

If psutil is unavailable, the dashboard will display mock data with a warning indicator.

## Documentation
- [Analytics Dashboard](/app/backend/docs/ANALYTICS_DASHBOARD.md)
