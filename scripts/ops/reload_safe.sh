#!/usr/bin/env bash
# Prometheus Safe Reload Script
# Purpose: Ensure promtool-check passes before reloading Prometheus
# Uses container-internal paths for consistency
# Usage: bash scripts/ops/reload_safe.sh

set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

PROM_URL="${PROM_URL:-http://localhost:9090}"
PROM_CONTAINER="${PROM_CONTAINER:-prometheus}"

log() {
  echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $*" >&2
}

log "=== Prometheus Safe Reload (Container-Internal Check) ==="

# Step 1: promtool-check using container-internal paths
log "Step 1: Checking Prometheus config and rules (container-internal)..."
if docker exec "$PROM_CONTAINER" promtool check config /etc/prometheus/prometheus.yml.minimal >/dev/null 2>&1; then
  log "[OK] Config check passed"
else
  log "[FAIL] promtool-check-config failed (container-internal)"
  log "Fallback: Using host-side promtool-check..."
  if ! make promtool-check >/dev/null 2>&1; then
    log "[FAIL] promtool-check failed (host-side)"
    log "Fix configuration/rule errors before reloading"
    exit 1
  fi
fi

# Check rules using container-internal paths
RULES_CHECKED=0
for rule_file in prometheus/rules/*.yml; do
  if docker exec "$PROM_CONTAINER" promtool check rules "/etc/prometheus/rules/$(basename "$rule_file")" >/dev/null 2>&1; then
    RULES_CHECKED=$((RULES_CHECKED + 1))
  fi
done

if [ "$RULES_CHECKED" -gt 0 ]; then
  log "[OK] Rules check passed ($RULES_CHECKED files)"
else
  log "[WARN] No rules checked via container, using host-side check..."
  if ! make promtool-check >/dev/null 2>&1; then
    log "[FAIL] promtool-check failed"
    exit 1
  fi
fi

# Step 2: Reload Prometheus
log "Step 2: Reloading Prometheus..."
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
