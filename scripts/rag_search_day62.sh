#!/usr/bin/env bash
set -euo pipefail

command -v jq >/dev/null || { echo "[err] jq not found"; exit 2; }

QUERY="${1:-요통}"
CAT="${2:-}"       # intake / education / ...
PF="${3:-}"        # "true" | "false" | ""(무시)
RANK="${4:-0}"     # "1" for ranking, "0" for default

if [[ -z "$QUERY" ]]; then
  echo "사용법: bash scripts/rag_search_day62.sh '<검색어>' [카테고리] [patient_facing] [rank]" >&2
  exit 1
fi

echo "🔍 RAG 검색: '$QUERY'"
[[ -n "$CAT" ]] && echo "   카테고리: $CAT"
[[ -n "$PF"  ]] && echo "   환자용: $PF"
[[ "$RANK" == "1" ]] && echo "   랭킹 ON"
echo

# 1) 기본 검색 (기존 방식)
find rag/ -name "*.jsonl" -print0 \
| xargs -0 -I{} jq -r --arg q "$QUERY" --arg cat "$CAT" --arg pf "$PF" '
  . as $doc
  | select(type=="object")
  | select(has("title") and has("body"))
  | select(($cat=="" or .category==$cat))
  | select(($pf==""  or (.patient_facing==($pf=="true"))))
  | select(((.title // "") + " " + ((.bullets // []) | join(" ")) + " " + ((.tags // []) | join(" "))) | test($q; "i"))
  . as $r
  | "📄 \($r.id // "-"): \($r.title // "-")\n   카테고리: \($r.category // "-")\n   환자용: \($r.patient_facing // false)\n   내용: \(( ($r.body // "") | gsub("\n"; " ") | .[0:160]))..."
' {} 2>/dev/null || echo "검색 실행 중 오류 발생"
