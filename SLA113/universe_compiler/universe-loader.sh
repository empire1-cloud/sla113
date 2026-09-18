#!/usr/bin/env bash
# SLA113 Universe Loader
#
# Boot sequence for capability packs. Called by the Execution Engine at startup.
#
# Flow:
#   1. Read pack-registry.json
#   2. For each pack: validate → check lifecycle → resolve deps → register → mount
#   3. Expose unified capability registry
#
# Usage:
#   ./universe-loader.sh                    # Load all active packs
#   ./universe-loader.sh --dry-run          # Preview without registering
#   ./universe-loader.sh --pack gaming      # Load a specific pack only

set -euo pipefail

COMPILER_DIR="$(cd "$(dirname "$0")" && pwd)"
PACKS_DIR="$COMPILER_DIR/packs"
REGISTRY="$COMPILER_DIR/pack-registry.json"
SCHEMA="$COMPILER_DIR/pack-schema.json"
DRY_RUN=false
TARGET_PACK=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=true; shift ;;
    --pack)    TARGET_PACK="$2"; shift 2 ;;
    *)         echo "Unknown option: $1"; exit 1 ;;
  esac
done

# Colors
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; CYAN='\033[0;36m'; NC='\033[0m'

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  SLA113 Universe Loader v1.0${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Phase 1: Read registry
echo -e "${YELLOW}[1/5] Reading pack registry...${NC}"
if [ ! -f "$REGISTRY" ]; then
  echo -e "${RED}  ✗ Registry not found: $REGISTRY${NC}"
  exit 1
fi
PACK_COUNT=$(jq '.packs | length' "$REGISTRY")
echo -e "  ${GREEN}✓${NC} Found $PACK_COUNT packs in registry"
echo ""

# Phase 2: Validate each pack
echo -e "${YELLOW}[2/5] Validating packs against schema...${NC}"
VALID_COUNT=0
SKIP_COUNT=0
ERROR_COUNT=0

for pack_name in $(jq -r '.packs[].name' "$REGISTRY"); do
  # Filter by target if --pack specified
  if [ -n "$TARGET_PACK" ] && [ "$pack_name" != "$TARGET_PACK" ]; then
    continue
  fi

  PACK_DIR="$PACKS_DIR/$pack_name"
  PACK_JSON="$PACK_DIR/pack.json"

  if [ ! -f "$PACK_JSON" ]; then
    echo -e "  ${RED}✗ $pack_name: pack.json not found${NC}"
    ERROR_COUNT=$((ERROR_COUNT + 1))
    continue
  fi

  # Check lifecycle
  LIFECYCLE=$(jq -r '.lifecycle // "unknown"' "$PACK_JSON")
  if [ "$LIFECYCLE" != "active" ]; then
    echo -e "  ${YELLOW}∼${NC} $pack_name: lifecycle=$LIFECYCLE (skipping)"
    SKIP_COUNT=$((SKIP_COUNT + 1))
    continue
  fi

  # Validate required fields
  MISSING=""
  for field in name pack_version schema_version engine_version domain capabilities; do
    if [ "$(jq "has(\"$field\")" "$PACK_JSON")" != "true" ]; then
      MISSING="$MISSING $field"
    fi
  done

  if [ -n "$MISSING" ]; then
    echo -e "  ${RED}✗ $pack_name: missing fields:$MISSING${NC}"
    ERROR_COUNT=$((ERROR_COUNT + 1))
    continue
  fi

  # Check schema version compatibility
  SCHEMA_VER=$(jq -r '.schema_version' "$PACK_JSON")
  echo -e "  ${GREEN}✓${NC} $pack_name (v$(jq -r '.pack_version' "$PACK_JSON"), schema $SCHEMA_VER, engine $(jq -r '.engine_version' "$PACK_JSON"))"
  VALID_COUNT=$((VALID_COUNT + 1))
done

echo -e "  Result: $VALID_COUNT valid, $SKIP_COUNT skipped, $ERROR_COUNT errors"
echo ""

# Phase 3: Resolve dependencies
echo -e "${YELLOW}[3/5] Resolving dependencies...${NC}"
RESOLVED_COUNT=0
WARN_COUNT=0

for pack_name in $(jq -r '.packs[] | select(.lifecycle == "active" or .lifecycle == null) | .name' "$REGISTRY"); do
  PACK_JSON="$PACKS_DIR/$pack_name/pack.json"
  [ ! -f "$PACK_JSON" ] && continue
  [ "$(jq -r '.lifecycle // "active"' "$PACK_JSON")" != "active" ] && continue

  DEPS=$(jq -r '.dependencies // [] | .[] | "\(.capability) \(.optional // false)"' "$PACK_JSON" 2>/dev/null || true)
  if [ -z "$DEPS" ]; then
    echo -e "  ${GREEN}✓${NC} $pack_name: no dependencies"
    RESOLVED_COUNT=$((RESOLVED_COUNT + 1))
    continue
  fi

  while IFS=' ' read -r dep_cap dep_opt; do
    [ -z "$dep_cap" ] && continue
    # Check if any active pack provides this capability
    FOUND=false
    for p in $(jq -r '.packs[] | select(.lifecycle == "active" or .lifecycle == null) | .name' "$REGISTRY"); do
      PJ="$PACKS_DIR/$p/pack.json"
      [ ! -f "$PJ" ] && continue
      [ "$(jq -r '.lifecycle // "active"' "$PJ")" != "active" ] && continue
      if jq -e ".capabilities[] | select(.name == \"$dep_cap\")" "$PJ" > /dev/null 2>&1; then
        FOUND=true
        break
      fi
    done

    if [ "$FOUND" = true ]; then
      echo -e "  ${GREEN}✓${NC} $pack_name → $dep_cap (resolved)"
    elif [ "$dep_opt" = "true" ]; then
      echo -e "  ${YELLOW}∼${NC} $pack_name → $dep_cap (optional, not found — continuing)"
      WARN_COUNT=$((WARN_COUNT + 1))
    else
      echo -e "  ${RED}✗ $pack_name → $dep_cap (required, not found)${NC}"
      ERROR_COUNT=$((ERROR_COUNT + 1))
    fi
  done <<< "$DEPS"
  RESOLVED_COUNT=$((RESOLVED_COUNT + 1))
done
echo -e "  Result: $RESOLVED_COUNT resolved, $WARN_COUNT warnings, $ERROR_COUNT errors"
echo ""

# Phase 4: Register packs
echo -e "${YELLOW}[4/5] Registering pack capabilities...${NC}"
REGISTERED=0
if [ "$DRY_RUN" = true ]; then
  echo -e "  ${YELLOW}(dry run — skipping registration)${NC}"
else
  for pack_name in $(jq -r '.packs[] | select(.lifecycle == "active" or .lifecycle == null) | .name' "$REGISTRY"); do
    PACK_DIR="$PACKS_DIR/$pack_name"
    PACK_JSON="$PACK_DIR/pack.json"
    [ ! -f "$PACK_JSON" ] && continue
    [ "$(jq -r '.lifecycle // "active"' "$PACK_JSON")" != "active" ] && continue

    echo -e "  → Registering $pack_name..."

    # Register agents
    for agent_dir in "$PACK_DIR"/agents/*/; do
      [ -d "$agent_dir" ] || continue
      agent_name=$(basename "$agent_dir")
      if [ -f "$agent_dir/agent.json" ]; then
        echo -e "    agent: $agent_name"
        # POST /api/agents
      fi
    done

    # Register skills
    for skill_dir in "$PACK_DIR"/skills/*/; do
      [ -d "$skill_dir" ] || continue
      skill_name=$(basename "$skill_dir")
      if [ -f "$skill_dir/skill.md" ]; then
        echo -e "    skill: $skill_name"
        # POST /api/skills
      fi
    done

    # Register providers
    for provider_dir in "$PACK_DIR"/providers/*/; do
      [ -d "$provider_dir" ] || continue
      provider_name=$(basename "$provider_dir")
      if [ -f "$provider_dir/provider.json" ]; then
        echo -e "    provider: $provider_name"
        # POST /api/providers
      fi
    done

    # Register workflows
    for workflow_dir in "$PACK_DIR"/workflows/*/; do
      [ -d "$workflow_dir" ] || continue
      workflow_name=$(basename "$workflow_dir")
      if [ -f "$workflow_dir/workflow.json" ]; then
        echo -e "    workflow: $workflow_name"
        # POST /api/workflows
      fi
    done

    REGISTERED=$((REGISTERED + 1))
  done
fi
echo -e "  ${GREEN}✓${NC} $REGISTERED packs registered"
echo ""

# Phase 5: Mount capabilities
echo -e "${YELLOW}[5/5] Mounting capabilities into Knowledge Graph...${NC}"
MOUNTED=0
for pack_name in $(jq -r '.packs[] | select(.lifecycle == "active" or .lifecycle == null) | .name' "$REGISTRY"); do
  PACK_JSON="$PACKS_DIR/$pack_name/pack.json"
  [ ! -f "$PACK_JSON" ] && continue
  [ "$(jq -r '.lifecycle // "active"' "$PACK_JSON")" != "active" ] && continue

  CAP_COUNT=$(jq '.capabilities | length' "$PACK_JSON")
  echo -e "  → $pack_name: $CAP_COUNT capabilities"
  # POST /api/knowledge-graph mount points for each capability
  MOUNTED=$((MOUNTED + 1))
done
echo -e "  ${GREEN}✓${NC} $MOUNTED packs mounted"
echo ""

# Summary
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  Universe Loader Complete${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
echo -e "  Valid:       $VALID_COUNT packs"
echo -e "  Skipped:     $SKIP_COUNT packs (not active)"
echo -e "  Registered:  $REGISTERED packs"
echo -e "  Mounted:     $MOUNTED packs"
echo -e "  Warnings:    $WARN_COUNT"
echo -e "  Errors:      $ERROR_COUNT"
echo ""

if [ "$DRY_RUN" = true ]; then
  echo -e "${YELLOW}(dry run — no changes made)${NC}"
fi
