# GCP Deployment Strategy
**Empire Ecosystem Cloud Architecture**

## Current Deployment Map

### Railway (Free Tier - 3/4 slots used)
1. **Lyrica3-pro backend** - FastAPI + Demucs audio processing
2. **Empire-1 backend** - Full 19-engine orchestration hub
3. **Cultura Vibe backend** - Flask API for cultural AI workflows

**Free tier limit:** 4 services before charges kick in. Slot #4 reserved for emergency/temporary deploys.

### Vercel (Unlimited Free Frontends)
1. **Empire-1 frontend** - Next.js (empire1.cloud, southernlifestyle.org)
2. **Lyrica3-pro frontend** - CRA+CRACO (lyrica3.com) - Node 20 required
3. **Cultura Vibe frontend** - CRA+CRACO (aicatalyst.empire1.cloud)

### GCP Cloud Run (Unlimited Free Tier Services)
1. **sl-universal backend** - FastAPI orchestration hub
   - URL: `https://sl-universal-339698334666.us-central1.run.app`
   - Custom domain: `sluniversal.lyrica3.com` (pending DNS)
   - Memory: 512Mi, CPU: 1, Min: 0, Max: 10
   - **Scales to zero = $0 when idle**

---

## Future GCP Services (All Cloud Run)

### AudioCraft/MusicGen Services
**musicgen.lyrica3.com** - Local music generation engine
- Container: `audiocraft-small` (CPU-optimized) or `audiocraft-large` (GPU T4)
- Pattern: Clone `vertex_lyria_full_song()` 6-segment chunking + pydub crossfade
- Memory: 2Gi (small) or 8Gi (large)
- Cold start: 30-60s (acceptable for music generation)
- Cost: $0 when idle, ~$0.10/hour when active

**audiogen.lyrica3.com** - SFX and environmental sound generation
- Container: `audiocraft-audiogen`
- Memory: 1Gi
- Handles sub-10s clips (fast inference)

### Neuro-San Orchestration
**neurobridge.lyrica3.com** - Multi-agent creative OS hub
- Wires all 19 Empire engines as Cognizant Neuro-San protocol
- Memory: 1Gi
- WebSocket support for real-time agent communication
- Scales 0-100 based on active sessions

### Local LLM Inference
**nemotron.lyrica3.com** - Offline LLM fallback (Nemotron-3 8B)
- Container: `nemotron-3-8b-instruct` (quantized GGUF)
- GPU: NVIDIA T4 or L4 (required)
- Memory: 16Gi
- Min instances: 0 (expensive - only wake when needed)
- Use case: When internet down, GCP credit available, or Gemini quota exceeded

### Voice Generation
**voice.lyrica3.com** - XTTS-v2 or Parler-TTS local voice cloning
- Container: `xtts-v2` (Coqui TTS)
- Memory: 4Gi
- GPU: Optional (3x faster inference)
- Replaces Chirp dependency when offline

### VICS Ledger Sync
**vics-sync.lyrica3.com** - MongoDB sync for offline VICS ledgers
- Lightweight FastAPI service
- Reads `empire1_ledger.json` from uploads
- Writes to MongoDB Atlas
- Memory: 256Mi (minimal)

---

## Deployment Commands

### Build & Deploy Pattern
```bash
# 1. Build container on Cloud Build
gcloud builds submit --tag gcr.io/disco-amphora-490606-n8/{SERVICE_NAME}

# 2. Deploy to Cloud Run
gcloud run deploy {SERVICE_NAME} \
  --image gcr.io/disco-amphora-490606-n8/{SERVICE_NAME} \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory {MEMORY} \
  --cpu {CPU} \
  --min-instances 0 \
  --max-instances {MAX} \
  --port 8080

# 3. Map custom domain
gcloud beta run domain-mappings create \
  --service {SERVICE_NAME} \
  --domain {SUBDOMAIN}.lyrica3.com \
  --region us-central1
```

### GPU Deploy (for Nemotron, AudioCraft large, XTTS)
```bash
gcloud run deploy {SERVICE_NAME} \
  --image gcr.io/disco-amphora-490606-n8/{SERVICE_NAME} \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 16Gi \
  --cpu 4 \
  --gpu 1 \
  --gpu-type nvidia-tesla-t4 \
  --min-instances 0 \
  --max-instances 2 \
  --port 8080 \
  --timeout 600
```

---

## DNS Configuration

**All subdomains point to:** `ghs.googlehosted.com` (CNAME)

| Subdomain | Service | Status |
|---|---|---|
| `sluniversal.lyrica3.com` | sl-universal | Mapped (pending DNS) |
| `musicgen.lyrica3.com` | AudioCraft MusicGen | Planned |
| `audiogen.lyrica3.com` | AudioCraft AudioGen | Planned |
| `neurobridge.lyrica3.com` | Neuro-San hub | Planned |
| `nemotron.lyrica3.com` | Nemotron-3 LLM | Planned |
| `voice.lyrica3.com` | XTTS-v2 | Planned |
| `vics-sync.lyrica3.com` | VICS ledger | Planned |

---

## Cost Optimization Strategy

1. **Scale to zero by default** - All services min-instances=0 except production critical paths
2. **CPU-first** - Use CPU containers unless GPU proven necessary (AudioCraft small = CPU-viable)
3. **Cold start acceptable** - Music/voice gen users expect 30-60s wait
4. **Shared containers** - MusicGen + AudioGen in same container (route by endpoint)
5. **Request batching** - Queue multiple requests, wake service once, batch process
6. **Memory tuning** - Start small (512Mi), scale up only if OOM
7. **Region lock** - us-central1 only (cheapest, lowest latency to Railway services)

---

## When To Use Each Platform

**Railway:**
- Services already deployed (Lyrica3-pro, Empire-1, Cultura Vibe backends)
- PostgreSQL needed (Railway includes free Postgres)
- WebSocket-heavy workloads (persistent connections)

**Vercel:**
- All frontends (React, Next.js, static sites)
- Edge functions (lightweight API routes)
- CDN-required assets

**GCP Cloud Run:**
- Heavy compute (audio generation, LLM inference)
- GPU workloads (MusicGen large, Nemotron, XTTS)
- Scale-to-zero services (cost-sensitive)
- Long-running requests (up to 60min timeout)

**Local (shiestybizz machine):**
- Development/testing
- Offline-first workflows (when internet unstable)
- Prototyping new engines before deploy

---

## SSL & Security

- **SSL auto-provisioned** by Google Cloud Load Balancer (free, auto-renew)
- **HTTPS-only** enforced on all Cloud Run services
- **CORS configured** per service to allow frontend origins
- **Rate limiting** via Cloud Armor (future - when traffic grows)
- **Secret management** via GCP Secret Manager (not .env in containers)

---

## Next Actions

1. ✅ sl-universal deployed
2. ⏳ DNS CNAME `sluniversal -> ghs.googlehosted.com` (waiting on you)
3. 🔜 Deploy AudioCraft small (CPU) to `musicgen.lyrica3.com`
4. 🔜 Clone `vertex_lyria_full_song()` pattern for 6-segment stitching
5. 🔜 Wire VICS ledger sync service
6. 🔜 Deploy Neuro-San orchestration hub

---

**Last updated:** 2026-05-16 by OpenCode (shiestybizz113-cell)
