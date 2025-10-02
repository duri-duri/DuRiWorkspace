#!/usr/bin/env bash
set -euo pipefail

command -v jq >/dev/null || { echo "[err] jq not found"; exit 2; }

LC_ALL=C
K=50
RANK=0
FMT="pretty"      # ids|json|pretty
LOG_PATH=""
MODE="literal"    # literal|regex

# ---- 옵션 파싱 ----
while [[ $# -gt 0 ]]; do
  case "$1" in
    --k) K="${2:-50}"; shift 2;;
    --rank) RANK=1; shift;;
    --format) FMT="${2:-pretty}"; shift 2;;
    --log) LOG_PATH="${2:-}"; shift 2;;
    --mode) MODE="${2:-literal}"; shift 2;;
    --) shift; break;;
    *) break;;
  esac
done

QUERY="${1:-}"
CAT="${2:-}"       # intake / education / ...
PF="${3:-}"        # "true" | "false" | ""(무시)

if [[ -z "$QUERY" ]]; then
  echo "사용법: bash scripts/rag_search_enhanced.sh '<검색어>' [카테고리] [patient_facing:true|false] [--rank] [--k N] [--format ids|json|pretty] [--log path] [--mode literal|regex]" >&2
  exit 1
fi

TMP="$(mktemp)"; trap 'rm -f "$TMP"' EXIT

# 1) 추출 + 점수화
find rag/ -name "*.jsonl" -print0 \
| xargs -0 -I{} jq -c --arg q "$QUERY" --arg cat "$CAT" --arg pf "$PF" --arg mode "$MODE" '
  def escre: gsub("([.^$|()\\[\\]{}*+?\\\\])"; "\\\\\1");
  try (
    . as $d
    | select(type=="object") | select(has("title") and has("body"))
    | select(($cat=="" or .category==$cat))
    | select(($pf==""  or (.patient_facing==($pf=="true"))))
    | ($d.title // "")  as $t
    | ($d.body  // "")  as $b
    | (($d.bullets // []) | join(" ")) as $bul
    | (($d.tags    // []) | join(" ")) as $tg
    | ( ($mode=="regex")? $q : ($q|escre) ) as $qq
    | (($t + " " + $b + " " + $bul + " " + $tg) | test($qq; "i")) as $matched
    | select($matched)
    | {
        id: ($d.id // "-"),
        title: ($t|tostring),
        category: ($d.category // "-"),
        patient_facing: ($d.patient_facing // false),
        body: ($b|tostring),
        _t: $t, _bul: $bul, _tg: $tg
      }
    # === 빈도 기반 점수 ===
    | . as $r
    | ($r._t  | scan("(?i)"+$qq) | length) as $c_t
    | ($r._tg | scan("(?i)"+$qq) | length) as $c_tag
    | ($r._bul| scan("(?i)"+$qq) | length) as $c_bul
    | ($r.body| scan("(?i)"+$qq) | length) as $c_b
    | (.score = ($c_t*3 + $c_tag*2 + $c_bul*2 + $c_b))
    | del(._t, ._bul, ._tg)
  ) catch empty
' {} 2>/dev/null > "$TMP"

# 2) 정렬/Top-K/출력
if [[ "$FMT" == "pretty" ]]; then
  jq -rs --argjson k "$K" --argjson rank "$RANK" '
    ($rank==1 ? (sort_by(-(.score // 0))) : .)
    | .[:$k] | .[]
    | "📄 \(.id): \(.title)\n   카테고리: \(.category)\n   환자용: \(.patient_facing)\n   내용: \((.body | gsub("\n"; " ") | .[0:160]))..."
  ' "$TMP"
elif [[ "$FMT" == "ids" ]]; then
  jq -rs --argjson k "$K" --argjson rank "$RANK" '
    ($rank==1 ? (sort_by(-(.score // 0))) : .)
    | .[:$k] | .[].id
  ' "$TMP"
else # json
  jq -rs --argjson k "$K" --argjson rank "$RANK" '
    ($rank==1 ? (sort_by(-(.score // 0))) : .)
    | .[:$k]
  ' "$TMP"
fi

# 3) 로그(옵션)
if [[ -n "$LOG_PATH" ]]; then
  mkdir -p "$(dirname "$LOG_PATH")"
  [[ -s "$LOG_PATH" ]] || printf "ts\tquery\tcat\tpf\tids\n" > "$LOG_PATH"
  ids_csv="$(jq -rs --argjson k "$K" --argjson rank "$RANK" '
    ($rank==1 ? (sort_by(-(.score // 0))) : .)
    | .[:$k] | [.[].id] | join(",")
  ' "$TMP")"
  ts="$(date --iso-8601=seconds 2>/dev/null || date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf "%s\t%s\t%s\t%s\t%s\n" "$ts" "$QUERY" "$CAT" "$PF" "$ids_csv" >> "$LOG_PATH"
fi
