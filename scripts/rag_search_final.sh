#!/usr/bin/env bash
set -euo pipefail

command -v jq >/dev/null || { echo "[err] jq not found"; exit 2; }

LC_ALL=C
K=10
RANK=0
FMT="pretty"
LOG_PATH=""
MODE="literal"

# ---- 옵션 파싱 ----
while [[ $# -gt 0 ]]; do
  case "$1" in
    --k)
      K="${2:-10}";
      shift 2
      ;;
    --rank)
      RANK=1;
      shift
      ;;
    --format)
      FMT="${2:-pretty}";
      shift 2
      ;;
    --log)
      LOG_PATH="${2:-}";
      shift 2
      ;;
    --mode)
      MODE="${2:-literal}";
      shift 2
      ;;
    --)
      shift;
      break
      ;;
    *.v1.*|v1.*|true|false|intake|education|exercise|orders|schedule|policy|consent|triage|sdm|soap|outcome|rx_education|work_plan|billing)
      # positional arguments - fall through
      break
      ;;
    "--"*)
      echo "알 수 없는 옵션: $1" >&2
      exit 1
      ;;
    *)
      # 검색어나 필터 인수
      break
      ;;
  esac
done

QUERY="${1:-}"
CAT="${2:-}"       # intake / education / ...
PF="${3:-}"        # "true" | "false" | ""(무시)

if [[ -z "$QUERY" ]]; then
  echo "사용법: bash scripts/rag_search_final.sh '<검색어>' [카테고리] [patient_facing:true|false]" >&2
  echo "옵션: [--rank] [--k N] [--format ids|json|pretty] [--log path] [--mode literal|regex]" >&2
  exit 1
fi

TMP="$(mktemp)"; trap 'rm -f "$TMP"' EXIT

echo "🔍 RAG 검색: '$QUERY'"
[[ -n "$CAT" ]] && echo "   카테고리: $CAT"
[[ -n "$PF"  ]] && echo "   환자용: $PF"
[[ "$RANK" == "1" ]] && echo "   랭킹 ON"
echo "   결과 수: 최대 $K개"
echo

# 1) 추출 + 점수화
find rag/ -name "*.jsonl" -print0 \
| xargs -0 -I{} jq -c --arg q "$QUERY" --arg cat "$CAT" --arg pf "$PF" --arg mode "$MODE" '
  def escre: gsub("([.^$|()\\[\\]{}*+?\\\\])"; "\\\\\1");
  try (
    . as $d
    | select(type=="object") | select(has("title") and has("body"))
    | select(($cat=="" or .category==$cat))
    | select(($pf==""  or (.patient_facing==($pf=="true"))))
    | ($d.title // "") as $title
    | ($d.body  // "") as $body
    | (($d.bullets // []) | join(" ")) as $bullets
    | (($d.tags    // []) | join(" ")) as $tags
    | ( ($mode=="regex")? $q : ($q|escre) ) as $qq
    | (($title + " " + $body + " " + $bullets + " " + $tags) | test($qq; "i")) as $matched
    | select($matched)
    | {
        id: ($d.id // "-"),
        title: $title,
        category: ($d.category // "-"),
        patient_facing: ($d.patient_facing // false),
        body: $body,
        _search_text: ($title + " " + $bullets + " " + $tags)
      }
    # === 빈도 기반 점수 ===
    | . as $r
    | (($r._search_text) | scan("(?i)"+$qq) | length) as $c_title_tags
    | (($r.body) | scan("(?i)"+$qq) | length) as $c_body
    | (.score = ($c_title_tags*3 + $c_body*1))
    | del(._search_text)
  ) catch empty
' {} 2>/dev/null > "$TMP"

# 2) 정렬/Top-K/출력
if [[ "$FMT" == "pretty" ]]; then
  if [[ -s "$TMP" ]]; then
    echo "✅ 검색 완료, 상위 $K개 결과:"
    jq -rs --argjson k "$K" --argjson rank "$RANK" '
      ($rank==1 ? (sort_by(-(.score // 0))) : .)
      | .[:$k] | .[]
      | "📄 \(.id): \(.title)\n   카테고리: \(.category)\n   환자용: \(.patient_facing)\n   내용: \((.body | gsub("\n"; " ") | .[0:160]))..."
    ' "$TMP"
  else
    echo "❌ 검색 결과 없음"
  fi
elif [[ "$FMT" == "ids" ]]; then
  if [[ -s "$TMP" ]]; then
    jq -rs --argjson k "$K" --argjson rank "$RANK" '
      ($rank==1 ? (sort_by(-(.score // 0))) : .)
      | .[:$k] | .[].id
    ' "$TMP"
  fi
else # json
  if [[ -s "$TMP" ]]; then
    echo "✅ 검색 완료, 상위 $K개 결과 (JSON):"
    jq -rs --argjson k "$K" --argjson rank "$RANK" '
      ($rank==1 ? (sort_by(-(.score // 0))) : .)
      | .[:$k]
    ' "$TMP"
  else
    echo "❌ 검색 결과 없음 (JSON: [])"
  fi
fi

# 3) 로그(옵션)
if [[ -n "$LOG_PATH" ]]; then
  mkdir -p "$(dirname "$LOG_PATH")"
  [[ -s "$LOG_PATH" ]] || printf "ts\tquery\tcat\tpf\tids\n" > "$LOG_PATH"
  ids_csv="$(if [[ -s "$TMP" ]]; then
    jq -rs --argjson k "$K" --argjson rank "$RANK" '
      ($rank==1 ? (sort_by(-(.score // 0))) : .)
      | .[:$k] | [.[].id] | join(",")
    ' "$TMP"
  else
    echo ""
  fi)"
  ts="$(date --iso-8601=seconds 2>/dev/null || date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf "%s\t%s\t%s\t%s\t%s\n" "$ts" "$QUERY" "$CAT" "$PF" "$ids_csv" >> "$LOG_PATH"
  echo "📝 로그 기록: $LOG_PATH"
fi
