# Local Development Setup (Solo Builder Edition)

Quick guide to get Empire1 running on your local machine.

## Prerequisites

- Python 3.12+ installed
- Node.js 18+ and yarn installed
- MongoDB running locally OR MongoDB Atlas account

## Step 1: Clone & Setup

```bash
# Clone the repo (if not already done)
git clone https://github.com/shiestybizz113-cell/sla113.git
cd sla113
```

## Step 2: Backend Setup

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Create your .env file
cp .env.example .env

# Edit .env with your settings (minimum required):
# MONGO_URL=mongodb://localhost:27017
# DB_NAME=hybrid_intelligence
# GEMINI_API_KEY=your-gemini-api-key  (optional but recommended)

# Optional: Create symlink for emergentintegrations (should already exist)
# ln -s emergentintegrations_local_backup emergentintegrations
```

## Step 3: Start MongoDB

**Option A: Local MongoDB**
```bash
# Start MongoDB (if installed locally)
sudo mongod --dbpath /data/db --fork --logpath /var/log/mongod.log
```

**Option B: MongoDB Atlas** (easiest for solo builders)
1. Go to https://www.mongodb.com/cloud/atlas
2. Create free cluster (512MB free tier)
3. Get connection string
4. Add to .env: `MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority`

## Step 4: Start Backend

```bash
# From backend/ directory
uvicorn server:app --reload --port 8001

# You should see:
# INFO:     Uvicorn running on http://127.0.0.1:8001
```

Keep this terminal open. Backend is now running on http://localhost:8001

## Step 5: Frontend Setup

Open a **new terminal**:

```bash
cd frontend

# Install dependencies
yarn install

# Create .env file
cp .env.example .env

# Edit .env:
# REACT_APP_BACKEND_URL=http://localhost:8001

# Start frontend dev server
yarn start
```

Frontend opens automatically at http://localhost:3000

## Step 6: Create Your First Account

1. Open http://localhost:3000 in your browser
2. Click "Sign Up"
3. Enter:
   - Email: your-email@example.com
   - Password: Test123! (or any password with uppercase, lowercase, number, 8+ chars)
   - First Name: Your
   - Last Name: Name
4. Click "Create Account"

**That's it!** You now have an account that works across all universes.

## Using Your Account

Your login credentials work in:
- ✅ **Empire1 Dashboard** at `/` - Main creator dashboard
- ✅ **SLA113 Operator** at `/sla113` - Game studio console  
- ✅ **Lyrica3** (future) - Music creation universe
- ✅ **Arcade** (future) - Game portal

No separate logins needed - one account for everything!

## Quick Test

Open http://localhost:8001/api/health - Should return:
```json
{"status":"healthy","database":"connected"}
```

## Project Structure

```
sla113/
├── backend/              # FastAPI backend
│   ├── server.py        # Main app entry
│   ├── routers/         # API routes
│   │   ├── auth/        # Authentication (login, signup, etc.)
│   │   ├── sla113.py    # SLA113 game studio APIs
│   │   └── engines/     # 19 AI engines
│   ├── services/        # Business logic
│   ├── models/          # Data models
│   └── .env.example     # Config template
│
├── frontend/            # React frontend
│   ├── src/
│   │   ├── App.jsx      # Main app with routing
│   │   ├── pages/       # All page components
│   │   │   ├── Login.jsx
│   │   │   ├── Signup.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   └── SLA113Page.jsx
│   │   └── contexts/    # AuthContext for login state
│   └── .env.example     # Config template
│
└── deployment/          # Cloud Run deployment
```

## Adding Your Gemini API Key

1. Get key from https://ai.google.dev/
2. Add to `backend/.env`:
   ```
   GEMINI_API_KEY=your-key-here
   ```
3. Restart backend: Ctrl+C then `uvicorn server:app --reload --port 8001`

Used for:
- Image generation in game studio
- Lyrica3 music analysis
- Various AI features

## Common Issues

**"No module named 'emergentintegrations'"**
```bash
cd backend
ln -s emergentintegrations_local_backup emergentintegrations
```

**"Database connection failed"**
- Check MongoDB is running: `mongod --version`
- Or use MongoDB Atlas free tier

**"Frontend shows undefined/api/..."**
- Check `frontend/.env` has `REACT_APP_BACKEND_URL=http://localhost:8001`
- Restart frontend: Ctrl+C then `yarn start`

**Port 3000 or 8001 already in use**
```bash
# Kill the process
lsof -ti:3000 | xargs kill -9  # Frontend
lsof -ti:8001 | xargs kill -9  # Backend
```

**Can't create account / login errors**
- Check backend logs for errors
- Verify MongoDB connection in terminal
- Try with test credentials: newuser@example.com / NewPass123!

## Development Workflow

1. Make code changes
2. Backend auto-reloads (--reload flag)
3. Frontend hot-reloads automatically
4. Test in browser
5. Commit when ready

## Testing

**Backend tests:**
```bash
cd backend
pytest tests/
```

**Frontend:**
No test files currently (all manual testing)

## Useful Commands

**Check backend health:**
```bash
curl http://localhost:8001/api/health
```

**Check SLA113 universes:**
```bash
curl http://localhost:8001/api/sla113/universes
```

**Create test account via API:**
```bash
curl -X POST http://localhost:8001/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!",
    "first_name": "Test",
    "last_name": "User"
  }'
```

## Stopping Services

**Backend:**
- Press Ctrl+C in backend terminal

**Frontend:**
- Press Ctrl+C in frontend terminal

**MongoDB (if running locally):**
```bash
sudo mongod --shutdown
# Or: sudo systemctl stop mongod
```

## Accessibility Features

Built for solo builders:
- ✅ Auto-reload on code changes (no manual restarts)
- ✅ Clear error messages in browser console
- ✅ Unified login (remember once, use everywhere)
- ✅ Browser password manager compatible
- ✅ 7-day refresh token (stay logged in)

## Next Steps

- Explore the SLA113 console at `/sla113`
- Try the AI engines via the dashboard
- Check deployment docs when ready to go live
- Add more API keys as needed (Stripe, etc.)

## Need Help?

- Backend logs: Check terminal running uvicorn
- Frontend logs: Check browser console (F12)
- API docs: http://localhost:8001/docs (FastAPI auto-docs)
- MongoDB issues: Check mongod logs

## Gemini API Key (Important for Lyrica)

The Gemini API key powers:
- 🎵 **Lyrica3 music AI** - Music generation and analysis
- 🎨 **Image generation** - Game assets, sprites, textures
- 🧠 **AI features** - Various intelligent features across universes

Get your free key:
1. Go to https://ai.google.dev/
2. Click "Get API key"
3. Create new key
4. Add to `backend/.env`
5. Restart backend

**Free tier**: 60 requests/minute - perfect for development!
