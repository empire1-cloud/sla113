# Quick Deploy Checklist (Solo Builder Edition)

**Designed for one-hand operation** - just copy/paste commands in order.

## Prerequisites (One-time Setup)

- [ ] Google Cloud account with billing enabled
- [ ] MongoDB Atlas cluster created (free tier works)
- [ ] gcloud CLI installed: `curl https://sdk.cloud.google.com | bash`

## Step 1: Save Your Secrets

Create a file `~/empire1-secrets.sh` with your keys (paste once, use forever):

```bash
#!/bin/bash
# Empire1 Secrets - Keep this file safe and never commit to git

export PROJECT_ID="your-gcp-project-id"
export MONGO_URL="mongodb+srv://user:password@cluster.mongodb.net/?retryWrites=true&w=majority"
export DB_NAME="hybrid_intelligence"
export GEMINI_API_KEY="your-gemini-api-key-here"
export EMERGENT_LLM_KEY="your-emergent-key-here"  # Optional
export STRIPE_SECRET_KEY="sk_live_..."  # Optional
```

Make it executable:
```bash
chmod +x ~/empire1-secrets.sh
```

## Step 2: Deploy (Single Command)

```bash
# Load your secrets and deploy
source ~/empire1-secrets.sh && cd /path/to/sla113 && bash deployment/deploy.sh
```

That's it! The script will:
- ✅ Configure GCP
- ✅ Build Docker images
- ✅ Deploy backend with all your API keys
- ✅ Deploy frontend
- ✅ Show you the URLs

## Step 3: Set Up Domain (One-time)

```bash
# Load secrets again
source ~/empire1-secrets.sh

# Map backend domain
gcloud run domain-mappings create \
  --service sla113-api \
  --domain sla113.southernlifestyle.org \
  --region us-central1

# Map frontend domain  
gcloud run domain-mappings create \
  --service sla113-frontend \
  --domain sla113.southernlifestyle.org \
  --region us-central1
```

Then add DNS CNAME records (do this in your domain registrar):
- `sla113.southernlifestyle.org` → `ghs.googlehosted.com`

## Step 4: Create Your Admin Account

```bash
# Create your first user (becomes admin automatically)
curl -X POST https://sla113.southernlifestyle.org/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "password": "YourSecure123!",
    "first_name": "Your",
    "last_name": "Name"
  }'
```

**Save these credentials** - they work across ALL universes (Empire1, SLA113, Lyrica3, Arcade).

## Quick Updates (After Initial Deploy)

Just run the deploy command again:
```bash
source ~/empire1-secrets.sh && cd /path/to/sla113 && bash deployment/deploy.sh
```

No need to repeat domain setup.

## Update Just Your API Keys

If you only need to update environment variables (like GEMINI_API_KEY):

```bash
source ~/empire1-secrets.sh

gcloud run services update sla113-api \
  --region us-central1 \
  --set-env-vars "GEMINI_API_KEY=${GEMINI_API_KEY}"
```

Service restarts automatically with new key.

## Check Service Status

```bash
# Backend health
curl https://sla113.southernlifestyle.org/api/health

# List your Cloud Run services
gcloud run services list --region us-central1
```

## Troubleshooting

**Can't login after deploy?**
- Check backend logs: `gcloud run services logs read sla113-api --region us-central1 --limit 50`
- Verify MONGO_URL is correct in the deployment

**Gemini API not working?**
- Update the env var: `gcloud run services update sla113-api --set-env-vars "GEMINI_API_KEY=your-key"`
- Check logs for "GEMINI_API_KEY" errors

**Need to redeploy quickly?**
```bash
# Save this as an alias in ~/.bashrc for one-command deploy:
alias empire1-deploy='source ~/empire1-secrets.sh && cd ~/sla113 && bash deployment/deploy.sh'

# Then just run:
empire1-deploy
```

## Cost Estimates

- **Cloud Run**: ~$5-10/month with free tier (first 2M requests free)
- **MongoDB Atlas**: Free tier (512MB) works for testing
- **Domain/DNS**: Varies by registrar
- **Total**: Can start with <$5/month

## Security Notes

- ✅ `~/empire1-secrets.sh` is in your home directory (not in git repo)
- ✅ Never commit `.env` files to GitHub
- ✅ JWT_SECRET_KEY is auto-generated securely on first deploy
- ✅ Cloud Run environment variables are encrypted at rest
- ✅ Use Secret Manager for production (optional): `gcloud secrets create`

## Getting Help

- **Backend logs**: `gcloud run services logs read sla113-api --region us-central1`
- **Frontend logs**: `gcloud run services logs read sla113-frontend --region us-central1`
- **Check deployment docs**: See `deployment/DEPLOYMENT_GUIDE.md`
