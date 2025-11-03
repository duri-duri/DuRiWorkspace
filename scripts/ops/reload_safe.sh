#!/usr/bin/env bash
# Prometheus Safe Reload Script
# Purpose: Ensure promtool-check passes before reloading Prometheus
# Usage: bash scripts/ops/reload_safe.sh

set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

PROM_URL="${PROM_URL:-http://localhost:9090}"

log() {
  echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $*" >&2
}

log "=== Prometheus Safe Reload ==="

# Step 1: promtool-check-config
log "Step 1: Checking Prometheus config..."
if ! make promtool-check-config >/dev/null 2>&1; then
  log "[FAIL] promtool-check-config failed"
  log "Fix configuration errors before reloading"
  exit 1
fi
log "[OK] Config check passed"

# Step 2: promtool-check-rules
log "Step 2: Checking Prometheus rules..."
if ! make promtool-check-rules >/dev/null 2>&1; then
  log "[FAIL] promtool-check-rules failed"
  log "Fix rule errors before reloading"
  exit 1
fi
log "[OK] Rules check passed"

# Step 1: promtool-check (config + rules)
log "Step 1: Checking Prometheus config and rules..."
if ! make promtool-check >/dev/null 2>&1; then
  log "[FAIL] promtool-check failed"
  log "Fix configuration/rule errors before reloading"
  exit 1
fi
log "[OK] Config and rules check passed"
if curl -sf -X POST "$PROM_URL/-/reload" >/dev/null 2>&1; then
  log "[OK] Prometheus reloaded successfully"
  sleep 2
  
  # Step 3: Verify reload success
  RELOAD_SUCCESS=$(curl -sf --max-time 3 "$PROM_URL/api/v1/status/config" 2>/dev/null | \
    jq -r '.data.yaml' | grep -c "prometheus" || echo "0")
  
  if [ "$RELOAD_SUCCESS" -gt 0 ]; then
    log "[OK] Reload verification passed"
    exit 0
  else
    log "[WARN] Reload verification unclear, but reload command succeeded"
    exit 0
  fi
else
  log "[FAIL] Prometheus reload failed"
  exit 1
fi
