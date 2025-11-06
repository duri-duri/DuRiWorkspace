#!/usr/bin/env bash
# NDJSON Prefilter - 입력 데이터 사전 검증 및 필터링
# Purpose: 원본 데이터를 사전 검증하여 불량 라인을 사전에 차단
# Usage: ndjson_prefilter.sh <input> <output> [--quarantine <dir>]

set -euo pipefail

SRC="${1:-var/audit/decisions.ndjson}"
OUT="${2:-var/audit/decisions.pref.ndjson}"
QUARANTINE_DIR="${3:-var/audit/quarantine}"

mkdir -p "$(dirname "$OUT")"
mkdir -p "$QUARANTINE_DIR"

TMP="$(mktemp)"
QUARANTINE_FILE="${QUARANTINE_DIR}/rejected_$(date +%Y%m%d_%H%M%S).ndjson"
trap 'rm -f "$TMP"' EXIT

# 필수 키 집합
REQUIRED_KEYS='["ts","decision"]'
ALLOW_DECISIONS='["GO","NO-GO","REVIEW","HOLD","HEARTBEAT","APPROVED","CONTINUE"]'

VALID=0
REJECTED=0

# 라인별 처리
while IFS= read -r line || [[ -n "$line" ]]; do
  # 빈 라인 스킵
  [[ -z "${line// }" ]] && continue
  
  # JSON 유효성 검증
  if ! echo "$line" | jq -e . >/dev/null 2>&1; then
    echo "$line" >> "$QUARANTINE_FILE"
    REJECTED=$((REJECTED + 1))
    continue
  fi
  
  # 스키마 검증
  if ! echo "$line" | jq -e "
    type==\"object\" and
    has(\"ts\") and
    has(\"decision\") and
    (.decision | tostring | ascii_upcase) as \$d | 
    ([\"GO\",\"NO-GO\",\"REVIEW\",\"HOLD\",\"HEARTBEAT\",\"APPROVED\",\"CONTINUE\"] | index(\$d) != null)
  " >/dev/null 2>&1; then
    echo "$line" >> "$QUARANTINE_FILE"
    REJECTED=$((REJECTED + 1))
    continue
  fi
  
  # 통과한 라인만 출력
  echo "$line" >> "$TMP"
  VALID=$((VALID + 1))
done < "$SRC"

mv -f "$TMP" "$OUT"
chmod 0644 "$OUT"

echo "[OK] prefiltered -> $OUT ($VALID valid, $REJECTED rejected)" >&2
echo "$REJECTED" > "${QUARANTINE_DIR}/.rejected_count"

