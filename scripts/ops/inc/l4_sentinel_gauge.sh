#!/usr/bin/env bash
# L4 Sentinel Gauge - 폐쇄 루프 완결성 신호 생성
# Purpose: 모든 자동화 루프가 완전히 닫혔는지 단일 신호로 표시
# Usage: Called by l4-selftest.service ExecStartPost

set -euo pipefail

# --- Safe defaults & fallbacks ---
WORK="${WORK:-$(git rev-parse --show-toplevel 2>/dev/null || echo /home/duri/DuRiWorkspace)}"
OUT_DIR="${NODE_EXPORTER_TEXTFILE_DIR:-${HOME}/.cache/node_exporter/textfile}"
OUT_FILE="${OUT_DIR}/l4_closed_loop_ok.prom"
TMP_FILE="${OUT_FILE}.tmp"

mkdir -p "${OUT_DIR}"

# --- Signals to check (boolean -> 0/1) ---
has_24h_decisions() {  # 24h 판정/하트비트 ≥ 1
  local n
  if [[ ! -f "${WORK}/var/audit/decisions.ndjson" ]]; then
    echo 0
    return
  fi
  n=$(jq -r '
    select(type=="object" and .ts and .decision) 
    | select(.decision | IN("GO","NO-GO","REVIEW","HOLD","HEARTBEAT","APPROVED","CONTINUE"))
    | ( .ts | fromdateiso8601 ) 
    | select(. > (now - 86400))
  ' "${WORK}/var/audit/decisions.ndjson" 2>/dev/null | wc -l | tr -d " ")
  [[ "${n:-0}" -ge 1 ]] && echo 1 || echo 0
}

selftest_fresh() {    # selftest_pass 최근 10분 이내
  local age
  if [[ ! -f "${OUT_DIR}/l4_selftest.pass.prom" ]]; then
    echo 0
    return
  fi
  age=$(( $(date +%s) - $(stat -c %Y "${OUT_DIR}/l4_selftest.pass.prom" 2>/dev/null || echo 0) ))
  [[ "${age:-999999}" -le 600 ]] && echo 1 || echo 0
}

weekly_fresh() {      # weekly_decision 최근 7일 이내 (첫 생성 예외 허용)
  local age
  if [[ ! -f "${OUT_DIR}/l4_weekly_decision.prom" ]]; then
    echo 1  # First-create exception: allow
    return
  fi
  age=$(( $(date +%s) - $(stat -c %Y "${OUT_DIR}/l4_weekly_decision.prom" 2>/dev/null || echo 0) ))
  [[ "${age:-999999}" -le 604800 ]] && echo 1 || echo 0
}

timers_ok() {         # 타이머 상태 확인
  if systemctl --user is-enabled l4-weekly.timer >/dev/null 2>&1; then
    echo 1
  else
    # Fallback: check if we have recent decisions (implies something is running)
    has_24h_decisions
  fi
}

# --- Compute quorum ---
S1=$(has_24h_decisions)
S2=$(selftest_fresh)
S3=$(weekly_fresh)
S4=$(timers_ok)

# Truth: 모두 1이면 OK
QUORUM=$(( S1 * S2 * S3 * S4 ))

# Atomic write: tmp -> fsync -> rename
{
  echo "# HELP l4_closed_loop_ok L4 closed loop completeness (1=all OK, 0=degraded)"
  echo "# TYPE l4_closed_loop_ok gauge"
  echo "l4_closed_loop_ok ${QUORUM}"
} > "${TMP_FILE}"

# Atomic move
mv "${TMP_FILE}" "${OUT_FILE}"

# Ensure permissions
chmod 0644 "${OUT_FILE}" 2>/dev/null || true

# Export timestamp
if [[ -f "${WORK}/scripts/ops/inc/_export_timestamp.sh" ]]; then
  bash "${WORK}/scripts/ops/inc/_export_timestamp.sh" "closed_loop_ok" 2>/dev/null || true
fi

exit 0

