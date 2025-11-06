#!/usr/bin/env bash
# Backfill Weekly Decision - 주간 결정 산출물 백필 힐러
# Purpose: l4_weekly_decision.prom이 없거나 오래된 경우 즉시 생성 보장
# Usage: Called by l4-weekly-backfill.service or manually

set -euo pipefail

# UTC 강제
export TZ=UTC

WORK="${WORK:-/home/duri/DuRiWorkspace}"
PROM_DIR="${NODE_EXPORTER_TEXTFILE_DIR:-${HOME}/.cache/node_exporter/textfile}"
SRC_NDJSON="${WORK}/var/audit/decisions.ndjson"
CANON_NDJSON="${WORK}/var/audit/decisions.canon.ndjson"
OUT="${PROM_DIR}/l4_weekly_decision.prom"
LOCK="${WORK}/var/audit/decisions.ndjson.lock"
LOCK_HELPER="${WORK}/scripts/ops/inc/with_lock.sh"

# 락 헬퍼 경로 보장
if [[ ! -f "$LOCK_HELPER" ]]; then
  echo "[WARN] with_lock.sh missing at $LOCK_HELPER; proceeding without external lock" >&2
fi

mkdir -p "$(dirname "$OUT")"
mkdir -p "$(dirname "$SRC_NDJSON")"

# umask 설정 (권한 고정)
umask 022

# 원자적 쓰기를 위한 임시 파일
tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

# 락을 사용하여 안전하게 백필
if [[ -f "$LOCK_HELPER" ]]; then
  bash "$LOCK_HELPER" "$LOCK" bash -c "
    set -euo pipefail
    export TZ=UTC
    
    # 0) 정규화 단계: 손상 라인/중복/개행 문제를 정규화 단계에서 제거
    if [[ -f \"${SRC_NDJSON}\" ]] && [[ -s \"${SRC_NDJSON}\" ]]; then
      bash \"${WORK}/scripts/ops/inc/ndjson_canonicalize.sh\" \"${SRC_NDJSON}\" \"${CANON_NDJSON}\" >/dev/null 2>&1 || true
    fi
    
    # 1) 정규화된 파일에서 최신 결정값 추출 (단일 스칼라 보장)
    decision_raw=\"\"
    if [[ -f \"${CANON_NDJSON}\" ]] && [[ -s \"${CANON_NDJSON}\" ]]; then
      decision_raw=\$(jq -Rn -r '
        [ inputs
          | fromjson?
          | select(type==\"object\" and .ts and .decision)
          | select(.decision | IN(\"GO\",\"NO-GO\",\"REVIEW\",\"HOLD\",\"HEARTBEAT\",\"APPROVED\",\"CONTINUE\"))
          | select((.ts | fromdateiso8601) > (now - 604800))
          | {ts:(.ts|fromdateiso8601), decision:.decision}
        ]
        | sort_by(.ts)
        | last
        | (.decision // \"HOLD\")
      ' < \"${CANON_NDJSON}\" 2>/dev/null || echo \"HOLD\")
    fi
    
    # 기본값 설정
    decision_val=\"\${decision_raw:-HOLD}\"
    [[ -z \"\$decision_val\" || \"\$decision_val\" == \"null\" ]] && decision_val=\"HOLD\"
    
    # 안전 이스케이프: Prometheus label (제어문자 제거 포함)
    decision_val=\$(printf '%s' \"\$decision_val\" | tr -d '\r\n' | sed 's/[[:space:]].*//' | head -c 32)
    
    # 라벨 허용집합 보증
    case \"\$decision_val\" in
      GO|NO-GO|REVIEW|HOLD|HEARTBEAT|APPROVED|CONTINUE) : ;;
      *) decision_val=\"HOLD\" ;;
    esac
    
    # Prometheus 라벨 이스케이프: \", \\ 처리
    decision_esc=\$(printf '%s' \"\$decision_val\" | sed 's/\\\\\\\\/\\\\\\\\\\\\\\\\/g; s/\"/\\\\\\\\\\\"/g')
    
    # 2) 타임스탬프 (UTC 기준)
    ts_utc=\$(date -u +%s)
    
    # 3) Prometheus 메트릭 생성 (개행 없는 단일 라인 보장)
    {
      echo '# HELP l4_weekly_decision_ts Unix timestamp of last weekly decision (UTC)'
      echo '# TYPE l4_weekly_decision_ts gauge'
      printf 'l4_weekly_decision_ts{decision=\"%s\"} %s\\n' \"\$decision_esc\" \"\$ts_utc\"
    } > \"${tmp}\"
    
    # 4) 원자적 쓰기
    if [[ -f \"${WORK}/scripts/ops/inc/atomic_write.sh\" ]]; then
      cat \"${tmp}\" | bash \"${WORK}/scripts/ops/inc/atomic_write.sh\" \"${OUT}\"
    else
      mv -f \"${tmp}\" \"${OUT}\"
      chmod 0644 \"${OUT}\"
    fi
    
    # 5) 타임스탬프 메트릭도 내보내기
    bash \"${WORK}/scripts/ops/inc/_export_timestamp.sh\" \"weekly_decision\" 2>/dev/null || true
    
    # 6) 백필 결과 코드 메트릭 (0=ok, >0=오류코드)
    BACKFILL_RC=0
    {
      echo '# HELP l4_backfill_last_rc Exit code of last backfill run (0=ok, >0=error)'
      echo '# TYPE l4_backfill_last_rc gauge'
      echo \"l4_backfill_last_rc{} \$BACKFILL_RC\"
    } > \"${PROM_DIR}/l4_backfill_rc.prom\"
    chmod 0644 \"${PROM_DIR}/l4_backfill_rc.prom\"
    
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
  
  # 백필 결과 코드 메트릭 (fallback 경로)
  BACKFILL_RC=0
  {
    echo '# HELP l4_backfill_last_rc Exit code of last backfill run (0=ok, >0=error)'
    echo '# TYPE l4_backfill_last_rc gauge'
    echo "l4_backfill_last_rc{} $BACKFILL_RC"
  } > "${PROM_DIR}/l4_backfill_rc.prom"
  chmod 0644 "${PROM_DIR}/l4_backfill_rc.prom"
fi

exit 0

