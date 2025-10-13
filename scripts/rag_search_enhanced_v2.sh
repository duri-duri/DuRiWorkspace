#!/usr/bin/env bash
set -euo pipefail

command -v jq >/dev/null || { echo "[err] jq not found"; exit 2; }

QUERY="${1:-}"
CAT="${2:-}"       # intake / education / ...
PF="${3:-}"        # "true" | "false" | ""(무시)

if [[ -z "$QUERY" ]]; then
  echo "사용법: bash scripts/rag_search_enhanced_v2.sh '<검색어>' [카테고리] [patient_facing:true|false]" >&2
  echo "예시: bash scripts/rag_search_enhanced_v2.sh \"요통\" intake false --rank --top 3 --log .reports/day62/search.tsv" >&2
  exit 1
fi

RANK=0
TOP=50
LOG_FILE=""

# 간단한 옵션 파싱
for arg in "${@:4}"; do
  case "$arg" in
    --rank) RANK=1 ;;
    --top=*) TOP="${arg#*=}" ;;
    --top) TOP="${5:-50}" ;;
    --log=*) LOG_FILE="${arg#*=}" ;;
    --log) LOG_FILE="${5:-.reports/day62/search.tsv}" ;;
  esac
done

echo "🔍 RAG 검색(점수기반): '$QUERY'"
[[ -n "$CAT" ]] && echo "   카테고리: $CAT"
[[ -n "$PF"  ]] && echo "   환자용: $PF"
[[ "$RANK" == "1" ]] && echo "   랭킹 점수 계산 ON"
echo "   최대 결과: $TOP개"
echo

TMP="$(mktemp)"; trap 'rm -f "$TMP"' EXIT

# 1) 점수화 검색
find rag/ -name "*.jsonl" -print0 \
| xargs -0 -I{} jq -c --arg q "$QUERY" --arg cat "$CAT" --arg pf "$PF" '
  . as $d
  | select(type=="object")
  | select(has("title") and has("body"))
  | select(($cat=="" or .category==$cat))
  | select(($pf==""  or (.patient_facing==($pf=="true"))))
  | ($d.title // "") as $title
  | ($d.body  // "") as $body
  | (($d.bullets // []) | join(" ")) as $bullets
  | (($d.tags    // []) | join(" ")) as $tags
  | {
      id: ($d.id // "-"),
      title: $title,
      category: ($d.category // "-"),
      patient_facing: ($d.patient_facing // false),
      body: $body,
      full_text: ($title + " " + $bullets + " " + $tags + " " + $body)
    }
  | select(.full_text | test($q; "i"))
  | (.score = ((.full_text | scan("(?i)"+$q) | length)))
  | del(.full_text)
' {} 2>/dev/null > "$TMP"

# 2) 정렬 및 출력
if [[ -s "$TMP" ]]; then
  echo "✅ 검색 완료, 상위 $TOP개 결과:"
  if [[ "$RANK" == "1" ]]; then
    jq -rs --argjson top "$TOP" '
      sort_by(-.score)
      | .[:$top] | .[]
      | "📄 \(.id): \(.title) (점수:\(.score))\n   카테고리: \(.category)\n   환자용: \(.patient_facing)\n   내용: \((.body | gsub("\n"; " ") | .[0:160]))..."
    ' "$TMP"
  else
    jq -rs --argjson top "$TOP" '
      .[:$top] | .[]
      | "📄 \(.id): \(.title)\n   카테고리: \(.category)\n   환자용: \(.patient_facing)\n   내용: \((.body | gsub("\n"; " ") | .[0:160]))..."
    ' "$TMP"
  fi
else
  echo "❌ 검색 결과 없음"
fi

# 3) 로그 기록
if [[ -n "$LOG_FILE" ]]; then
  mkdir -p "$(dirname "$LOG_FILE")"
  [[ -f "$LOG_FILE" ]] || printf "timestamp\tquery\tcat\tpf\ttop_ids\n" > "$LOG_FILE"
  ids="$(if [[ -s "$TMP" ]]; then
    jq -rs --argjson top "$TOP" '
      .[:$top] | [.[].id] | join(",")
    ' "$TMP" 2>/dev/null || echo ""
  else
    echo ""
  fi)"
  timestamp="$(date --iso-8601=seconds 2>/dev/null || date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf "%s\t%s\t%s\t%s\t%s\n" "$timestamp" "$QUERY" "$CAT" "$PF" "$ids" >> "$LOG_FILE"
  echo "📝 검색 로그 기록: $LOG_FILE"
fi
