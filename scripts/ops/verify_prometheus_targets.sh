#!/usr/bin/env bash
# Prometheus Target Verification Script
# Purpose: Verify node-exporter is being scraped correctly
# Usage: bash scripts/ops/verify_prometheus_targets.sh

set -euo pipefail

PROM_URL="${PROM_URL:-http://localhost:9090}"

log() {
  echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $*" >&2
}

log "=== Prometheus Target Verification ==="

# Check targets API
TARGETS=$(curl -sf --max-time 5 --get "$PROM_URL/api/v1/targets" 2>/dev/null || echo "{}")

# Find node-exporter targets
NODE_TARGETS=$(echo "$TARGETS" | jq -r '.data.activeTargets[]? | select(.labels.instance|test(":9100$")) | "\(.labels.job) \(.scrapeUrl) \(.health)"' 2>/dev/null || echo "")

if [ -z "$NODE_TARGETS" ]; then
  log "[FAIL] No node-exporter targets found"
  log ""
  log "Checking scrape configs..."
  curl -sf --max-time 5 "$PROM_URL/api/v1/status/config" 2>/dev/null | jq -r '.data.yaml' | grep -A 10 "node-exporter" || log "[WARN] Could not fetch config"
  exit 1
fi

log "[OK] Found node-exporter targets:"
echo "$NODE_TARGETS" | while read -r line; do
  log "  $line"
done

# Check if any target is healthy
HEALTHY=$(echo "$NODE_TARGETS" | grep -c "up" || echo "0")

if [ "$HEALTHY" -eq 0 ]; then
  log "[FAIL] No healthy targets found"
  exit 1
fi

log "[OK] $HEALTHY healthy target(s) found"

# Verify metrics are being scraped
log ""
log "=== Metric Verification ==="
METRICS=$(curl -sf --max-time 5 http://localhost:9100/metrics 2>/dev/null | grep -c '^duri_' || echo "0")

if [ "$METRICS" -eq 0 ]; then
  log "[WARN] No duri_ metrics found at localhost:9100"
  log "  Run: bash scripts/ops/sync_textfile_dir.sh"
else
  log "[OK] Found $METRICS duri_ metrics at localhost:9100"
fi

# Check Prometheus has scraped the metrics
PROM_METRICS=$(curl -sf --max-time 5 --get "$PROM_URL/api/v1/query" \
  --data-urlencode 'query=duri_textfile_heartbeat_seq' 2>/dev/null | \
  jq -r '.data.result | length' || echo "0")

if [ "$PROM_METRICS" -eq 0 ]; then
  log "[WARN] Prometheus has not scraped duri_textfile_heartbeat_seq yet"
  log "  Wait 15-30 seconds for scrape interval"
else
  log "[OK] Prometheus has scraped duri_ metrics"
fi

log ""
log "[OK] Target verification complete"

