#!/usr/bin/env bash
# Canary Promote or Rollback Hook
# Purpose: Evaluate canary health and decide promotion or rollback
# Usage: Called after canary deployment, checks health metrics

set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

PROM_URL="${PROM_URL:-http://localhost:9090}"
PROMOTION_CONFIG="${PROMOTION_CONFIG:-.obs/promotion.yml}"

log() {
  echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $*" >&2
}

# Load promotion config
if [ -f "$PROMOTION_CONFIG" ]; then
  MIN_SAMPLES=$(grep -E '^  min_samples:' "$PROMOTION_CONFIG" | awk '{print $2}' || echo "100")
  MAX_WAIT=$(grep -E '^  max_wait_seconds:' "$PROMOTION_CONFIG" | awk '{print $2}' || echo "1800")
  HEALTH_QUERY=$(grep -E '^  health_query:' "$PROMOTION_CONFIG" | cut -d"'" -f2 || echo 'duri_canary_health == 1')
  QUORUM_THRESHOLD=$(grep -E '^  quorum_threshold:' "$PROMOTION_CONFIG" | awk '{print $2}' || echo "0.95")
else
  MIN_SAMPLES=100
  MAX_WAIT=1800
  HEALTH_QUERY='duri_canary_health == 1'
  QUORUM_THRESHOLD=0.95
fi

log "Canary evaluation: min_samples=$MIN_SAMPLES, max_wait=${MAX_WAIT}s, threshold=$QUORUM_THRESHOLD"

# Check canary health
PASS_COUNT=$(curl -sf --max-time 3 --get "$PROM_URL/api/v1/query" \
  --data-urlencode "query=$HEALTH_QUERY" 2>/dev/null | \
  jq -r '.data.result | length' || echo "0")

TOTAL_SAMPLES=$(curl -sf --max-time 3 --get "$PROM_URL/api/v1/query" \
  --data-urlencode 'query=count(duri_canary_health)' 2>/dev/null | \
  jq -r '.data.result[0].value[1] // "0"' || echo "0")

if [ "$TOTAL_SAMPLES" -lt "$MIN_SAMPLES" ]; then
  log "[WAIT] Insufficient samples: $TOTAL_SAMPLES < $MIN_SAMPLES"
  exit 0  # Not ready yet, continue waiting
fi

PASS_RATIO=$(echo "scale=2; $PASS_COUNT / $TOTAL_SAMPLES" | bc -l 2>/dev/null || echo "0")

log "[METRICS] pass_count=$PASS_COUNT, total=$TOTAL_SAMPLES, ratio=$PASS_RATIO"

# Decision: promote or rollback
if (( $(echo "$PASS_RATIO >= $QUORUM_THRESHOLD" | bc -l 2>/dev/null || echo "0") )); then
  log "[PROMOTE] Canary health passed threshold: $PASS_RATIO >= $QUORUM_THRESHOLD"
  echo "PROMOTE"
  exit 0
else
  log "[ROLLBACK] Canary health below threshold: $PASS_RATIO < $QUORUM_THRESHOLD"
  
  # Create rollback tag
  RBT="rollback-$(date +%Y%m%d-%H%M)"
  git tag -a "$RBT" -m "auto rollback: canary health=$PASS_RATIO < $QUORUM_THRESHOLD"
  git push origin "$RBT" 2>/dev/null || log "[WARN] Failed to push rollback tag"
  
  echo "ROLLBACK"
  exit 1
fi

