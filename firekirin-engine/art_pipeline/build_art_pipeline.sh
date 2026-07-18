#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

PIPELINE="firekirin-engine/art_pipeline"

python3 "$PIPELINE/generate_sprites.py" --roster "$PIPELINE/aztec_roster.json" --validate-only
python3 "$PIPELINE/generate_static_art.py" --contract "$PIPELINE/aztec_static_assets.json" --dry-run

if [[ "${1:-}" == "--generate" ]]; then
  python3 "$PIPELINE/generate_sprites.py" --roster "$PIPELINE/aztec_roster.json" --resume
  python3 "$PIPELINE/pack_sprite_sheet.py" --all --aggregate --install-dir backend/static/sprites
  python3 "$PIPELINE/generate_static_art.py" --contract "$PIPELINE/aztec_static_assets.json"
else
  echo
  echo "Validation only. Run with --generate to make API calls and build all art."
fi
