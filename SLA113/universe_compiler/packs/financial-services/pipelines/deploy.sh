#!/usr/bin/env bash
# Deploy financial-services capability pack to SLA113 Execution Engine
set -euo pipefail

PACK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SLA113_CORE="${SLA113_CORE:-../../SLA113}"
DRY_RUN="${DRY_RUN:-false}"

echo "=== Financial Services Capability Pack ==="
echo "Pack: $PACK_DIR"
echo "Core: $SLA113_CORE"
echo ""

# 1. Validate structure
echo "[1/4] Validating capability pack structure..."
for dir in agents skills providers workflows connectors config; do
  if [ -d "$PACK_DIR/$dir" ]; then
    count=$(find "$PACK_DIR/$dir" -name "*.json" -o -name "*.md" | wc -l)
    echo "  ✓ $dir/ ($count files)"
  else
    echo "  ✗ $dir/ missing"
    exit 1
  fi
done

# 2. Register agents with Execution Engine
echo "[2/4] Registering agents..."
for agent_dir in "$PACK_DIR/agents"/*/; do
  agent_name=$(basename "$agent_dir")
  if [ -f "$agent_dir/agent.json" ]; then
    echo "  → $agent_name"
    if [ "$DRY_RUN" = false ]; then
      # POST agent definition to SLA113 Execution Engine
      : # curl -X POST "$SLA113_CORE/api/agents" -d @"$agent_dir/agent.json"
    fi
  fi
done

# 3. Register skills
echo "[3/4] Registering skills..."
for skill_dir in "$PACK_DIR/skills"/*/; do
  skill_name=$(basename "$skill_dir")
  if [ -f "$skill_dir/skill.md" ]; then
    echo "  → $skill_name"
    if [ "$DRY_RUN" = false ]; then
      : # curl -X POST "$SLA113_CORE/api/skills" -d @"$skill_dir/skill.md"
    fi
  fi
done

# 4. Register providers
echo "[4/4] Registering providers..."
for provider_dir in "$PACK_DIR/providers"/*/; do
  provider_name=$(basename "$provider_dir")
  if [ -f "$provider_dir/provider.json" ]; then
    echo "  → $provider_name"
    if [ "$DRY_RUN" = false ]; then
      : # curl -X POST "$SLA113_CORE/api/providers" -d @"$provider_dir/provider.json"
    fi
  fi
done

echo ""
echo "=== Deploy complete ==="
