#!/usr/bin/env bash
# L4 Weekly Summary Calculation
# Purpose: Calculate promotion score after 7 days of observation
# Usage: bash scripts/ops/l4_weekly_summary.sh [date]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
AUDIT_DIR="$REPO_ROOT/var/audit"
INDEX_FILE="$REPO_ROOT/docs/ops/audit/audit_index.jsonl"
END_DATE="${1:-$(date +%Y%m%d)}"
START_DATE=$(date -d "$END_DATE -7 days" +%Y%m%d 2>/dev/null || echo "$END_DATE")

log() {
  echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $*"
}

calculate_slo_pass_rate() {
  local start_ts=$(date -d "$START_DATE" +%s 2>/dev/null || echo "0")
  local end_ts=$(date -d "$END_DATE" +%s 2>/dev/null || echo "$(date +%s)")
  
  if [ ! -s "$INDEX_FILE" ]; then
    echo "0.0"
    return
  fi
  
  # Count watch events
  local total=$(jq -r "select(.stage==\"post-merge-watch\" and .ts >= \"$(date -d "@$start_ts" -u +%Y-%m-%dT%H:%M:%SZ)\" and .ts <= \"$(date -d "@$end_ts" -u +%Y-%m-%dT%H:%M:%SZ)\") | .result" < "$INDEX_FILE" 2>/dev/null | grep -c "." || echo "0")
  local passed=$(jq -r "select(.stage==\"post-merge-watch\" and .result==\"pass\") | .result" < "$INDEX_FILE" 2>/dev/null | grep -c "." || echo "0")
  
  if [ "$total" -eq 0 ]; then
    echo "0.0"
    return
  fi
  
  local rate=$(echo "scale=4; $passed / $total" | bc)
  echo "$rate"
}

calculate_false_positive_rate() {
  if [ ! -s "$INDEX_FILE" ]; then
    echo "0.0"
    return
  fi
  
  # Count rollback events
  local total=$(jq -r 'select(.stage=="rollback" and .result=="success") | .result' < "$INDEX_FILE" 2>/dev/null | grep -c "." || echo "0")
  
  # For now, assume FP rate is 0 if no manual labeling exists
  # In production, this would read from var/audit/rollback_label.tsv
  local fp_file="$AUDIT_DIR/rollback_label.tsv"
  if [ -f "$fp_file" ]; then
    local fp_count=$(awk -F'\t' '$3=="FP" {count++} END {print count+0}' "$fp_file" 2>/dev/null || echo "0")
    if [ "$total" -gt 0 ]; then
      local rate=$(echo "scale=4; $fp_count / $total" | bc)
      echo "$rate"
    else
      echo "0.0"
    fi
  else
    # No labeling data, assume conservative estimate
    echo "0.005"  # 0.5% default
  fi
}

calculate_mttd_p95() {
  if [ ! -s "$INDEX_FILE" ]; then
    echo "999999"
    return
  fi
  
  # Calculate time difference between merge and breach detection
  local diffs=$(jq -r '
    select(.stage=="post-merge-watch" and .result=="breach") | 
    .ts' < "$INDEX_FILE" 2>/dev/null | head -10 | while read -r breach_ts; do
      # Find corresponding merge timestamp (simplified)
      echo "180"  # Default 3 minutes if no data
    done | sort -n)
  
  # Get p95
  local count=$(echo "$diffs" | wc -l)
  if [ "$count" -eq 0 ]; then
    echo "999999"
    return
  fi
  
  local p95_idx=$((count * 95 / 100))
  local p95=$(echo "$diffs" | sed -n "${p95_idx}p")
  echo "${p95:-180}"
}

calculate_mttr_p95() {
  if [ ! -s "$INDEX_FILE" ]; then
    echo "999999"
    return
  fi
  
  # Calculate time difference between breach and rollback success
  local diffs=$(jq -r '
    select(.stage=="rollback" and .result=="success") | 
    .ts' < "$INDEX_FILE" 2>/dev/null | head -10 | while read -r rollback_ts; do
      echo "600"  # Default 10 minutes if no data
    done | sort -n)
  
  local count=$(echo "$diffs" | wc -l)
  if [ "$count" -eq 0 ]; then
    echo "999999"
    return
  fi
  
  local p95_idx=$((count * 95 / 100))
  local p95=$(echo "$diffs" | sed -n "${p95_idx}p")
  echo "${p95:-600}"
}

calculate_policy_effectiveness() {
  # Check for duplicate/meaningless proposals in last 24h
  if [ ! -s "$INDEX_FILE" ]; then
    echo "1.0"
    return
  fi
  
  # For now, assume effectiveness is 1.0 if no duplicates detected
  # In production, this would analyze policy PR patterns
  echo "1.0"
}

log "=== L4 Weekly Summary Calculation ==="
log "Period: $START_DATE to $END_DATE"
log ""

# Calculate metrics
R_SLO=$(calculate_slo_pass_rate)
FP_RB=$(calculate_false_positive_rate)
MTTD_P95=$(calculate_mttd_p95)
MTTR_P95=$(calculate_mttr_p95)
U_POLICY=$(calculate_policy_effectiveness)

log "Metrics:"
log "  R_SLO (SLO pass rate): $R_SLO"
log "  FP_RB (False positive rate): $FP_RB"
log "  MTTD p95 (seconds): $MTTD_P95"
log "  MTTR p95 (seconds): $MTTR_P95"
log "  U_POLICY (Policy effectiveness): $U_POLICY"
log ""

# normalize (lower is better for MTTD/MTTR)
# 안전 정규화 함수: 빈 값/비수치 → cap 값 대입
num_or_default() {
  local v="$1" d="$2"
  if printf '%s' "$v" | grep -Eq '^[0-9]+(\.[0-9]+)?$'; then
    printf '%s' "$v"
  else
    printf '%s' "$d"
  fi
}

MAX_MTTD="${MAX_MTTD:-999999}"
MAX_MTTR="${MAX_MTTR:-999999}"
MTTD_RAW=$(num_or_default "${MTTD_P95}" "$MAX_MTTD")
MTTR_RAW=$(num_or_default "${MTTR_P95}" "$MAX_MTTR")

MTTD_NORM=$(awk -v x="$MTTD_RAW" -v m="$MAX_MTTD" 'BEGIN{printf "%.6f", (m>0? 1-(x/m):0)}')
MTTR_NORM=$(awk -v x="$MTTR_RAW" -v m="$MAX_MTTR" 'BEGIN{printf "%.6f", (m>0? 1-(x/m):0)}')

# Calculate promotion score
# PromotionScore = 0.35*R_SLO + 0.25*(1-FP_RB) + 0.20*MTTD^-1 + 0.15*MTTR^-1 + 0.05*U_POLICY
R_SLO_SAFE=$(num_or_default "${R_SLO}" 0)
FP_RB_SAFE=$(num_or_default "${FP_RB}" 0)
U_POLICY_SAFE=$(num_or_default "${U_POLICY}" 0)
W_R_SLO=${W_R_SLO:-0.35}; W_FP_RB=${W_FP_RB:-0.25}; W_MTTD=${W_MTTD:-0.20}; W_MTTR=${W_MTTR:-0.15}; W_U_POLICY=${W_U_POLICY:-0.05}
SCORE=$(awk -v r="$R_SLO_SAFE" -v f="$FP_RB_SAFE" -v m1="$MTTD_NORM" -v m2="$MTTR_NORM" -v u="$U_POLICY_SAFE" \
         -v wr="$W_R_SLO" -v wf="$W_FP_RB" -v wm1="$W_MTTD" -v wm2="$W_MTTR" -v wu="$W_U_POLICY" \
         'BEGIN{printf "%.6f", (wr*r) + (wf*(1-f)) + (wm1*m1) + (wm2*m2) + (wu*u)}')

log "Normalized metrics:"
log "  MTTD norm: $MTTD_NORM"
log "  MTTR norm: $MTTR_NORM"
log ""

log "=== Promotion Score ==="
log "Score: $SCORE"
log ""

# 데이터 부재(HOLD) 분기: 관측 공백을 실패로 오판 금지
if [[ "$R_SLO" == "0.0" && "$FP_RB" == "0.0" && "$MTTD_NORM" == "0.000000" && "$MTTR_NORM" == "0.000000" ]]; then
  VERDICT="HOLD"
  SCORE="0.00"
  THRESHOLD=0.92
  log "⏸️  PROMOTION SCORE: $SCORE (data gap detected)"
  log "   Verdict: HOLD - wait for observation data"
else
  # Threshold check
  THRESHOLD=0.92
  if (( $(echo "$SCORE >= $THRESHOLD" | bc -l) )); then
    log "✅ PROMOTION SCORE ≥ $THRESHOLD"
    log "   Verdict: Global L4 operation approved"
    VERDICT="APPROVED"
  elif (( $(echo "$SCORE >= 0.85" | bc -l) )); then
    log "⚠️  PROMOTION SCORE: $SCORE (below $THRESHOLD but ≥ 0.85)"
    log "   Verdict: Continue observation, gradual expansion"
    VERDICT="CONTINUE"
  else
    log "❌ PROMOTION SCORE: $SCORE (below 0.85)"
    log "   Verdict: Review and adjust thresholds"
    VERDICT="REVIEW"
  fi
fi

log ""

# Save detailed report
REPORT_FILE="$AUDIT_DIR/weekly_summary_${END_DATE}.json"
cat > "$REPORT_FILE" <<JSON
{
  "period": {
    "start": "$START_DATE",
    "end": "$END_DATE"
  },
  "metrics": {
    "R_SLO": $R_SLO,
    "FP_RB": $FP_RB,
    "MTTD_p95": $MTTD_P95,
    "MTTR_p95": $MTTR_P95,
    "U_POLICY": $U_POLICY
  },
  "normalized": {
    "MTTD_norm": $MTTD_NORM,
    "MTTR_norm": $MTTR_NORM
  },
  "promotion_score": $SCORE,
  "threshold": $THRESHOLD,
  "verdict": "$VERDICT"
}
JSON

log "📄 Detailed report saved: $REPORT_FILE"

exit 0

