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

exit $fail
