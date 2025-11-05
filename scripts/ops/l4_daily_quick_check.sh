#!/usr/bin/env bash
# L4 Daily Quick Check - HOLD 감지 및 데이터 공백 체크
# Purpose: 매일 09:10에 빠른 체크하여 HOLD 상태를 24h 내 감지
# Usage: Called by systemd timer

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo /home/duri/DuRiWorkspace)"
cd "${ROOT}"

AUDIT_DIR="${ROOT}/var/audit"
DECISIONS="${AUDIT_DIR}/decisions.ndjson"
LOG_DIR="${AUDIT_DIR}/logs"
mkdir -p "${LOG_DIR}"

ts=$(date +%Y%m%d_%H%M%S)
log_file="${LOG_DIR}/quick_check_${ts}.log"

{
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] === L4 Daily Quick Check ==="
  
  # 1. 최근 48h 내 결정 확인 (NDJSON 파싱 안전화 및 정렬 보장)
  if [[ -f "${DECISIONS}" ]]; then
    # ISO8601 초 단위 Z로 48h 전 시점 계산
    cutoff_ts=$(date -u -d '48 hours ago' '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date -u -v-48H '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || echo "")
    
    # 라인별 필터링 (비JSON 라인/빈줄 무시) 후 정렬 → 최신 결정 추출
    recent_decisions=$(tail -n 50 "${DECISIONS}" | jq -cr 'select(type=="object" and .ts and .decision) | select(.ts >= "'"${cutoff_ts}"'") | .decision' 2>/dev/null || echo "")
    recent_count=$(echo "$recent_decisions" | grep -c "." || echo 0)
    recent_decision=$(echo "$recent_decisions" | tail -n 1 || echo "")
    
    # 최근 3개 타임스탬프 확인 (파싱 오류 방지)
    recent_ts=$(tail -n 50 "${DECISIONS}" | jq -cr 'select(type=="object" and .ts)|.ts' 2>/dev/null | tail -n 3 || echo "")
    
    echo "Recent decisions (48h): ${recent_count}"
    echo "Latest decision: ${recent_decision:-none}"
    if [[ -n "$recent_ts" ]]; then
      echo "Recent timestamps:"
      echo "$recent_ts" | while read -r ts; do echo "  - $ts"; done
    fi
    
    if [[ "$recent_decision" == "HOLD" ]]; then
      echo "[WARN] HOLD detected in last 48h - shadow replay may be needed"
    fi
  else
    echo "[INFO] No decisions.ndjson found - initial state"
  fi
  
  # 2. 일일 관찰 로그 확인
  daily_logs=$(ls -1t "${LOG_DIR}"/daily_*.log 2>/dev/null | head -1 || echo "")
  if [[ -n "$daily_logs" ]]; then
    echo "Latest daily log: $(basename "$daily_logs")"
  else
    echo "[WARN] No daily observation logs found"
  fi
  
  # 3. Prometheus 메트릭 확인 (설정된 경우)
  if [[ -n "${NODE_EXPORTER_TEXTFILE_DIR:-}" ]] && [[ -f "${NODE_EXPORTER_TEXTFILE_DIR}/l4_weekly_decision.prom" ]]; then
    current_metric=$(grep -E '^l4_weekly_decision' "${NODE_EXPORTER_TEXTFILE_DIR}/l4_weekly_decision.prom" | awk '{print $2}' || echo "")
    echo "Current Prometheus metric: ${current_metric}"
  fi
  
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] === Quick Check Complete ==="
} | tee "${log_file}"

exit 0
