#!/usr/bin/env bash
# Canary Promote or Rollback Hook
# Purpose: Evaluate canary health and decide promotion or rollback
# Enhanced: Dual-pass criteria (KS_p + unique_ratio), quorum check, exit codes
# Usage: Called after canary deployment, checks health metrics
# Exit codes: 0=promote, 3=quorum insufficient (wait), 4=rollback

set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

PROM_URL="${PROM_URL:-http://localhost:9090}"
PROMOTION_CONFIG="${PROMOTION_CONFIG:-.obs/promotion.yml}"

# Require commands
require() {
  command -v "$1" >/dev/null 2>&1 || { echo "[ERROR] missing $1" >&2; exit 2; }
}

require curl
require jq

log() {
  echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $*" >&2
}

# Load promotion config
if [ -f "$PROMOTION_CONFIG" ]; then
  MIN_SAMPLES=$(grep -E '^  min_samples:' "$PROMOTION_CONFIG" | awk '{print $2}' || echo "300")
  MAX_WAIT=$(grep -E '^  max_wait_seconds:' "$PROMOTION_CONFIG" | awk '{print $2}' || echo "1800")
  KS_P_THRESHOLD=$(grep -E '^  ks_p_threshold:' "$PROMOTION_CONFIG" | awk '{print $2}' || echo "0.05")
  UNIQUE_RATIO_MIN=$(grep -E '^  unique_ratio_min:' "$PROMOTION_CONFIG" | awk '{print $2}' || echo "0.92")
  DUAL_PASS=$(grep -E '^  dual_pass_required:' "$PROMOTION_CONFIG" | awk '{print $2}' || echo "true")
else
  MIN_SAMPLES=300
  MAX_WAIT=1800
  KS_P_THRESHOLD=0.05
  UNIQUE_RATIO_MIN=0.92
  DUAL_PASS="true"
fi

log "Canary evaluation: min_samples=$MIN_SAMPLES, max_wait=${MAX_WAIT}s, ks_p_threshold=$KS_P_THRESHOLD, unique_ratio_min=$UNIQUE_RATIO_MIN"

# 1) Quorum check
SAMPLES=$(curl -sf --max-time 3 --get "$PROM_URL/api/v1/query" \
  --data-urlencode 'query=duri_canary_samples' 2>/dev/null | \
  jq -r '.data.result[0].value[1] // "0"' || echo "0")

SAMPLES_INT=$(printf '%.0f' "$SAMPLES" 2>/dev/null || echo "0")

if [ "$SAMPLES_INT" -lt "$MIN_SAMPLES" ]; then
  log "[WAIT] Insufficient samples: $SAMPLES_INT < $MIN_SAMPLES"
  echo "NO_QUORUM"
  exit 3
fi

# 2) Dual-pass criteria check
KS_P_VALUE=$(curl -sf --max-time 3 --get "$PROM_URL/api/v1/query" \
  --data-urlencode 'query=duri_p_uniform_ks_p{window="2h"}' 2>/dev/null | \
  jq -r '.data.result[0].value[1] // "0"' || echo "0")

UNIQUE_RATIO_VALUE=$(curl -sf --max-time 3 --get "$PROM_URL/api/v1/query" \
  --data-urlencode 'query=duri_p_unique_ratio{window="2h"}' 2>/dev/null | \
  jq -r '.data.result[0].value[1] // "0"' || echo "0")

log "[METRICS] samples=$SAMPLES_INT, ks_p=$KS_P_VALUE, unique_ratio=$UNIQUE_RATIO_VALUE"

# Check dual-pass criteria
if [ "$DUAL_PASS" = "true" ]; then
  KS_P_PASS=$(echo "$KS_P_VALUE >= $KS_P_THRESHOLD" | bc -l 2>/dev/null || echo "0")
  UNIQUE_PASS=$(echo "$UNIQUE_RATIO_VALUE >= $UNIQUE_RATIO_MIN" | bc -l 2>/dev/null || echo "0")
  
  if [ "$KS_P_PASS" -eq 0 ] || [ "$UNIQUE_PASS" -eq 0 ]; then
    log "[ROLLBACK] Dual-pass failed: ks_p=$KS_P_VALUE (threshold=$KS_P_THRESHOLD), unique_ratio=$UNIQUE_RATIO_VALUE (min=$UNIQUE_RATIO_MIN)"
    
    # Create rollback tag
    TAG="rollback-$(date +%Y%m%d-%H%M)"
    git tag -a "$TAG" -m "canary auto-rollback: dual-pass failed (ks_p=$KS_P_VALUE, unique=$UNIQUE_RATIO_VALUE)" 2>/dev/null || log "[WARN] Failed to create tag"
    git push origin "$TAG" 2>/dev/null || log "[WARN] Failed to push tag"
    
    echo "ROLLBACK:$TAG"
    exit 4
  fi
fi

# 3) Final decision: promote
log "[PROMOTE] Canary passed: samples=$SAMPLES_INT, dual-pass OK"
echo "PROMOTE"
exit 0
