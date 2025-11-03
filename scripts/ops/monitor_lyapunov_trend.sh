#!/usr/bin/env bash
# Lyapunov V Trend Monitor
# Purpose: Monitor Lyapunov V trend and related metrics during L4 dry-run
# Usage: bash scripts/ops/monitor_lyapunov_trend.sh [duration_seconds]

set -euo pipefail

PROM_URL="${PROM_URL:-http://localhost:9090}"
DURATION="${1:-300}"  # Default 5 minutes
INTERVAL=30

log() {
  echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $*" >&2
}

query_prom() {
  local query="$1"
  curl -sf --max-time 3 --get "$PROM_URL/api/v1/query" \
    --data-urlencode "query=$query" 2>/dev/null | \
    jq -r '.data.result[0].value[1] // "N/A"' || echo "N/A"
}

log "=== Lyapunov V Trend Monitor ==="
log "Duration: ${DURATION}s, Interval: ${INTERVAL}s"
log ""

START_TIME=$(date +%s)
END_TIME=$((START_TIME + DURATION))

echo "Time,lyapunov_v,canary_unique_ratio,canary_failure_ratio,dr_p95_minutes,green_uptime_ratio"

while [ $(date +%s) -lt "$END_TIME" ]; do
  TIMESTAMP=$(date +%s)
  LYAPUNOV_V=$(query_prom 'duri_lyapunov_v')
  CANARY_UNIQUE=$(query_prom 'duri_canary_unique_ratio')
  CANARY_FAILURE=$(query_prom 'duri_canary_failure_ratio')
  DR_P95=$(query_prom 'duri_dr_rehearsal_p95_minutes')
  GREEN_UPTIME=$(query_prom 'duri_green_uptime_ratio')
  
  echo "$TIMESTAMP,$LYAPUNOV_V,$CANARY_UNIQUE,$CANARY_FAILURE,$DR_P95,$GREEN_UPTIME"
  
  sleep "$INTERVAL"
done

log ""
log "=== Trend Analysis ==="
log "Calculate stability: ΔV/Δt should be ≤ 0 for stability"

