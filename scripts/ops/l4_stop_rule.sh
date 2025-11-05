#!/usr/bin/env bash
# L4 Stop Rule Check - 48h 후 분기 결정
# Purpose: 48h 후 데이터 상태를 확인하여 계속/보강/중단 결정
# Usage: 매주 일요일 16:00 주간 요약 후 실행

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo /home/duri/DuRiWorkspace)"
cd "${ROOT}"

AUDIT_DIR="${ROOT}/var/audit"
DECISIONS="${AUDIT_DIR}/decisions.ndjson"
LOG_DIR="${AUDIT_DIR}/logs"
mkdir -p "${LOG_DIR}"

ts=$(date +%Y%m%d_%H%M%S)
log_file="${LOG_DIR}/stop_rule_${ts}.log"

{
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] === L4 Stop Rule Check (48h) ==="
  
  if [[ ! -f "${DECISIONS}" ]]; then
    echo "[INFO] No decisions found - initial state, continue observation"
    exit 0
  fi
  
  # 48h 전 시점 계산
  cutoff_ts=$(date -u -d '48 hours ago' '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date -u -v-48H '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || echo "")
  
  # 48h 내 결정들 추출
  recent_decisions=$(jq -r "select(.ts >= \"${cutoff_ts}\") | .decision" "${DECISIONS}" 2>/dev/null || echo "")
  recent_scores=$(jq -r "select(.ts >= \"${cutoff_ts}\") | .score" "${DECISIONS}" 2>/dev/null || echo "")
  
  hold_count=$(echo "$recent_decisions" | grep -c "^HOLD$" || echo 0)
  total_count=$(echo "$recent_decisions" | grep -c "." || echo 0)
  
  echo "Decisions in last 48h: ${total_count}"
  echo "HOLD count: ${hold_count}"
  
  # 분산 계산 (간단 버전: 표준편차 근사)
  if [[ -n "$recent_scores" ]]; then
    score_array=($recent_scores)
    if [[ ${#score_array[@]} -ge 2 ]]; then
      # 간단한 분산 계산
      mean=$(echo "${score_array[@]}" | awk '{sum=0; for(i=1;i<=NF;i++) sum+=$i; print sum/NF}')
      variance=$(echo "${score_array[@]}" | awk -v m="$mean" '{sum=0; for(i=1;i<=NF;i++) sum+=($i-m)^2; print sum/NF}')
      echo "Score variance: ${variance}"
    fi
  fi
  
  # 스톱룰 판정
  if [[ $hold_count -gt 0 ]] && [[ $total_count -ge 1 ]]; then
    # HOLD가 있고, 샘플 수가 최소 요구치(30) 미만
    if [[ $total_count -lt 30 ]]; then
      echo "[ACTION] ACT - Shadow replay needed (n=${total_count} < 30)"
      exit 1  # shadow replay 트리거
    elif [[ $hold_count -eq $total_count ]]; then
      echo "[ACTION] STOP - All recent decisions are HOLD (72h+)"
      exit 2  # 중단 신호
    else
      echo "[ACTION] KEEP - Continue observation (HOLD resolved)"
      exit 0
    fi
  elif [[ $total_count -ge 1 ]]; then
    echo "[ACTION] KEEP - Continue observation (no HOLD)"
    exit 0
  else
    echo "[ACTION] ACT - Need more data (n=${total_count})"
    exit 1  # shadow replay 트리거
  fi
} | tee "${log_file}"

exit 0

