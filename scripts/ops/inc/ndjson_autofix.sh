#!/usr/bin/env bash
# NDJSON Autofix - 자동 수정형 정규화
# Purpose: 일반적인 오류 패턴을 자동으로 수정하여 복구 시도
# Usage: ndjson_autofix.sh <input> <output> [--quarantine <dir>]

set -euo pipefail

SRC="${1:-var/audit/decisions.ndjson}"
OUT="${2:-var/audit/decisions.fixed.ndjson}"
QUARANTINE_DIR="${3:-var/audit/quarantine}"

mkdir -p "$(dirname "$OUT")"
mkdir -p "$QUARANTINE_DIR"

TMP="$(mktemp)"
QUARANTINE_FILE="${QUARANTINE_DIR}/unfixable_$(date +%Y%m%d_%H%M%S).ndjson"
trap 'rm -f "$TMP"' EXIT

FIXED=0
UNFIXABLE=0

# 라인별 처리
while IFS= read -r line || [[ -n "$line" ]]; do
  [[ -z "${line// }" ]] && continue
  
  # 1차: 원본 JSON 검증
  if echo "$line" | jq -e . >/dev/null 2>&1; then
    echo "$line" >> "$TMP"
    FIXED=$((FIXED + 1))
    continue
  fi
  
  # 2차: 자동 수정 시도
  fixed_line="$line"
  
  # 수정 패턴 1: 트레일링 콤마 제거
  fixed_line=$(echo "$fixed_line" | sed -E 's/,([[:space:]]*[}\]])/\1/g')
  
  # 수정 패턴 2: 제어 문자 제거
  fixed_line=$(echo "$fixed_line" | tr -d '\000-\010\013\014\016-\037')
  
  # 수정 패턴 3: 이중 따옴표 누락 보정 (간단한 패턴만)
  if ! echo "$fixed_line" | grep -qE '^\{.*\}$'; then
    # JSON 객체 형식이 아니면 수정 시도
    fixed_line=$(echo "$fixed_line" | sed -E 's/([^"]):([^",}]+)/\1:"\2"/g' 2>/dev/null || echo "$fixed_line")
  fi
  
  # 수정 패턴 4: decision 소문자 → 대문자
  fixed_line=$(echo "$fixed_line" | sed -E 's/"decision"\s*:\s*"([^"]+)"/"decision":"\U\1"/g')
  
  # 수정 후 재검증
  if echo "$fixed_line" | jq -e . >/dev/null 2>&1; then
    echo "$fixed_line" >> "$TMP"
    FIXED=$((FIXED + 1))
  else
    echo "$line" >> "$QUARANTINE_FILE"
    UNFIXABLE=$((UNFIXABLE + 1))
  fi
done < "$SRC"

mv -f "$TMP" "$OUT"
chmod 0644 "$OUT"

echo "[OK] autofixed -> $OUT ($FIXED fixed, $UNFIXABLE unfixable)" >&2

