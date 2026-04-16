# SLA113 — Universal AI Game Studio Operator OS

## Product Overview
SLA113 is the **sovereign root OS** for AI-powered game creation. Cultural backbone: Aztec myth + Chicano SGV + IELA roots.

## Game Engines (FireKirin/Juwa Tier)

### Fish Shooter Engine (fish_engine.py)
- 6 weapons: Cannon, Laser (pierce), Chain Lightning (3-chain), Bomb (120px AOE), Auto (triple), Railgun (boss killer)
- 12 fish species across 8 tiers (Clownfish → Sovereign Whale) with weighted spawn rates
- 3 Boss types: Jaguar Warrior (200hp, 1000x), Quetzalcoatl (300hp, 2000x), Tezcatlipoca (500hp, 5000x)
- 4 Special fish: Treasure Chest, Bomb Fish, Freeze Fish, Jackpot Crab
- 7 bet levels (1x-100x), progressive jackpot pool (2% of every shot)
- Movement patterns: linear, sine, zigzag, circle, drift, boss figure-8
- Damage numbers, death particles, boss announcements

### Video Slots Engine (slots_engine.py)
- 5 reels x 3 rows, up to 20 paylines
- 4 Progressive Jackpots: Grand (50K), Major (10K), Minor (2K), Mini (500)
- Cascading/Avalanche wins (winning symbols removed, new fall from top)
- Hold & Spin (6+ coins = lock & respin, fill all = GRAND JACKPOT)
- Bonus Wheel (5x-200x multipliers or free spins)
- Wild expansion + sticky wilds during free spins
- Free Spins: 3+ scatters = 10-25 spins with 2-3x multiplier
- Custom symbol support (Southern Lifestyle, Aztec, etc.)

## Architecture
```
/app/backend/sla113/
  ├── fish_engine.py        # FireKirin-tier fish shooter
  ├── slots_engine.py       # Juwa-tier video slots
  ├── fish_multiplayer.py   # WebSocket multiplayer
  ├── game_templates.py     # Template router
  ├── audio_forge.py, vision_engine.py, logic_engine.py, composer_engine.py, models.py
```

## Backlog
- [ ] Wire custom symbol sets into compile pipeline (P1)
- [ ] Add sprite-based fish rendering (replace Graphics with actual art assets) (P1)
- [ ] Agent/distributor cashier system (P2)
- [ ] Game library lobby with thumbnails (P2)
- [ ] Tournament system (P3)
