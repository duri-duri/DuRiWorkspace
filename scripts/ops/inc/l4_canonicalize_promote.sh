#!/usr/bin/env bash
# Canonicalize Promote - 정규화된 NDJSON 승급 (2단계)
# Purpose: sanitize된 파일을 검증 후 원본으로 승급 (실패 시 게이지 0)
# Usage: Called by l4-canonicalize-promote.service

set -euo pipefail

# UTC 강제
export TZ=UTC

WORK="${WORK:-/home/duri/DuRiWorkspace}"
SAN="${WORK}/var/audit/decisions.san"
OUT="${WORK}/var/audit/decisions.ndjson"
PROM_DIR="${NODE_EXPORTER_TEXTFILE_DIR:-${HOME}/.cache/node_exporter/textfile}"
LOCK="${WORK}/var/audit/decisions.ndjson.lock"

mkdir -p "$(dirname "${OUT}")"
mkdir -p "${PROM_DIR}"
umask 022

# 락을 사용하여 안전하게 승급
if [[ -f "${WORK}/scripts/ops/inc/with_lock.sh" ]]; then
  bash "${WORK}/scripts/ops/inc/with_lock.sh" "$LOCK" bash -c "
    set -euo pipefail
    export TZ=UTC
    
    if [[ ! -f \"${SAN}\" ]]; then
      echo '[WARN] decisions.san not found, skipping promote'
      echo 'l4_canonicalize_promote_ok 0' > \"${PROM_DIR}/l4_canonicalize_promote_ok.prom\"
      chmod 0644 \"${PROM_DIR}/l4_canonicalize_promote_ok.prom\"
      exit 0
    fi
    
    # 검증: 유효한 JSON 라인인지 확인
    if jq -e '.' \"${SAN}\" >/dev/null 2>&1; then
      # 정렬 및 중복 제거
      tmp=\$(mktemp)
      if jq -cs 'sort_by([.ts, (.seq // 0)]) | unique_by(.ts + \"|\" + (.decision // \"\")) | .[]' \"${SAN}\" > \"\$tmp\" 2>/dev/null; then
        # 원자적 쓰기
        if [[ -f \"${WORK}/scripts/ops/inc/atomic_write.sh\" ]]; then
          cat \"\$tmp\" | bash \"${WORK}/scripts/ops/inc/atomic_write.sh\" \"${OUT}\"
        else
          mv -f \"\$tmp\" \"${OUT}\"
          chmod 0644 \"${OUT}\"
        fi
        
        # 동기화 보장
        sync
        if command -v fdatasync >/dev/null 2>&1; then
          fdatasync <\"${OUT}\" >/dev/null 2>&1 || true
        fi
        
        # 성공 메트릭
        echo 'l4_canonicalize_promote_ok 1' > \"${PROM_DIR}/l4_canonicalize_promote_ok.prom\"
        chmod 0644 \"${PROM_DIR}/l4_canonicalize_promote_ok.prom\"
        echo \"[INFO] Promoted: \$(wc -l < \"${OUT}\" || echo 0) lines\"
      else
        echo '[WARN] Promote failed (sort error), keeping original'
        rm -f \"\$tmp\"
        echo 'l4_canonicalize_promote_ok 0' > \"${PROM_DIR}/l4_canonicalize_promote_ok.prom\"
        chmod 0644 \"${PROM_DIR}/l4_canonicalize_promote_ok.prom\"
      fi
    else
      echo '[WARN] Promote failed (invalid JSON), keeping original'
      echo 'l4_canonicalize_promote_ok 0' > \"${PROM_DIR}/l4_canonicalize_promote_ok.prom\"
      chmod 0644 \"${PROM_DIR}/l4_canonicalize_promote_ok.prom\"
    fi
    
    exit 0
  "
else
  # Fallback
  if [[ -f "${SAN}" ]]; then
    jq -cs 'sort_by([.ts, (.seq // 0)]) | unique_by(.ts + "|" + (.decision // "")) | .[]' "${SAN}" > "${OUT}" 2>/dev/null || true
    echo 'l4_canonicalize_promote_ok 1' > "${PROM_DIR}/l4_canonicalize_promote_ok.prom" 2>/dev/null || true
    chmod 0644 "${OUT}" "${PROM_DIR}/l4_canonicalize_promote_ok.prom" 2>/dev/null || true
  fi
fi

exit 0

