#!/usr/bin/env bash
# L4 Dry-Run Rollback Script
# Purpose: Rollback to L4 start checkpoint on ABORT
# Usage: bash scripts/ops/l4_dryrun_rollback.sh

set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

START_COMMIT_FILE="${START_COMMIT_FILE:-$ROOT/.reports/L4_START_COMMIT.txt}"

log() {
  echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $*" >&2
}

log "=== L4 Dry-Run Rollback ==="

# Step 1: Check if START_COMMIT file exists
if [ ! -f "$START_COMMIT_FILE" ]; then
  log "[FAIL] L4 start commit file not found: $START_COMMIT_FILE"
  log "[INFO] Manual rollback required"
  exit 1
fi

START_COMMIT=$(cat "$START_COMMIT_FILE" | head -1)
log "[INFO] Rolling back to commit: $START_COMMIT"

# Step 2: Revert rules changes (if any)
log "Step 1: Reverting rule changes..."
if git log --oneline "$START_COMMIT"..HEAD | grep -q "prometheus/rules"; then
  LAST_RULE_COMMIT=$(git log --oneline "$START_COMMIT"..HEAD -- prometheus/rules | head -1 | awk '{print $1}')
  if [ -n "$LAST_RULE_COMMIT" ]; then
    log "[INFO] Reverting rule commit: $LAST_RULE_COMMIT"
    git revert --no-edit "$LAST_RULE_COMMIT" || true
  fi
else
  log "[INFO] No rule changes to revert"
fi

# Step 3: Reset to start commit
log "Step 2: Resetting to start commit..."
git reset --hard "$START_COMMIT" || {
  log "[FAIL] Failed to reset to start commit"
  exit 1
}

# Step 4: Reload Prometheus
log "Step 3: Reloading Prometheus..."
bash scripts/ops/reload_safe.sh || {
  log "[WARN] Prometheus reload failed, restarting container..."
  docker compose -f compose.observation.yml restart prometheus || true
  sleep 10
}

# Step 5: Verify rollback
log "Step 4: Verifying rollback..."
sleep 5
if curl -sf http://localhost:9090/-/ready >/dev/null 2>&1; then
  log "[OK] Prometheus ready after rollback"
else
  log "[FAIL] Prometheus not ready after rollback"
  exit 1
fi

log "[OK] L4 Dry-Run Rollback completed successfully"
log "[INFO] System restored to checkpoint: $START_COMMIT"

