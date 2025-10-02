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
bad_timestamps=$(jq -r 'select(has("updated_at")) | .updated_at' rag/**/*.jsonl 2>/dev/null | grep -Ev '^\d{4}-\d{2}-\d{2}T.*\+\d{2}:\d{2}$' || true)
if [ -n "${bad_timestamps:-}" ]; then echo "⚠️ bad timestamp (ISO8601 권장):"; printf "%s\n" "$bad_timestamps"; fi

# 6) id 패턴 검증 (영역.주제.v1.xxx)
bad_ids=$(jq -r '.id' rag/**/*.jsonl 2>/dev/null | grep -Ev '^[a-z0-9_.-]+\.v[0-9]+(\.[0-9]+)?\.[0-9]{3}$' || true)
if [ -n "${bad_ids:-}" ]; then echo "⚠️ bad id pattern:"; printf "%s\n" "$bad_ids"; fail=1; fi

# 7) body 길이 검증 (검색 품질, 권장사항)
short_bodies=$(jq -r '.id + "\t" + (.body|tostring)' rag/**/*.jsonl 2>/dev/null | awk -F'\t' '{ if(length($2) < 200) print $1 }' || true)
if [ -n "${short_bodies:-}" ]; then echo "⚠️ short body (<200 chars, 검색 품질 권장):"; printf "%s\n" "$short_bodies"; fi

exit $fail
