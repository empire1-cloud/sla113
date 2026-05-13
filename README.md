# Empire1 Ecosystem - SLA113 Sovereign Operator OS

Multi-universe AI entertainment platform with unified authentication and game studio.

## 🎵 NEW: Empire Lyric Master (Zero-API Music Production)

**Generate complete tracks in one command - zero API costs, 100% local:**

```bash
python3 LYRICA3/empire_lyric_master.py "toxic breakup anthem trap 120bpm"
```

**What you get:**
- ✅ Generated lyrics with vocal expression tags
- ✅ MIDI patterns (kick/snare/hihat with Late-Pocket timing)
- ✅ Mastering blueprint (DSP parameters for all stems)
- ✅ DSP automation events
- ✅ Complete track metadata

**[→ Full Guide](./LYRICA3/docs/EMPIRE_LYRIC_MASTER_GUIDE.md)** | **[→ Test it now](./tests/test_empire_lyric_master.py)**

**This is its own lane** - not competing with Suno/Udio, built for producers who need CONTROL.

---

## 🌐 The Empire1 Ecosystem

| Universe | Domain | Purpose |
|----------|--------|---------|
| **Empire1** | `empire1.cloud` | Creator SaaS Dashboard |
| **SLA113** | `sla113.southernlifestyle.org` | Sovereign Operator OS & Game Studio |
| **Lyrica3** | `lyrica3.com` | Music Universe - AI Music Creation |
| **Arcade** | `arcade.southernlifestyle.org` | Player-facing Game Portal |
| **Universal** | `sluniversal.lyrica3.com` | Universe Registry & Meta-Router |
| **SouthernLifestyle** | `southernlifestyle.org` | Brand Root & Identity |

**✨ Key Feature**: ONE login works across ALL universes - no separate accounts needed!

## 🚀 Quick Start (Local Development)

**Detailed guide**: See [LOCAL_SETUP.md](./LOCAL_SETUP.md) for full walkthrough.

```bash
# 1. Backend
cd backend
pip install -r requirements.txt
cp .env.example .env  # Edit with your MongoDB URL and API keys
uvicorn server:app --reload --port 8001

# 2. Frontend (new terminal)
cd frontend
yarn install
cp .env.example .env  # Edit: REACT_APP_BACKEND_URL=http://localhost:8001
yarn start
```

**First-time setup**: See [LOCAL_SETUP.md](./LOCAL_SETUP.md) for MongoDB, API keys, and more.

## 🚢 Deploy to Production

**For solo builders**: One-command deployment designed for accessibility.

**Quick Deploy**: See [deployment/QUICK_DEPLOY.md](./deployment/QUICK_DEPLOY.md)

```bash
# Save your secrets once
export MONGO_URL="mongodb+srv://..."
export GEMINI_API_KEY="your-key"

# Deploy everything
bash deployment/deploy.sh
```

**Full docs**: See [deployment/](./deployment/) folder for detailed guides.

## 🔑 Unified Authentication

**Important**: Empire1 uses ONE authentication system for ALL universes.

- ✅ Create ONE account → access ALL universes
- ✅ Same email/password for Empire1, SLA113, Lyrica3, Arcade
- ✅ Login once → session works everywhere
- ✅ Designed for solo builders with accessibility needs

**Test Account** (development):
- Email: `newuser@example.com`
- Password: `NewPass123!`

See [memory/test_credentials.md](./memory/test_credentials.md) for details.

## ✨ Features

### SLA113 Operator OS
- 29 game types across 5 categories (arcade, casino, RPG, racing, hybrid)
- AI-powered game studio with Vision, Logic, Composer engines
- Real-time multiplayer (fish shooter, slots)
- Build pipeline with AAA asset compilation
- White-label game deployment

### Empire1 Dashboard
- 19 specialized AI engines
- Pipeline composer for chaining engines
- Team management & billing
- Real-time analytics dashboard
- API key management

### Lyrica3 (Music Universe)
- **🎵 Empire Lyric Master** - Complete zero-API music production system
  - One-command track generation: `python3 LYRICA3/empire_lyric_master.py "your song idea"`
  - Zero API costs - 100% local processing
  - <5ms generation time per track
  - 20+ global genres (SGV/Chicano + Afrobeats/UK Drill/K-pop/etc)
  - Complete blueprints: lyrics, MIDI, DSP, mastering
  - See [EMPIRE_LYRIC_MASTER_GUIDE.md](./LYRICA3/docs/EMPIRE_LYRIC_MASTER_GUIDE.md) for usage
- AI music creation with Gemini
- Duet engine & emotional grammar
- Vocal logic system
- Creator-owned workflows

## 📋 Environment Configuration

### Backend (.env)

**Required**:
- `MONGO_URL` - MongoDB connection string
- `DB_NAME` - Database name (default: `hybrid_intelligence`)

**Optional but recommended**:
- `GEMINI_API_KEY` - For Lyrica3, image generation, AI features
- `EMERGENT_LLM_KEY` - For Empire1 AI engines
- `STRIPE_SECRET_KEY` - For billing features

**Template**: See [backend/.env.example](./backend/.env.example)

### Frontend (.env)

**Required**:
- `REACT_APP_BACKEND_URL` - Backend API URL

**Template**: See [frontend/.env.example](./frontend/.env.example)

## 🎯 Gemini API Key (Important for Lyrica)

The Gemini API key powers:
- 🎵 Lyrica3 music AI
- 🎨 Image generation for game assets
- 🧠 Various AI features across universes

**Get your free key**: https://ai.google.dev/ (60 requests/min free tier)

Add to `backend/.env`:
```bash
GEMINI_API_KEY=your-key-here
```

## 📚 Documentation

- **[LOCAL_SETUP.md](./LOCAL_SETUP.md)** - Local development setup
- **[deployment/](./deployment/)** - Production deployment guides
  - [QUICK_DEPLOY.md](./deployment/QUICK_DEPLOY.md) - One-command deploy
  - [DEPLOYMENT_GUIDE.md](./deployment/DEPLOYMENT_GUIDE.md) - Detailed Cloud Run guide
  - [LAUNCH_CHECKLIST.md](./deployment/LAUNCH_CHECKLIST.md) - Pre-launch verification
- **[memory/test_credentials.md](./memory/test_credentials.md)** - Unified login system
- **[AGENTS.md](./AGENTS.md)** - Full ecosystem architecture

## 🏗️ Technical Stack

- **Backend**: FastAPI (Python 3.12) + MongoDB + Motor (async)
- **Frontend**: React 19 + CRACO + TailwindCSS
- **Deployment**: Google Cloud Run (auto-scaling)
- **Database**: MongoDB Atlas (or self-hosted)
- **AI**: Gemini, Emergent LLM, GPT-5.2, Claude Sonnet

## 🔐 Security & Accessibility

Built with solo builders in mind:
- ✅ JWT auth with refresh tokens (7-day sessions)
- ✅ One account for all universes
- ✅ Browser password manager compatible
- ✅ Secure env var handling
- ✅ CORS configured per environment
- ✅ One-command deployment

## 🆘 Troubleshooting

**Can't connect to database?**
- Check `MONGO_URL` in backend/.env
- Verify MongoDB is running (local) or Atlas cluster is active

**Frontend shows "undefined/api/..."?**
- Check `REACT_APP_BACKEND_URL` in frontend/.env
- Should be `http://localhost:8001` for local dev

**Gemini API not working?**
- Verify `GEMINI_API_KEY` in backend/.env
- Check you have credits at https://ai.google.dev/
- Restart backend after adding key

**Module not found: emergentintegrations?**
```bash
cd backend
ln -s emergentintegrations_local_backup emergentintegrations
```

## 📱 Accessibility Features

Designed for solo builders with one-hand operation:
- ✅ Auto-reload dev servers
- ✅ Clear error messages
- ✅ One-command deployment
- ✅ Secrets file (configure once, use forever)
- ✅ No complex multi-step processes

## 📈 Cost (Production)

- **Cloud Run**: ~$5-10/month (2M free requests)
- **MongoDB Atlas**: Free tier available (512MB)
- **Total**: Can start <$5/month

## 🔄 Development Workflow

1. Make code changes
2. Services auto-reload
3. Test at http://localhost:3000
4. Commit & push to GitHub
5. Deploy: `bash deployment/deploy.sh`

## 📞 Support

- **Local issues**: Check terminal logs (backend) and browser console (frontend)
- **Production logs**: `gcloud run services logs read sla113-api --region us-central1`
- **API docs**: http://localhost:8001/docs (auto-generated FastAPI docs)
- **Issues**: Open on GitHub
