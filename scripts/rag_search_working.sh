#!/usr/bin/env bash
set -euo pipefail

command -v jq >/dev/null || { echo "[err] jq not found"; exit 2; }

QUERY="${1:-}"
CAT="${2:-}"       # intake / education / ...
PF="${3:-}"        # "true" | "false" | ""(무시)

if [[ -z "$QUERY" ]]; then
  echo "사용법: bash scripts/rag_search_working.sh '<검색어>' [카테고리] [patient_facing:true|false]"
  exit 1
fi

echo "🔍 RAG 검색: '$QUERY'"
[[ -n "$CAT" ]] && echo "   카테고리: $CAT"
[[ -n "$PF"  ]] && echo "   환자용: $PF"
echo

# 모든 jsonl을 한 번에 jq로 처리
find rag/ -name "*.jsonl" -print0 \
| xargs -0 -I{} jq -r --arg q "$QUERY" --arg cat "$CAT" --arg pf "$PF" '
  . as $doc
  | select(type=="object")
  | select(has("title") and has("body"))
  | select(($cat=="" or .category==$cat))
  | select(($pf==""  or (.patient_facing==($pf=="true"))))
  | select(((.title // "") + " " + ((.bullets // []) | join(" ")) + " " + ((.tags // []) | join(" "))) | test($q; "i"))
  | {
      id: (.id // "-"),
      title: (.title // "-"),
      category: (.category // "-"),
      patient_facing: (.patient_facing // false),
      body: (.body // "")
    }
' {} 2>/dev/null \
| jq -r '
  . as $r
  | "📄 \($r.id): \($r.title)\n   카테고리: \($r.category)\n   환자용: \($r.patient_facing)\n   내용: \(( $r.body | gsub("\n"; " ") ) | .[0:160])..."
'
