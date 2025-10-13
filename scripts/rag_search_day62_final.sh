#!/usr/bin/env bash
set -euo pipefail

command -v jq >/dev/null || { echo "[err] jq not found"; exit 2; }

QUERY="${1:-}"
CAT="${2:-}"
PF="${3:-}"
TOP="${4:-10}"
RANK="${5:-0}"

if [[ -z "$QUERY" ]]; then
  echo "사용법: bash scripts/rag_search_day62_final.sh '<검색어>' [카테고리] [patient_facing] [top_N] [rank_on]" >&2
  echo "예시: bash scripts/rag_search_day62_final.sh \"요통\" \"\" \"\" \"5\" \"1\"" >&2
  exit 1
fi

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
  | ((.bullets // []) | join(" ")) as $bullets
  | ((.tags    // []) | join(" ")) as $tags
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
  # 머신 출력 모드 (평가용)
  if [[ "${FORMAT:-pretty}" == "ids" ]]; then
    jq -rs --argjson top "$TOP" '
      unique_by(.id)
      | sort_by(-.score)
      | .[:$top] | .[] | .id
    ' "$TMP"
  else
    # 예쁜 출력 모드 (사용자용)
    echo "✅ 검색 완료, 상위 $TOP개 결과:"
    if [[ "$RANK" == "1" ]]; then
      jq -rs --argjson top "$TOP" '
        unique_by(.id)
        | sort_by(-.score)
        | .[:$top] | .[]
        | "📄 \(.id): \(.title) (점수:\(.score))\n   카테고리: \(.category)\n   환자용: \(.patient_facing)\n   내용: \((.body | gsub("\n"; " ") | .[0:160]))..."
      ' "$TMP"
    else
      jq -rs --argjson top "$TOP" '
        unique_by(.id)
        | .[:$top] | .[]
        | "📄 \(.id): \(.title)\n   카테고리: \(.category)\n   환자용: \(.patient_facing)\n   내용: \((.body | gsub("\n"; " ") | .[0:160]))..."
      ' "$TMP"
    fi
  fi
else
  if [[ "${FORMAT:-pretty}" == "ids" ]]; then
    # 머신 출력 모드에서는 빈 결과도 조용히
    true
  else
    echo "❌ 검색 결과 없음"
  fi
fi
