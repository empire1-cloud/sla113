#!/usr/bin/env bash
set -euo pipefail

SLA113_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0
FAIL=0

echo "============================================"
echo "  SLA113 Platform Verification Suite"
echo "============================================"
echo ""

run_test() {
    local name="$1"
    local script="$2"
    echo "--- $name ---"
    if python3 "$SLA113_DIR/$script"; then
        echo "  PASS"
        PASS=$((PASS + 1))
    else
        echo "  FAIL"
        FAIL=$((FAIL + 1))
    fi
    echo ""
}

run_test "Phase 1 — Registries + Execution Engine + Handlers" "verify_phase1.py"
run_test "Phase 2A — Runtime internals (router, lifecycle, cache)" "verify_phase2a.py"
run_test "Phase 2 — Capabilities (AI, Identity, Storage) + Cross-pack" "verify_phase2.py"

echo "============================================"
echo "  Results: $PASS passed, $FAIL failed"
echo "============================================"

exit $FAIL
