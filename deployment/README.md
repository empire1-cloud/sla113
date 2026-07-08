# Empire1 Deployment Hub

Quick links for deploying the Empire1 ecosystem to Google Cloud Run.

## 🚀 Quick Start (Recommended)

**For solo builders**: Use the simplified guide designed for one-hand operation.

📄 **[QUICK_DEPLOY.md](./QUICK_DEPLOY.md)** - Copy/paste deployment (easiest)

This guide:
- ✅ Single secrets file you configure once
- ✅ One command to deploy everything
- ✅ Includes Gemini API key setup
- ✅ Built for accessibility

## 📚 Detailed Guides

**For production setup**: Full step-by-step instructions with explanations.

📄 **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - Comprehensive Cloud Run guide

📄 **[LAUNCH_CHECKLIST.md](./LAUNCH_CHECKLIST.md)** - Pre-launch verification

## 🔧 Deployment Script

The main deployment script that does all the work:

📄 **[deploy.sh](./deploy.sh)** - Automated deploy script

## 🔑 API Keys & Configuration

### Required
- `MONGO_URL` - MongoDB connection string (Atlas or self-hosted)
- `DB_NAME` - Database name (default: `hybrid_intelligence`)

### Optional (but recommended)
- `GEMINI_API_KEY` - For Lyrica3 music AI, image generation, and more
- `EMERGENT_LLM_KEY` - For Empire1 AI engines
- `STRIPE_SECRET_KEY` - For billing features
- `RESEND_API_KEY` - For email notifications

### How to Configure

**Option 1**: Use environment variables (recommended for solo builder)
```bash
export GEMINI_API_KEY="your-key-here"
export MONGO_URL="mongodb+srv://..."
bash deployment/deploy.sh
```

**Option 2**: Create a secrets file (easiest)
```bash
# Create ~/empire1-secrets.sh with all your keys
# Then: source ~/empire1-secrets.sh && bash deployment/deploy.sh
```

See [QUICK_DEPLOY.md](./QUICK_DEPLOY.md) for the full template.

**Option 3**: Update after deployment
```bash
gcloud run services update sla113-api \
  --region us-central1 \
  --set-env-vars "GEMINI_API_KEY=your-new-key"
```

## 🎯 Unified Login System

**Important**: The Empire1 ecosystem uses ONE authentication system for ALL universes.

- ✅ Create one account → access Empire1, SLA113, Lyrica3, Arcade
- ✅ Same email/password works everywhere
- ✅ Login once, session works across all dashboards
- ✅ No separate Lyrica login - it uses Empire1 auth

See [../memory/test_credentials.md](../memory/test_credentials.md) for details.

## 📋 Pre-flight Checklist

Before deploying:
- [ ] GCP project created with billing enabled
- [ ] MongoDB Atlas cluster set up (or MongoDB server running)
- [ ] Gemini API key obtained (https://ai.google.dev/)
- [ ] Domain DNS access (for custom domains)
- [ ] gcloud CLI installed and authenticated

## 🆘 Quick Troubleshooting

**Deployment fails with "MONGO_URL not set"**
```bash
export MONGO_URL="your-connection-string"
```

**Gemini API not working after deploy**
```bash
# Update the env var:
gcloud run services update sla113-api \
  --region us-central1 \
  --set-env-vars "GEMINI_API_KEY=your-key"
```

**Can't login after deployment**
- Check backend logs: `gcloud run services logs read sla113-api --region us-central1`
- Verify MongoDB connection in logs
- Create first account: See test_credentials.md

**Need to redeploy quickly**
```bash
# Just run deploy again:
bash deployment/deploy.sh
```

## 🏗️ Architecture

The deployment creates 2 Cloud Run services:

1. **sla113-api** (Backend)
   - FastAPI + MongoDB
   - 19 AI engines
   - Unified auth system
   - All API routes

2. **sla113-frontend** (Frontend)
   - React 19 + CRACO
   - Empire1 dashboard
   - SLA113 operator console
   - Future: Lyrica3, Arcade UIs

Both services auto-scale, use custom domains, and share the same authentication.

## 🔐 Security Notes

- Environment variables are encrypted in Cloud Run
- JWT secrets auto-generated on first deploy
- Never commit `.env` files to git
- Use Secret Manager for production secrets (optional)
- CORS configured per environment

## 📈 Cost Estimate

- Cloud Run: ~$5-10/month (2M free requests/month)
- MongoDB Atlas: Free tier available (512MB)
- Artifact Registry: First 0.5 GB free
- Domain: Varies by registrar

**Total**: Can start with <$5/month on free tiers.

## 🔄 Update Workflow

1. Make code changes
2. Commit to GitHub
3. Run deploy script: `bash deployment/deploy.sh`
4. Services rebuild and redeploy automatically
5. Zero downtime (Cloud Run does rolling updates)

## 🌍 Universes & Domains

| Universe | Domain | Service | Status |
|----------|--------|---------|--------|
| Empire1 | `empire1.cloud` | `sla113-frontend` (/) | ✅ Active |
| SLA113 | `sla113.southernlifestyle.org` | `sla113-api` + `sla113-frontend` | ✅ Active |
| Lyrica3 | `lyrica3.com` | Shares SLA113 auth | 🚧 Future |
| Arcade | `arcade.southernlifestyle.org` | Shares SLA113 auth | 🚧 Future |
| Universal | `sluniversal.lyrica3.com` | Meta-router | 🚧 Future |
| SouthernLifestyle | `southernlifestyle.org` | Brand root | 🚧 Future |

All use the same authentication backend.

## 📱 Accessibility Features

Built with solo builders in mind:
- ✅ One command deployment
- ✅ Secrets file you configure once
- ✅ No complex multi-step processes
- ✅ Clear error messages
- ✅ Automatic retry on transient failures
- ✅ Progress indicators throughout deploy

## 📞 Support

- Issues: Open on GitHub
- Logs: `gcloud run services logs read SERVICE_NAME`
- Docs: See DEPLOYMENT_GUIDE.md for detailed info
