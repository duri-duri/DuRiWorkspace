#!/usr/bin/env bash
# Canary Promote or Rollback Hook
# Purpose: Evaluate canary health and decide promotion or rollback
# Enhanced: Uses promotion.yml constants and dual-pass criteria (KS_p + unique_ratio)
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

# Check canary health using Prometheus recording rule
CANARY_HEALTH=$(curl -sf --max-time 3 --get "$PROM_URL/api/v1/query" \
  --data-urlencode 'query=duri_canary_health' 2>/dev/null | \
  jq -r '.data.result[0].value[1] // "0"' || echo "0")

# Check individual metrics if dual_pass is required
KS_P_VALUE="0"
UNIQUE_RATIO_VALUE="0"
if [ "$DUAL_PASS" = "true" ]; then
  KS_P_VALUE=$(curl -sf --max-time 3 --get "$PROM_URL/api/v1/query" \
    --data-urlencode 'query=duri_p_uniform_ks_p{window="2h"}' 2>/dev/null | \
    jq -r '.data.result[0].value[1] // "0"' || echo "0")
  
  UNIQUE_RATIO_VALUE=$(curl -sf --max-time 3 --get "$PROM_URL/api/v1/query" \
    --data-urlencode 'query=duri_p_unique_ratio{window="2h"}' 2>/dev/null | \
    jq -r '.data.result[0].value[1] // "0"' || echo "0")
fi

# Check sample count
SAMPLES=$(curl -sf --max-time 3 --get "$PROM_URL/api/v1/query" \
  --data-urlencode 'query=duri_canary_samples' 2>/dev/null | \
  jq -r '.data.result[0].value[1] // "0"' || echo "0")

log "[METRICS] canary_health=$CANARY_HEALTH, samples=$SAMPLES, ks_p=$KS_P_VALUE, unique_ratio=$UNIQUE_RATIO_VALUE"

# Decision: promote or rollback
if [ "$SAMPLES" -lt "$MIN_SAMPLES" ]; then
  log "[WAIT] Insufficient samples: $SAMPLES < $MIN_SAMPLES"
  exit 0  # Not ready yet, continue waiting
fi

# Check dual-pass criteria if required
if [ "$DUAL_PASS" = "true" ]; then
  KS_P_PASS=$(echo "$KS_P_VALUE >= $KS_P_THRESHOLD" | bc -l 2>/dev/null || echo "0")
  UNIQUE_PASS=$(echo "$UNIQUE_RATIO_VALUE >= $UNIQUE_RATIO_MIN" | bc -l 2>/dev/null || echo "0")
  
  if [ "$KS_P_PASS" -eq 0 ] || [ "$UNIQUE_PASS" -eq 0 ]; then
    log "[ROLLBACK] Dual-pass failed: ks_p=$KS_P_VALUE (threshold=$KS_P_THRESHOLD), unique_ratio=$UNIQUE_RATIO_VALUE (min=$UNIQUE_RATIO_MIN)"
    
    # Create rollback tag
    RBT="rollback-$(date +%Y%m%d-%H%M)"
    git tag -a "$RBT" -m "auto rollback: dual-pass failed (ks_p=$KS_P_VALUE, unique=$UNIQUE_RATIO_VALUE)"
    git push origin "$RBT" 2>/dev/null || log "[WARN] Failed to push rollback tag"
    
    echo "ROLLBACK"
    exit 1
  fi
fi

# Final decision based on canary_health
if (( $(echo "$CANARY_HEALTH == 1" | bc -l 2>/dev/null || echo "0") )); then
  log "[PROMOTE] Canary health passed: samples=$SAMPLES, dual-pass OK"
  echo "PROMOTE"
  exit 0
else
  log "[ROLLBACK] Canary health failed: canary_health=$CANARY_HEALTH"
  
  # Create rollback tag
  RBT="rollback-$(date +%Y%m%d-%H%M)"
  git tag -a "$RBT" -m "auto rollback: canary health=$CANARY_HEALTH"
  git push origin "$RBT" 2>/dev/null || log "[WARN] Failed to push rollback tag"
  
  echo "ROLLBACK"
  exit 1
fi

