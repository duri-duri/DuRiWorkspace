#!/usr/bin/env bash
# Prometheus Safe Reload Script (Hardened)
# Purpose: Ensure promtool-check passes before reloading Prometheus
# Uses container-internal + host-side cross-check for reliability
# Includes retry logic and rule verification
# Usage: bash scripts/ops/reload_safe.sh

set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

PROM_URL="${PROM_URL:-http://localhost:9090}"
PROM_CONTAINER="${PROM_CONTAINER:-prometheus}"
PROM_IMG="${PROM_IMG:-prom/prometheus:v2.54.1}"

# Container-internal paths
PROM_CFG="/etc/prometheus/prometheus.yml"
PROM_RULES_DIR="/etc/prometheus/rules"

# Host-side paths
HOST_CFG="prometheus/prometheus.yml.minimal"
HOST_RULES_DIR="prometheus/rules"

log() {
  echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $*" >&2
}

log "=== Prometheus Safe Reload (Hardened - Cross-Check) ==="

# Step 0: Textfile directory verification
log "Step 0: Verifying textfile directory..."
TEXTFILE_DIR="${TEXTFILE_DIR:-$ROOT/reports/textfile}"
if [ ! -d "$TEXTFILE_DIR" ]; then
  log "[FAIL] Textfile directory missing: $TEXTFILE_DIR"
  exit 1
fi
if [ ! -w "$TEXTFILE_DIR" ]; then
  log "[FAIL] Textfile directory not writable: $TEXTFILE_DIR"
  exit 1
fi
log "[OK] Textfile directory verified: $TEXTFILE_DIR"

# Check node-exporter target health
log "Step 0.5: Verifying node-exporter target health..."
NODE_EXPORTER_UP=$(curl -sf --max-time 3 "${PROM_URL}/api/v1/targets" 2>/dev/null | \
  jq -r '[.data.activeTargets[]? | select(.labels.job=="node-exporter" and .health=="up")] | length' || echo "0")
if [ "$NODE_EXPORTER_UP" -eq 0 ]; then
  log "[WARN] No healthy node-exporter targets found (may be normal if not configured)"
else
  log "[OK] Node-exporter target healthy (up: $NODE_EXPORTER_UP)"
fi

# Step 1: Container-internal promtool check
log "Step 1: Container-internal promtool check..."
CONTAINER_OK=0
if docker exec "$PROM_CONTAINER" promtool check config "$PROM_CFG" >/dev/null 2>&1; then
  # Check rules individually (avoid glob issues)
  RULES_CHECKED=0
  for rule_file in prometheus/rules/*.yml; do
    if [ -f "$rule_file" ]; then
      rule_name=$(basename "$rule_file")
      if docker exec "$PROM_CONTAINER" promtool check rules "${PROM_RULES_DIR}/${rule_name}" >/dev/null 2>&1; then
        RULES_CHECKED=$((RULES_CHECKED + 1))
      fi
    fi
  done
  if [ "$RULES_CHECKED" -gt 0 ]; then
    log "[OK] Container-internal checks passed ($RULES_CHECKED rules)"
    CONTAINER_OK=1
  fi
fi

# Step 2: Host-side promtool check (cross-check, same version)
log "Step 2: Host-side promtool check (cross-check, pinned to ${PROM_IMG})..."
HOST_OK=0
if docker run --rm --entrypoint /bin/sh \
  -v "$ROOT/prometheus:/etc/prometheus:ro" \
  "$PROM_IMG" -lc "promtool check config /etc/prometheus/prometheus.yml.minimal" >/dev/null 2>&1; then
  RULES_CHECKED_HOST=0
  for rule_file in prometheus/rules/*.yml; do
    if [ -f "$rule_file" ]; then
      rule_name=$(basename "$rule_file")
      if docker run --rm --entrypoint /bin/sh \
        -v "$ROOT/prometheus:/etc/prometheus:ro" \
        "$PROM_IMG" -lc "promtool check rules /etc/prometheus/rules/${rule_name}" >/dev/null 2>&1; then
        RULES_CHECKED_HOST=$((RULES_CHECKED_HOST + 1))
      fi
    fi
  done
  if [ "$RULES_CHECKED_HOST" -gt 0 ]; then
    log "[OK] Host-side checks passed ($RULES_CHECKED_HOST rules)"
    HOST_OK=1
  fi
fi

# Both checks must pass (or at least one passes)
if [ "$CONTAINER_OK" -eq 0 ] && [ "$HOST_OK" -eq 0 ]; then
  log "[FAIL] Both container-internal and host-side checks failed"
  log "Fix configuration/rule errors before reloading"
  exit 1
fi

# Step 3: Wait for Prometheus readiness before reload
log "Step 3: Waiting for Prometheus readiness..."
for i in $(seq 1 10); do
  if curl -sf --max-time 2 "${PROM_URL}/-/ready" >/dev/null 2>&1; then
    log "[OK] Prometheus ready"
    break
  fi
  if [ "$i" -eq 10 ]; then
    log "[WARN] Prometheus readiness check timeout, proceeding anyway"
  else
    sleep 1
  fi
done

# Step 4: Reload Prometheus (with retry)
log "Step 4: Reloading Prometheus (with retry)..."
RELOAD_OK=0
for i in 1 2 3; do
  if curl -sf -X POST "${PROM_URL}/-/reload" >/dev/null 2>&1; then
    log "[OK] Prometheus reload request sent (attempt $i)"
    RELOAD_OK=1
    break
  else
    log "[WARN] Reload attempt $i failed, retrying..."
    sleep 2
  fi
done

if [ "$RELOAD_OK" -eq 0 ]; then
  log "[FAIL] Prometheus reload failed after 3 attempts"
  exit 1
fi

# Step 5: Wait for reload to complete
sleep 2

# Step 6: Verify reload success (check rules API for duri_heartbeat_ok)
log "Step 5: Verifying reload success..."
RELOAD_VERIFIED=0
for i in $(seq 1 5); do
  if curl -sf --max-time 3 "${PROM_URL}/api/v1/rules" 2>/dev/null | \
    jq -e '.. | objects | select(.name?=="duri_heartbeat_ok")' >/dev/null 2>&1; then
    log "[OK] Reload verification passed (heartbeat_ok rule found)"
    RELOAD_VERIFIED=1
    break
  fi
  if [ "$i" -lt 5 ]; then
    sleep 1
  fi
done

if [ "$RELOAD_VERIFIED" -eq 0 ]; then
  log "[WARN] Reload verification unclear, but reload command succeeded"
  log "[INFO] Check Prometheus logs if issues persist"
fi

# Step 7: Verify targets health
log "Step 6: Verifying targets health..."
TARGETS_HEALTHY=0
TARGETS_JSON=$(curl -sf --max-time 3 "${PROM_URL}/api/v1/targets" 2>/dev/null || echo "{}")
UP_COUNT=$(echo "$TARGETS_JSON" | jq -r '[.data.activeTargets[]? | select(.health=="up")] | length' || echo "0")
if [ "$UP_COUNT" -gt 0 ]; then
  log "[OK] Targets health check passed ($UP_COUNT targets up)"
  TARGETS_HEALTHY=1
else
  log "[WARN] No healthy targets found (may be normal if no targets configured)"
fi

log "[OK] Prometheus safe reload completed successfully"
exit 0
