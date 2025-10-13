#!/usr/bin/env bash
set -euo pipefail

# 공통 상수 로드
source "$(dirname "$0")/_rag_constants.sh"

# 0) JSONL 단일행 보장 검사 (멀티라인 재발 방지)
echo "🔍 JSONL 단일행 검사..."
find rag/ -name "*.jsonl" -print0 | xargs -0 -I{} bash -c '
  L=$(wc -l < "{}"); V=$(jq -c . "{}" | wc -l);
  if [[ "$L" -ne "$V" ]]; then
    echo "❌ multiline or invalid: {} (lines=$L, valid=$V)"
    exit 1
  fi
' || { echo "❌ JSONL 형식 오류 발견"; exit 1; }
echo "✅ JSONL 단일행 검사 통과"
shopt -s nullglob

fail=0

# 1) JSON 문법
while IFS= read -r -d '' f; do
  if ! jq -e . "$f" >/dev/null; then
    echo "❌ JSON parse: $f"; fail=1
  fi
done < <(find rag -type f -name '*.jsonl' -print0)

# 2) 필수 스키마
while IFS= read -r -d '' f; do
  if ! jq -e 'has("id") and has("title") and has("body")
              and (.lang|type=="string")
              and (.clinician_only|type=="boolean")
              and (.patient_facing|type=="boolean")' "$f" >/dev/null; then
    echo "❌ Schema fail: $f"; fail=1
  fi
done < <(find rag -type f -name '*.jsonl' -print0)

# 3) 카테고리 화이트리스트
while IFS= read -r -d '' f; do
  if ! jq -e --argjson A "$ALLOWED_CATEGORIES" '.category as $c | ($A | index($c)) != null' "$f" >/dev/null; then
    echo "⚠️ Non-standard category: $f"; fail=1
  fi
done < <(find rag -type f -name '*.jsonl' -print0)

# 4) id 중복
ids=$(jq -r '.id' rag/**/*.jsonl 2>/dev/null | sort || true)
dups=$(printf "%s\n" "$ids" | uniq -d || true)
if [ -n "${dups:-}" ]; then echo "❌ Duplicate ids:"; printf "%s\n" "$dups"; fail=1; fi

# 5) ISO8601 타임스탬프 검증 (선택적)
# ISO8601 (예: 2025-10-02T11:45:00Z | 2025-10-02T11:45:00+09:00 | 2025-10-02T11:45:00.123+09:00)
ISO_RE='^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}([.][0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})$'

BAD_TS=0
while IFS= read -r ts; do
  [[ "$ts" =~ $ISO_RE ]] || { echo "⚠️ bad timestamp (ISO8601 권장):"; echo "$ts"; BAD_TS=1; }
done < <(jq -r 'select(has("updated_at")) | .updated_at' rag/**/*.jsonl 2>/dev/null || true)

# 6) id 패턴 검증 (영역.주제.v1.xxx)
bad_ids=$(jq -r '.id' rag/**/*.jsonl 2>/dev/null | grep -Ev "$ID_PATTERN" || true)
if [ -n "${bad_ids:-}" ]; then echo "⚠️ bad id pattern:"; printf "%s\n" "$bad_ids"; fail=1; fi

# 7) body 길이 검증 (카테고리별 권장사항)

while IFS=$'\t' read -r cat id body; do
  min=${MIN_LEN[$cat]:-$MIN_LEN_DEFAULT}
  blen=$(echo -n "$body" | wc -m)
  if (( blen < min )); then
    echo "⚠️ short body (<$min chars): $id ($cat)"
  fi
done < <(
  jq -r '[.category,.id,.body] | @tsv' rag/**/*.jsonl 2>/dev/null \
  | sed '/^\t\t$/d'
)

exit $fail
