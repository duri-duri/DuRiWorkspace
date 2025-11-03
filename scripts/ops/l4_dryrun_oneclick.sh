#!/usr/bin/env bash
# L4 Dry-Run One-Click Execution Script
# Purpose: Execute all pre-flight checks and snapshots before L4 dry-run
# Usage: bash scripts/ops/l4_dryrun_oneclick.sh

set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

PROM_URL="${PROM_URL:-http://localhost:9090}"

log() {
  echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $*" >&2
}

log "=== L4 Dry-Run One-Click Pre-Flight Checks ==="

# Step 1: promtool-check
log "Step 1: promtool-check..."
if ! make promtool-check >/dev/null 2>&1; then
  log "[FAIL] promtool-check failed"
  exit 1
fi
log "[OK] promtool-check passed"

# Step 2: heartbeat-rules-lint
log "Step 2: heartbeat-rules-lint..."
if ! make heartbeat-rules-lint >/dev/null 2>&1; then
  log "[FAIL] heartbeat-rules-lint failed"
  exit 1
fi
log "[OK] heartbeat-rules-lint passed"

# Step 3: promql-unit (필수 통과 - 운영 전 테스트 결정론 확보)
log "Step 3: promql-unit REALM=prod (필수 통과)..."
if ! make promql-unit REALM=prod 2>&1; then
  log "[FAIL] promql-unit failed"
  log "[INFO] PromQL unit tests must pass before L4 dry-run"
  log "[INFO] Check test fixtures: tests/promql/heartbeat_test.yml"
  log "[INFO] Fix: Ensure input_series are properly injected and labels match"
  exit 1
fi
log "[OK] promql-unit passed"

# Step 4: reload_safe.sh
log "Step 4: reload_safe.sh..."
if ! bash scripts/ops/reload_safe.sh >/dev/null 2>&1; then
  log "[FAIL] reload_safe.sh failed"
  exit 1
fi
log "[OK] reload_safe.sh passed"

# Step 5: Heartbeat double increment (race protection)
log "Step 5: Heartbeat double increment (race protection)..."
bash scripts/ops/textfile_heartbeat.sh >/dev/null 2>&1 || true
sleep 3
bash scripts/ops/textfile_heartbeat.sh >/dev/null 2>&1 || true
log "[OK] Heartbeat incremented 2 times"

# Step 6: Snapshot
log ""
log "=== Metric Snapshot ==="
for q in \
  'duri_heartbeat_ok' \
  'duri_heartbeat_stall' \
  'duri_heartbeat_changes_6m' \
  'duri_heartbeat_fresh_120s' \
  'error_budget_burn_7d' \
  'error_budget_burn_30d' \
  'canary_failure_ratio' \
  'canary_unique_ratio' \
  'dr_rehearsal_p95_minutes' \
  'lyapunov_v'
do
  printf "[%s] " "$q"
  VALUE=$(curl -sf --max-time 3 --get "${PROM_URL}/api/v1/query" \
    --data-urlencode "query=$q" 2>/dev/null | \
    jq -r '.data.result[0].value[1] // "N/A"' || echo "N/A")
  echo "$VALUE"
done

# Step 7: L4 Dry-Run Decision
log ""
log "=== L4 Dry-Run Decision ==="
bash scripts/ops/l4_dryrun_decision.sh

log ""
log "[OK] L4 Dry-Run One-Click Pre-Flight Checks Completed"

