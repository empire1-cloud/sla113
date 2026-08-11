# Flip It Protocol — Notes

## What It Is

The Flip It Protocol is the S2 Disruption Engine's public-facing workflow. It allows artists to:
1. Upload a source track (any genre)
2. Select a target genre matrix or define a custom cross-synthesis
3. Apply latent space transplantation (S2 engine)
4. Preview the flip at DRAFT tier
5. Render final at FINAL tier with royalty ledger entry

## S2 Disruption Engine

- STFT-based audio morphing (magnitude + phase manipulation)
- Latent space transplantation: forces incompatible genres to blend mathematically
- Example: SGV G-Funk + Gothic Choir + 808 Sub-Bass → new genre
- Spectral morphing: acoustic to electronic timbral fusion
- Groove transplantation: late-pocket swing injection into rigid patterns

## empire1_flip_engine.py

Source: `soulfire-ecosystem/src/services/empire1_flip_engine.py`  
Deployed to: `Lyrica3-pro/backend/empire1_flip_engine.py`

## Frontend

- `FlipItRemixInterface.tsx` — UI for flip workflow
- `FlipItSimulator.tsx` — preview/simulation mode
- `FlipFeed.jsx` — community flip discovery feed

## Status

- Flip engine Python: complete  
- Frontend components: present in Lyrica3-pro  
- API endpoint: needs wiring in server.py
