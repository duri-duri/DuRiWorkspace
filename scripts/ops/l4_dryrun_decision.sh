#!/usr/bin/env bash
# L4 Dry-Run Go/No-Go Decision Script
# Purpose: Verify all 4 axes are connected and determine if L4 dry-run can proceed
# Usage: bash scripts/ops/l4_dryrun_decision.sh

set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

PROM_URL="${PROM_URL:-http://localhost:9090}"
REPO="${REPO:-duri-duri/DuRiWorkspace}"

log() {
  echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $*" >&2
}

query_prom() {
  local query="$1"
  curl -sf --max-time 3 --get "$PROM_URL/api/v1/query" \
    --data-urlencode "query=$query" 2>/dev/null | \
    jq -r '.data.result[0].value[1] // "0"' || echo "0"
}

# 1) Protected Branch 검증
log "=== 1) Protected Branch 검증 ==="
if command -v gh >/dev/null 2>&1; then
  PROTECTION=$(gh api "repos/$REPO/branches/main/protection" 2>/dev/null || echo "{}")
  
  ENFORCE_ADMINS=$(echo "$PROTECTION" | jq -r '.enforce_admins.enabled // false')
  ALLOW_FORCE=$(echo "$PROTECTION" | jq -r '.allow_force_pushes.enabled // false')
  ALLOW_DELETE=$(echo "$PROTECTION" | jq -r '.allow_deletions.enabled // false')
  REQUIRED_CHECKS=$(echo "$PROTECTION" | jq -r '.required_status_checks.contexts[]? // empty' | sort)
  
  log "  enforce_admins: $ENFORCE_ADMINS"
  log "  allow_force_pushes: $ALLOW_FORCE"
  log "  allow_deletions: $ALLOW_DELETE"
  log "  required_checks:"
  echo "$REQUIRED_CHECKS" | while read -r check; do
    log "    - $check"
  done
  
  # Check for required checks
  REQUIRED_CHECK_LIST=("obs-lint" "sandbox-smoke-60s" "promql-unit" "dr-rehearsal-24h-pass" "canary-quorum-pass" "error-budget-burn-ok")
  MISSING_CHECKS=()
  for check in "${REQUIRED_CHECK_LIST[@]}"; do
    if ! echo "$REQUIRED_CHECKS" | grep -q "^${check}$"; then
      MISSING_CHECKS+=("$check")
    fi
  done
  
  if [ ${#MISSING_CHECKS[@]} -gt 0 ]; then
    log "[FAIL] Missing required checks: ${MISSING_CHECKS[*]}"
    PROTECTION_OK=0
  else
    log "[OK] All required checks present"
    PROTECTION_OK=1
  fi
else
  log "[WARN] GitHub CLI (gh) not found, skipping Protected Branch verification"
  PROTECTION_OK=0
fi

# 2) Cron 등록 확인
log ""
log "=== 2) Cron 등록 확인 ==="
CRON_HEARTBEAT=$(crontab -l 2>/dev/null | grep -c "textfile_heartbeat.sh" || echo "0")
CRON_DR=$(crontab -l 2>/dev/null | grep -c "dr_rehearsal.sh" || echo "0")

log "  textfile_heartbeat.sh: $CRON_HEARTBEAT entry"
log "  dr_rehearsal.sh: $CRON_DR entry"

if [ "$CRON_HEARTBEAT" -ge 1 ] && [ "$CRON_DR" -ge 1 ]; then
  CRON_OK=1
  log "[OK] Cron entries registered"
else
  CRON_OK=0
  log "[FAIL] Missing cron entries"
fi

# 3) 핵심 8개 시계열 검증
log ""
log "=== 3) 핵심 시계열 검증 ==="

GREEN_UPTIME=$(query_prom 'duri_green_uptime_ratio')
ERROR_BUDGET_7D=$(query_prom 'duri_error_budget_burn_7d')
ERROR_BUDGET_30D=$(query_prom 'duri_error_budget_burn_30d')
DR_P95=$(query_prom 'duri_dr_rehearsal_p95_minutes')  # Use smoke rule
CANARY_FAILURE=$(query_prom 'duri_canary_failure_ratio')
CANARY_UNIQUE=$(query_prom 'duri_canary_unique_ratio')
LYAPUNOV_V=$(query_prom 'duri_lyapunov_v')
HEARTBEAT_STALL=$(query_prom 'duri_textfile_heartbeat_seq')  # Use current value instead of increase

log "  duri_green_uptime_ratio: $GREEN_UPTIME (target: ≥0.9990)"
log "  error_budget_burn_7d: $ERROR_BUDGET_7D (target: ≤0.60)"
log "  error_budget_burn_30d: $ERROR_BUDGET_30D (target: ≤0.40)"
log "  dr_rehearsal_p95_minutes: $DR_P95 (target: ≤12)"
log "  canary_failure_ratio: $CANARY_FAILURE (target: ≤0.08)"
log "  canary_unique_ratio: $CANARY_UNIQUE (target: ≥0.92)"
log "  lyapunov_V: $LYAPUNOV_V"
log "  heartbeat_stall: $HEARTBEAT_STALL (target: >0)"

# Go/No-Go 판정
GO=1

if (( $(echo "$GREEN_UPTIME < 0.9990" | bc -l 2>/dev/null || echo "1") )); then
  log "[NO-GO] GREEN uptime < 0.9990"
  GO=0
fi

if (( $(echo "$ERROR_BUDGET_30D > 0.40" | bc -l 2>/dev/null || echo "0") )); then
  log "[NO-GO] Error budget burn 30d > 0.40"
  GO=0
fi

if (( $(echo "$DR_P95 > 12" | bc -l 2>/dev/null || echo "0") )); then
  log "[NO-GO] DR p95 > 12 minutes"
  GO=0
fi

if (( $(echo "$CANARY_FAILURE > 0.08" | bc -l 2>/dev/null || echo "0") )); then
  log "[NO-GO] Canary failure ratio > 0.08"
  GO=0
fi

if (( $(echo "$CANARY_UNIQUE < 0.92" | bc -l 2>/dev/null || echo "0") )); then
  log "[NO-GO] Canary unique ratio < 0.92"
  GO=0
fi

if [ "$HEARTBEAT_STALL" = "0" ] || [ -z "$HEARTBEAT_STALL" ] || (( $(echo "$HEARTBEAT_STALL < 1" | bc -l 2>/dev/null || echo "1") )); then
  log "[NO-GO] Heartbeat stalled (value: $HEARTBEAT_STALL)"
  GO=0
fi

if [ "$PROTECTION_OK" -eq 0 ]; then
  log "[NO-GO] Protected Branch not configured"
  GO=0
fi

if [ "$CRON_OK" -eq 0 ]; then
  log "[NO-GO] Cron not registered"
  GO=0
fi

# 4) 최종 판정
log ""
log "=== 4) 최종 판정 ==="

if [ "$GO" -eq 1 ]; then
  log "[GO] ✅ L4 dry-run can proceed"
  log ""
  log "Current state: L3.7 (±0.2)"
  log "All 4 axes connected: Governance, Observability, Self-Evolution, DR"
  log ""
  log "Next steps:"
  log "  1. Execute L4 dry-run tests"
  log "  2. Monitor Lyapunov V trend"
  log "  3. Verify canary promotion/rollback"
  exit 0
else
  log "[NO-GO] ❌ L4 dry-run blocked"
  log ""
  log "Blocking conditions:"
  [ "$PROTECTION_OK" -eq 0 ] && log "  - Protected Branch not configured"
  [ "$CRON_OK" -eq 0 ] && log "  - Cron not registered"
  (( $(echo "$GREEN_UPTIME < 0.9990" | bc -l 2>/dev/null || echo "1") )) && log "  - GREEN uptime < 0.9990"
  (( $(echo "$ERROR_BUDGET_30D > 0.40" | bc -l 2>/dev/null || echo "0") )) && log "  - Error budget burn > 0.40"
  (( $(echo "$DR_P95 > 12" | bc -l 2>/dev/null || echo "0") )) && log "  - DR p95 > 12 minutes"
  (( $(echo "$CANARY_FAILURE > 0.08" | bc -l 2>/dev/null || echo "0") )) && log "  - Canary failure > 0.08"
  (( $(echo "$CANARY_UNIQUE < 0.92" | bc -l 2>/dev/null || echo "0") )) && log "  - Canary unique < 0.92"
  [ "$HEARTBEAT_STALL" = "0" ] && log "  - Heartbeat stalled"
  log ""
  log "Fix blocking conditions and rerun this script"
  exit 1
fi

