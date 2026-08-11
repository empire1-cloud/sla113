# Empire Lyric Master - Setup & Installation

Complete setup guide for the zero-API music production system.

## Quick Start (5 Minutes)

### 1. Backend Setup

```bash
cd /home/shiestybizz/sla113

# Empire Lyric Master is already installed!
# Test it:
python3 LYRICA3/empire_lyric_master.py "test track trap 120bpm"
```

### 2. Install Audio Rendering (Optional)

```bash
# For audio rendering from blueprints:
pip install pydub mido soundfile

# Install ffmpeg (required for audio processing):
sudo apt update
sudo apt install ffmpeg
```

### 3. Start Backend Server

```bash
cd backend
uvicorn server:app --reload --port 8001
```

### 4. Start Frontend (New Terminal)

```bash
cd frontend
yarn start
```

### 5. Access the UI

Open browser: **http://localhost:3000/empire**

---

## API Endpoints

### Generate Track
```bash
POST /api/empire/generate
Content-Type: application/json

{
  "prompt": "toxic breakup anthem trap 120bpm",
  "genre_override": "trap",          // optional
  "bpm_override": 120,                // optional
  "vulnerability_override": 0.7       // optional
}
```

### Health Check
```bash
GET /api/empire/health
```

### List Genres
```bash
GET /api/empire/genres
```

---

## Usage Examples

### Command Line

```bash
# Quick generate
python3 LYRICA3/empire_lyric_master.py "your song idea"

# With output path
python3 LYRICA3/empire_lyric_master.py "heartbreak soul ballad" --output my_track.json

# Render audio from blueprint
python3 LYRICA3/render_from_blueprint.py output/empire_tracks/track_*.json

# Render to MP3
python3 LYRICA3/render_from_blueprint.py track.json --format mp3
```

### Python Script

```python
from LYRICA3.empire_lyric_master import EmpireLyricMaster

master = EmpireLyricMaster()
result = master.generate_complete_track("aggressive drill track")
result.save("output/my_track.json")
```

### cURL

```bash
curl -X POST http://localhost:8001/api/empire/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "toxic breakup anthem trap 120bpm"}'
```

---

## UI Modes

Empire Lyric Master has **3 interface modes**:

### 1. Quick Generate (Fast)
- Simple prompt input
- One-click generation
- Instant results
- Perfect for rapid ideation

### 2. Studio Pro (Control)
- Manual genre selection
- BPM slider
- Vulnerability control
- Tabbed results view (Lyrics, MIDI, DSP, Export)
- Full production interface

### 3. DuoSoul (Vibe) - Coming Soon
- Dual voice system
- Biometric controls
- Cultural authenticity
- Adapted from Lyrica3-pro prototype

---

## File Structure

```
sla113/
├── LYRICA3/
│   ├── empire_lyric_master.py      # Main system (615 lines)
│   ├── render_from_blueprint.py    # Audio renderer
│   ├── docs/
│   │   └── EMPIRE_LYRIC_MASTER_GUIDE.md
│   ├── intent_engine/              # AURA, ASE, EFL
│   ├── rhythm_engine/              # MMA (MIDI patterns)
│   ├── mastering_engine/           # PDA (DSP/mastering)
│   └── soulfire_engine/            # PFA, Empire Pipeline
├── backend/
│   └── routers/
│       └── empire_router.py        # API endpoints
├── frontend/
│   └── src/
│       ├── pages/
│       │   └── EmpireLyricMasterPage.jsx
│       └── components/empire/
│           ├── QuickGenerateMode.jsx
│           ├── StudioProMode.jsx
│           └── DuoSoulMode.jsx
├── tests/
│   └── test_empire_lyric_master.py
└── output/
    └── empire_tracks/              # Generated blueprints
```

---

## Troubleshooting

### Backend won't start
```bash
# Check Python path
which python3

# Check dependencies
pip install -r backend/requirements.txt
```

### Frontend can't connect
```bash
# Check backend URL in frontend/.env
echo "REACT_APP_BACKEND_URL=http://localhost:8001" > frontend/.env

# Restart frontend
cd frontend && yarn start
```

### Audio rendering fails
```bash
# Install audio libraries
pip install pydub mido soundfile

# Install ffmpeg
sudo apt install ffmpeg

# Test
python3 LYRICA3/render_from_blueprint.py --help
```

### Generation is slow
- First generation initializes engines (~100ms)
- Subsequent generations are <5ms
- This is normal!

---

## What You Get

Every track generation produces:

✅ **Lyrics** (4 lines with LML vocal tags)  
✅ **MIDI Patterns** (kick/snare/hihat with Late-Pocket timing)  
✅ **DSP Blueprint** (mastering parameters for all stems)  
✅ **Automation Events** (vocal_fry, emotional_crack, etc.)  
✅ **Performance Metrics** (AI detection risk, cultural authenticity)  
✅ **Complete JSON** (ready for audio rendering)

---

## Production Deployment

### Environment Variables

```bash
# backend/.env
MONGO_URL=mongodb://localhost:27017
DB_NAME=hybrid_intelligence

# frontend/.env
REACT_APP_BACKEND_URL=http://localhost:8001
```

### Docker (Optional)

```bash
# Build
docker build -t empire-lyric-master .

# Run
docker run -p 8001:8001 empire-lyric-master
```

---

## Performance

- **Generation**: <5ms per track
- **Memory**: ~50MB per instance
- **API Cost**: $0 forever
- **Network**: Zero external calls

---

## Support

**Documentation**: `/home/shiestybizz/sla113/LYRICA3/docs/EMPIRE_LYRIC_MASTER_GUIDE.md`

**GitHub**: https://github.com/shiestybizz113-cell/sla113

**Test Suite**: `python3 tests/test_empire_lyric_master.py`

---

Built by a solo mama builder. This is YOUR lane. 💪❤️
