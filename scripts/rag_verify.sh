#!/usr/bin/env bash
set -euo pipefail
shopt -s nullglob

fail=0
ALLOWED='["intake","diagnosis","education","exercise","orders","schedule","policy"]'

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
  if ! jq -e --argjson A "$ALLOWED" '.category as $c | ($A | index($c)) != null' "$f" >/dev/null; then
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
bad_ids=$(jq -r '.id' rag/**/*.jsonl 2>/dev/null | grep -Ev '^[a-z0-9_.-]+\.v[0-9]+(\.[0-9]+)?\.[0-9]{3}$' || true)
if [ -n "${bad_ids:-}" ]; then echo "⚠️ bad id pattern:"; printf "%s\n" "$bad_ids"; fail=1; fi

# 7) body 길이 검증 (카테고리별 권장사항)
# 카테고리별 권장 최소 길이(한글 기준)
MIN_LEN_DEFAULT=200
declare -A MIN_LEN
MIN_LEN[intake]=200
MIN_LEN[education]=220
MIN_LEN[exercise]=180
MIN_LEN[orders]=120
MIN_LEN[schedule]=140
MIN_LEN[policy]=120
MIN_LEN[diagnosis]=200

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
