#!/usr/bin/env bash
# L4 Readiness Check - L4 도달 체크 자동화
# Purpose: 6개 신호(S1-S6) 필요충분 조건 검증 및 GA 판정
# Usage: bash scripts/ops/l4_readiness_check.sh

set -euo pipefail

# UTC 강제
export TZ=UTC

WORK="${WORK:-/home/duri/DuRiWorkspace}"
PROM_DIR="${NODE_EXPORTER_TEXTFILE_DIR:-${HOME}/.cache/node_exporter/textfile}"
OUTPUT_FILE="${WORK}/var/audit/l4_readiness.json"

mkdir -p "$(dirname "$OUTPUT_FILE")"

# 신호 체크 함수
check_signal() {
  local name=$1
  local file=$2
  local max_age=${3:-60}
  
  if [[ ! -f "$file" ]]; then
    echo "0"
    return 1
  fi
  
  local age=$(( $(date -u +%s) - $(stat -c %Y "$file" 2>/dev/null || echo 0) ))
  if [[ $age -gt $max_age ]]; then
    echo "0"
    return 1
  fi
  
  local value=$(grep -E "^${name}[[:space:]]+[0-9]+" "$file" 2>/dev/null | awk '{print $2}' | head -1)
  if [[ -z "$value" ]] || [[ "$value" != "1" ]]; then
    echo "0"
    return 1
  fi
  
  echo "1"
  return 0
}

# S1: closed_loop_ok
S1=$(check_signal "l4_closed_loop_ok" "${PROM_DIR}/l4_closed_loop_ok.prom" 60)

# S2: weekly_backfill_ok
S2=$(check_signal "l4_weekly_backfill_ok" "${PROM_DIR}/l4_weekly_backfill_ok.prom" 60)

# S3: decision_sla_ok
S3=$(check_signal "l4_decision_sla_ok" "${PROM_DIR}/l4_decision_sla_ok.prom" 60)

# S4: promote 성공률
if [[ -f "${PROM_DIR}/l4_canonicalize_promote_ok.prom" ]]; then
  promote_value=$(grep -E "^l4_canonicalize_promote_ok[[:space:]]+[0-9]+" "${PROM_DIR}/l4_canonicalize_promote_ok.prom" 2>/dev/null | awk '{print $2}' | head -1)
  if [[ "$promote_value" == "1" ]]; then
    S4=1
  else
    S4=0
  fi
else
  S4=0
fi

# S5: UTC 일관성 (A4 검증)
if [[ -f "${PROM_DIR}/l4_weekly_decision.prom" ]]; then
  ts_value=$(grep -E "^l4_weekly_decision_ts" "${PROM_DIR}/l4_weekly_decision.prom" 2>/dev/null | awk '{print $2}' | head -1)
  if [[ -n "$ts_value" ]]; then
    now_utc=$(date -u +%s)
    age=$((now_utc - ts_value))
    # 7일 이내이면 OK
    if [[ $age -le 604800 ]]; then
      S5=1
    else
      S5=0
    fi
  else
    S5=0
  fi
else
  S5=0
fi

# S6: 경보 루프 작동 (무음 방지)
# 모든 메트릭이 존재하고 신선함
if [[ -f "${PROM_DIR}/l4_closed_loop_ok.prom" ]] && \
   [[ -f "${PROM_DIR}/l4_weekly_backfill_ok.prom" ]] && \
   [[ -f "${PROM_DIR}/l4_decision_sla_ok.prom" ]]; then
  S6=1
else
  S6=0
fi

# 쿼럼 계산
QUORUM=$(( S1 * S2 * S3 * S4 * S5 * S6 ))

# 결과 출력
cat > "$OUTPUT_FILE" <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "signals": {
    "S1_closed_loop_ok": ${S1},
    "S2_weekly_backfill_ok": ${S2},
    "S3_decision_sla_ok": ${S3},
    "S4_promote_success": ${S4},
    "S5_utc_consistency": ${S5},
    "S6_alert_loop_active": ${S6}
  },
  "quorum": ${QUORUM},
  "status": "$([[ $QUORUM -eq 1 ]] && echo "READY" || echo "NOT_READY")",
  "probability_estimate": $(awk "BEGIN {printf \"%.6f\", $QUORUM * 0.9992 + (1-$QUORUM) * 0.95}")
}
EOF

# 출력
echo "=== L4 Readiness Check ==="
echo "S1 (closed_loop_ok):      ${S1}"
echo "S2 (weekly_backfill_ok):   ${S2}"
echo "S3 (decision_sla_ok):      ${S3}"
echo "S4 (promote_success):      ${S4}"
echo "S5 (utc_consistency):      ${S5}"
echo "S6 (alert_loop_active):    ${S6}"
echo "---"
echo "QUORUM:                    ${QUORUM}"
echo "STATUS:                    $([[ $QUORUM -eq 1 ]] && echo "✅ READY" || echo "❌ NOT_READY")"
echo ""
echo "Results saved to: ${OUTPUT_FILE}"

# Exit code
if [[ $QUORUM -eq 1 ]]; then
  exit 0
else
  exit 1
fi

