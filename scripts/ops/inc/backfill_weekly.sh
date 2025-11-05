#!/usr/bin/env bash
# Backfill Weekly Decision - 주간 결정 산출물 백필 힐러
# Purpose: l4_weekly_decision.prom이 없거나 오래된 경우 즉시 생성 보장
# Usage: Called by l4-weekly-backfill.service or manually

set -euo pipefail

WORK="${WORK:-/home/duri/DuRiWorkspace}"
PROM_DIR="${NODE_EXPORTER_TEXTFILE_DIR:-${HOME}/.cache/node_exporter/textfile}"
SRC_NDJSON="${WORK}/var/audit/decisions.ndjson"
OUT="${PROM_DIR}/l4_weekly_decision.prom"
LOCK="${WORK}/var/audit/decisions.ndjson.lock"

mkdir -p "$(dirname "$OUT")"
mkdir -p "$(dirname "$SRC_NDJSON")"

# umask 설정 (권한 고정)
umask 022

# 원자적 쓰기를 위한 임시 파일
tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

# 락을 사용하여 안전하게 백필
if [[ -f "${WORK}/scripts/ops/inc/with_lock.sh" ]]; then
  bash "${WORK}/scripts/ops/inc/with_lock.sh" "$LOCK" bash -c "
    set -euo pipefail
    
    # 1) 최근 7일 내 결정 스캔 → 가장 최신 결정 추출
    decision_val=\"HOLD\"
    if [[ -f \"${SRC_NDJSON}\" ]]; then
      decision_val=\$(jq -r '
        select(type==\"object\" and .ts and .decision)
        | select(.decision | IN(\"GO\",\"NO-GO\",\"REVIEW\",\"HOLD\",\"HEARTBEAT\",\"APPROVED\",\"CONTINUE\"))
        | select((.ts | fromdateiso8601) > (now - 604800))
        | .decision
      ' \"${SRC_NDJSON}\" 2>/dev/null | tail -1 || echo \"HOLD\")
      
      if [[ -z \"\$decision_val\" ]]; then
        decision_val=\"HOLD\"
      fi
    fi
    
    # 2) 타임스탬프 생성 (UTC 기준)
    ts_utc=\$(date -u +%s)
    
    # 3) Prometheus 메트릭 생성
    cat > \"${tmp}\" <<EOF
# HELP l4_weekly_decision_ts Unix timestamp of last weekly decision (UTC)
# TYPE l4_weekly_decision_ts gauge
l4_weekly_decision_ts{decision=\"\$decision_val\"} \$ts_utc
EOF
    
    # 4) 원자적 쓰기
    if [[ -f \"${WORK}/scripts/ops/inc/atomic_write.sh\" ]]; then
      cat \"${tmp}\" | bash \"${WORK}/scripts/ops/inc/atomic_write.sh\" \"${OUT}\"
    else
      mv -f \"${tmp}\" \"${OUT}\"
      chmod 0644 \"${OUT}\"
    fi
    
    # 5) 타임스탬프 메트릭도 내보내기
    bash \"${WORK}/scripts/ops/inc/_export_timestamp.sh\" \"weekly_decision\" 2>/dev/null || true
    
    echo \"[OK] Weekly decision backfilled: decision=\$decision_val, ts=\$ts_utc\"
    exit 0
  "
else
  # Fallback: 락 없이 실행
  ts_utc=$(date -u +%s)
  cat > "$tmp" <<EOF
# HELP l4_weekly_decision_ts Unix timestamp of last weekly decision (UTC)
# TYPE l4_weekly_decision_ts gauge
l4_weekly_decision_ts{decision="HOLD"} $ts_utc
EOF
  mv -f "$tmp" "$OUT"
  chmod 0644 "$OUT"
  bash "${WORK}/scripts/ops/inc/_export_timestamp.sh" "weekly_decision" 2>/dev/null || true
fi

exit 0

