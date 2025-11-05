#!/usr/bin/env bash
# Canonicalize Sanitize - NDJSON 오염 라인 드롭 (1단계)
# Purpose: 오염된 라인을 드롭하고 .san 파일 생성 (항상 exit 0)
# Usage: Called by l4-canonicalize-sanitize.service

set -euo pipefail

WORK="${WORK:-/home/duri/DuRiWorkspace}"
IN="${WORK}/var/audit/decisions.ndjson"
SAN="${WORK}/var/audit/decisions.san"
LOCK="${WORK}/var/audit/decisions.ndjson.lock"

mkdir -p "$(dirname "${IN}")"
umask 022

# 락을 사용하여 안전하게 정규화
if [[ -f "${WORK}/scripts/ops/inc/with_lock.sh" ]]; then
  bash "${WORK}/scripts/ops/inc/with_lock.sh" "$LOCK" bash -c "
    set -euo pipefail
    
    if [[ ! -f \"${IN}\" ]]; then
      echo '[WARN] decisions.ndjson not found, skipping sanitize'
      exit 0
    fi
    
    # 입력 스냅샷 생성 (읽는 동안 업스트림 변경 무관)
    SNAP=\$(mktemp)
    cp \"${IN}\" \"\$SNAP\"
    
    # 허용 규칙: 단일 JSON 라인만 통과
    # 드롭: 빈 줄, 주석, malformed JSON
    total=0
    good=0
    
    if jq -c '
      if type==\"array\" then . else [.] end
      | map(select(type==\"object\" and .ts != null))
      | map(select(.decision | IN(\"GO\",\"NO-GO\",\"REVIEW\",\"HOLD\",\"HEARTBEAT\",\"APPROVED\",\"CONTINUE\")))
      | map(select((.ts | fromdateiso8601) > 0))
    ' \"\$SNAP\" > \"${SAN}\" 2>/dev/null; then
      total=\$(wc -l < \"\$SNAP\" || echo 0)
      good=\$(wc -l < \"${SAN}\" || echo 0)
      bad=\$((total > good ? total - good : 0))
      echo \"[INFO] Sanitized: \$good lines (dropped: \$bad)\"
    else
      echo \"[WARN] Sanitize failed, keeping original\"
      cp \"\$SNAP\" \"${SAN}\"
    fi
    
    rm -f \"\$SNAP\"
    chmod 0644 \"${SAN}\" 2>/dev/null || true
    exit 0
  "
else
  # Fallback
  if [[ -f "${IN}" ]]; then
    jq -c '
      if type=="array" then . else [.] end
      | map(select(type=="object" and .ts != null))
    ' "${IN}" > "${SAN}" 2>/dev/null || cp "${IN}" "${SAN}"
    chmod 0644 "${SAN}" 2>/dev/null || true
  fi
fi

exit 0

