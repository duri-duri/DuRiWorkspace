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
  
  # 1. 최근 48h 내 결정 확인
  if [[ -f "${DECISIONS}" ]]; then
    recent_count=$(jq -r 'select(.ts >= (now - 172800 | todateiso8601)) | .decision' "${DECISIONS}" 2>/dev/null | wc -l || echo 0)
    recent_decision=$(jq -r 'select(.ts >= (now - 172800 | todateiso8601)) | .decision' "${DECISIONS}" 2>/dev/null | tail -1 || echo "")
    
    echo "Recent decisions (48h): ${recent_count}"
    echo "Latest decision: ${recent_decision:-none}"
    
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
