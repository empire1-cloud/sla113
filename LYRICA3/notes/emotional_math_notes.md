# Emotional Math — Notes

## Emotional Vectors

Each track payload carries emotional vectors used by the Lyrica pipeline:

- `vulnerability_score` (0–100): How exposed/raw the emotional content is
- `vibe_matrix`: Named cultural/emotional preset (e.g., "Guarded Hearts", "Chicano Soul")
- `rhythm_matrix`: Groove preset with BPM and snare drag values
- `duo`: boolean — whether this is a duet/duo soul track

## Biometric Realism

- PFA agent (Vocal Biometrics): translates vocal artifact tags to DSP automation JSON
- EPD (End-Point Detection): places natural silence and breathing phrases at phrase boundaries
- PTM (Psychoacoustic Texture Modeler): extracts impulse response from real spaces (SGV garage, Monte Carlo trunk, etc.)

## Bloodline Blending

Cross-pollinates vocal DNA to create harmonies from family members who have never sung together. Fuel sources:
- Family voicemails
- Jail calls (Ghost Audio artifacts)
- VHS recordings
- Live session captures

## Pipeline: AURA → EFL → ASE → ECHO → EFAD

| Stage | Role |
|---|---|
| AURA | Intent extraction, input sanitization |
| EFL | Emotion/biometric tagging |
| ASE | Novelty/authenticity scoring |
| ECHO | Groove physics, DSP routing |
| EFAD | Final Soulfire JSON payload assembly |
