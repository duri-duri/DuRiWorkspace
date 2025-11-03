#!/usr/bin/env bash
# L4 24-Hour Stability Monitor
# Purpose: Monitor L4 dry-run stability for 24 hours and collect statistics
# Usage: bash scripts/ops/l4_24h_monitor.sh [duration_hours]
# Default: 24 hours (or specify custom duration)

set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

PROM_URL="${PROM_URL:-http://localhost:9090}"
DURATION_HOURS="${1:-24}"
INTERVAL_MINUTES="${INTERVAL_MINUTES:-10}"
LOG_FILE="${LOG_FILE:-var/logs/l4_24h_monitor.log}"

mkdir -p "$(dirname "$LOG_FILE")"

log() {
  local timestamp=$(date +%Y-%m-%d\ %H:%M:%S)
  echo "[$timestamp] $*" | tee -a "$LOG_FILE"
}

query_prom() {
  local query="$1"
  curl -sf --max-time 3 --get "${PROM_URL}/api/v1/query" \
    --data-urlencode "query=$query" 2>/dev/null | \
    jq -r '.data.result[0].value[1] // "N/A"' || echo "N/A"
}

log "=== L4 24-Hour Stability Monitor Started ==="
log "Duration: ${DURATION_HOURS} hours"
log "Interval: ${INTERVAL_MINUTES} minutes"
log "Log file: $LOG_FILE"

START_TIME=$(date +%s)
END_TIME=$((START_TIME + DURATION_HOURS * 3600))
ITERATION=0
FAIL_COUNT=0
ABORT_FLAG=0

# Critical thresholds
LYAPUNOV_THRESHOLD=0.3
CANARY_FAILURE_THRESHOLD=0.08
CANARY_UNIQUE_THRESHOLD=0.92
ERROR_BUDGET_7D_THRESHOLD=0.60
ERROR_BUDGET_30D_THRESHOLD=0.40
DR_P95_THRESHOLD=12

# Statistics arrays
declare -a LYAPUNOV_VALUES
declare -a HEARTBEAT_OK_VALUES
declare -a CANARY_FAILURE_VALUES
declare -a CANARY_UNIQUE_VALUES

log ""
log "=== Monitoring Started ==="
log "Thresholds:"
log "  - Lyapunov V: ≤ $LYAPUNOV_THRESHOLD"
log "  - Canary failure ratio: ≤ $CANARY_FAILURE_THRESHOLD"
log "  - Canary unique ratio: ≥ $CANARY_UNIQUE_THRESHOLD"
log "  - Error budget burn 7d: ≤ $ERROR_BUDGET_7D_THRESHOLD"
log "  - Error budget burn 30d: ≤ $ERROR_BUDGET_30D_THRESHOLD"
log "  - DR p95 minutes: ≤ $DR_P95_THRESHOLD"
log ""

while [ $(date +%s) -lt "$END_TIME" ]; do
  ITERATION=$((ITERATION + 1))
  ELAPSED_HOURS=$(echo "scale=2; ($(date +%s) - $START_TIME) / 3600" | bc)
  
  log "[Iteration $ITERATION] Elapsed: ${ELAPSED_HOURS}h"
  
  # Query all critical metrics
  HEARTBEAT_OK=$(query_prom 'duri_heartbeat_ok')
  HEARTBEAT_STALL=$(query_prom 'duri_heartbeat_stall')
  HEARTBEAT_CHANGES=$(query_prom 'duri_heartbeat_changes_6m')
  HEARTBEAT_FRESH=$(query_prom 'duri_heartbeat_fresh_120s')
  LYAPUNOV_V=$(query_prom 'duri_lyapunov_v')
  CANARY_FAILURE=$(query_prom 'duri_canary_failure_ratio')
  CANARY_UNIQUE=$(query_prom 'duri_canary_unique_ratio')
  ERROR_BUDGET_7D=$(query_prom 'duri_error_budget_burn_7d')
  ERROR_BUDGET_30D=$(query_prom 'duri_error_budget_burn_30d')
  DR_P95=$(query_prom 'duri_dr_rehearsal_p95_minutes')
  
  # Store values for statistics
  LYAPUNOV_VALUES+=("$LYAPUNOV_V")
  HEARTBEAT_OK_VALUES+=("$HEARTBEAT_OK")
  CANARY_FAILURE_VALUES+=("$CANARY_FAILURE")
  CANARY_UNIQUE_VALUES+=("$CANARY_UNIQUE")
  
  log "  heartbeat_ok: $HEARTBEAT_OK (target: ==1)"
  log "  heartbeat_stall: $HEARTBEAT_STALL (target: ==0)"
  log "  heartbeat_changes_6m: $HEARTBEAT_CHANGES (target: ≥1)"
  log "  heartbeat_fresh_120s: $HEARTBEAT_FRESH (target: ==1)"
  log "  lyapunov_V: $LYAPUNOV_V (target: ≤$LYAPUNOV_THRESHOLD)"
  log "  canary_failure_ratio: $CANARY_FAILURE (target: ≤$CANARY_FAILURE_THRESHOLD)"
  log "  canary_unique_ratio: $CANARY_UNIQUE (target: ≥$CANARY_UNIQUE_THRESHOLD)"
  log "  error_budget_burn_7d: $ERROR_BUDGET_7D (target: ≤$ERROR_BUDGET_7D_THRESHOLD)"
  log "  error_budget_burn_30d: $ERROR_BUDGET_30D (target: ≤$ERROR_BUDGET_30D_THRESHOLD)"
  log "  dr_rehearsal_p95_minutes: $DR_P95 (target: ≤$DR_P95_THRESHOLD)"
  
  # Check thresholds
  VIOLATION=0
  
  if [ "$HEARTBEAT_OK" != "1" ] && [ "$HEARTBEAT_OK" != "N/A" ]; then
    log "  [VIOLATION] heartbeat_ok != 1"
    VIOLATION=1
  fi
  
  if [ "$HEARTBEAT_STALL" = "1" ]; then
    log "  [VIOLATION] heartbeat_stall == 1"
    VIOLATION=1
  fi
  
  if [ "$HEARTBEAT_CHANGES" != "N/A" ] && (( $(echo "$HEARTBEAT_CHANGES < 1" | bc -l 2>/dev/null || echo "0") )); then
    log "  [VIOLATION] heartbeat_changes_6m < 1"
    VIOLATION=1
  fi
  
  if [ "$LYAPUNOV_V" != "N/A" ] && (( $(echo "$LYAPUNOV_V > $LYAPUNOV_THRESHOLD" | bc -l 2>/dev/null || echo "0") )); then
    log "  [VIOLATION] lyapunov_V > $LYAPUNOV_THRESHOLD"
    VIOLATION=1
    ABORT_FLAG=1
  fi
  
  if [ "$CANARY_FAILURE" != "N/A" ] && (( $(echo "$CANARY_FAILURE > $CANARY_FAILURE_THRESHOLD" | bc -l 2>/dev/null || echo "0") )); then
    log "  [VIOLATION] canary_failure_ratio > $CANARY_FAILURE_THRESHOLD"
    VIOLATION=1
  fi
  
  if [ "$CANARY_UNIQUE" != "N/A" ] && (( $(echo "$CANARY_UNIQUE < $CANARY_UNIQUE_THRESHOLD" | bc -l 2>/dev/null || echo "0") )); then
    log "  [VIOLATION] canary_unique_ratio < $CANARY_UNIQUE_THRESHOLD"
    VIOLATION=1
  fi
  
  if [ "$ERROR_BUDGET_7D" != "N/A" ] && (( $(echo "$ERROR_BUDGET_7D > $ERROR_BUDGET_7D_THRESHOLD" | bc -l 2>/dev/null || echo "0") )); then
    log "  [VIOLATION] error_budget_burn_7d > $ERROR_BUDGET_7D_THRESHOLD"
    VIOLATION=1
  fi
  
  if [ "$ERROR_BUDGET_30D" != "N/A" ] && (( $(echo "$ERROR_BUDGET_30D > $ERROR_BUDGET_30D_THRESHOLD" | bc -l 2>/dev/null || echo "0") )); then
    log "  [VIOLATION] error_budget_burn_30d > $ERROR_BUDGET_30D_THRESHOLD"
    VIOLATION=1
  fi
  
  if [ "$DR_P95" != "N/A" ] && (( $(echo "$DR_P95 > $DR_P95_THRESHOLD" | bc -l 2>/dev/null || echo "0") )); then
    log "  [VIOLATION] dr_rehearsal_p95_minutes > $DR_P95_THRESHOLD"
    VIOLATION=1
  fi
  
  if [ "$VIOLATION" -eq 1 ]; then
    FAIL_COUNT=$((FAIL_COUNT + 1))
    log "  [WARN] Violation detected (count: $FAIL_COUNT)"
    
    # Abort if Lyapunov V exceeds threshold
    if [ "$ABORT_FLAG" -eq 1 ]; then
      log ""
      log "[ABORT] Lyapunov V > $LYAPUNOV_THRESHOLD - Aborting monitoring"
      log "[ACTION] Trigger canary freeze + promotion stop"
      exit 1
    fi
    
    # Abort if violations persist for 2+ consecutive iterations
    if [ "$FAIL_COUNT" -ge 2 ]; then
      log ""
      log "[ABORT] Persistent violations detected (count: $FAIL_COUNT)"
      log "[ACTION] Trigger automatic remediation"
      exit 1
    fi
  else
    FAIL_COUNT=0  # Reset on success
  fi
  
  log ""
  
  # Sleep until next interval
  sleep $((INTERVAL_MINUTES * 60))
done

# Final statistics
log ""
log "=== Monitoring Completed ==="
log "Total iterations: $ITERATION"
log "Total violations: $FAIL_COUNT"

# Calculate statistics
if [ ${#LYAPUNOV_VALUES[@]} -gt 0 ]; then
  log ""
  log "=== Statistics ==="
  
  # Lyapunov V statistics
  LYAPUNOV_SUM=0
  LYAPUNOV_COUNT=0
  for val in "${LYAPUNOV_VALUES[@]}"; do
    if [ "$val" != "N/A" ]; then
      LYAPUNOV_SUM=$(echo "$LYAPUNOV_SUM + $val" | bc -l 2>/dev/null || echo "$LYAPUNOV_SUM")
      LYAPUNOV_COUNT=$((LYAPUNOV_COUNT + 1))
    fi
  done
  
  if [ "$LYAPUNOV_COUNT" -gt 0 ]; then
    LYAPUNOV_MEAN=$(echo "scale=4; $LYAPUNOV_SUM / $LYAPUNOV_COUNT" | bc -l)
    log "Lyapunov V: mean=$LYAPUNOV_MEAN, samples=$LYAPUNOV_COUNT"
    
    if (( $(echo "$LYAPUNOV_MEAN <= 0.2" | bc -l 2>/dev/null || echo "0") )); then
      log "[SUCCESS] L4.9 certification: Autonomous stability verified"
      exit 0
    elif (( $(echo "$LYAPUNOV_MEAN <= 0.3" | bc -l 2>/dev/null || echo "0") )); then
      log "[OK] L4.7 status: Stable but monitoring recommended"
      exit 0
    else
      log "[WARN] L4.5 status: Unstable, requires investigation"
      exit 1
    fi
  fi
fi

log "[OK] 24-hour monitoring completed successfully"
exit 0

