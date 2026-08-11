# Micro Royalties — Notes

## MSGO Render Tiers

| Tier | Sample Rate | Bit Depth | Timesteps | CFG | Cost/Render |
|---|---|---|---|---|---|
| DRAFT | 22,050 Hz | 16-bit | 5 | 1.5 | $0.0003 |
| PREVIEW | 44,100 Hz | 16-bit | 8 | 2.0 | $0.0008 |
| FINAL | 48,000 Hz | 24-bit | 12 | 2.5 | $0.0020 |

## Territory Multipliers (EPD — End-Point Detection)

| Territory | Multiplier | Example (1M streams) |
|---|---|---|
| US | 1.0 | $4,000 |
| EU | 0.85 | $3,400 |
| LATAM | 0.6 | $2,400 |
| APAC | 0.7 | $2,800 |

## Split Architecture

- No middlemen. Ledger slices go directly to: beat maker, vocalist, lyricist, producer.
- CockroachDB ledger — immutable, idempotent, checksummed.
- EPD (End-Point Detection) adds natural breathing artifacts per territory compression profile.

## Implementation Status

- Python empire_ledger service: complete, operational
- CockroachDB integration: active
- Frontend royalty display (StemDeck.jsx): ready for backend hookup
- Smart contracts for Cultural Vault: pending
