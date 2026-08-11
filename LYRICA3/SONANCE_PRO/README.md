# Sonance Pro — Sub-Universe 8 (inside Lyrica3)

**Role:** Pro music AI studio, advanced controls, mastering, subscription tier  
**Route:** lyrica3.com (default mode in Lyrica3 app)

## What It Is

Sonance Pro is the professional studio mode of Lyrica3. Full stem deck, S2 mutation slider, vulnerability scoring, biometric vocal strip, DAW bridge (Orchestrator), and micro-royalty display.

## Key Components

- `SonanceProStudio.tsx` — Pro studio UI shell
- `MixerConsole.tsx` — 4-stem mixer with reverb/EQ/pan
- `BiometricVocalStrip.tsx` — Real-time vocal biometric display
- `SSLVConsole.tsx` — SSL-style mastering console
- `VICSModule.tsx` — VICS Protocol UI
- `FlipItRemixInterface.tsx` + `FlipItSimulator.tsx` — Flip It workflow

## Subscription Layer

- DRAFT: free tier
- PREVIEW: creator tier
- FINAL: pro tier (48kHz/24-bit, full stem export, royalty ledger entry)
