#!/usr/bin/env bash
set -euo pipefail

# Day 65: Reranker-ready search wrapper (gate-safe)
QUERY="${1:-}"
K="${K:-3}"                                 # 최종 반환 개수
PRE_K="${TOPK_BEFORE_RERANK:-20}"           # 리랭크 전 후보 개수
RERANK="${RERANK:-off}"
FORMAT="${FORMAT:-ids}"                     # ids | json | pretty
BASE_SEARCH="${BASE_SEARCH:-scripts/rag_search_tuned.sh}"  # 필요시 enhanced로 교체

export PATH="$HOME/.local/bin:$PATH"  # python/jq 경로 보강

log(){ echo "$@" >&2; }
need(){ command -v "$1" >/dev/null 2>&1; }

[[ -n "$QUERY" ]] || exit 0

# -- 기본 모드(리랭크 off) ------------------------------------------------------
if [[ "$RERANK" != "on" ]]; then
  log "📋 base: '$QUERY' (K=$K, FORMAT=$FORMAT)"
  case "$FORMAT" in
    json)   FORMAT=json K="$K" "$BASE_SEARCH" "$QUERY" ;;
    ids)    FORMAT=json K="$K" "$BASE_SEARCH" "$QUERY" | jq -r ".[0:$K][].id" ;;
    *)      FORMAT=json K="$K" "$BASE_SEARCH" "$QUERY" \
              | jq -r '.[0:'"$K"'] | .[] | "📄 \(.id): \(.title // "N/A") (score:\(.combined_score // .score // 0))"'
          ;;
  esac
  exit 0
fi

log "🔄 rerank: '$QUERY' (preK=$PRE_K → K=$K, FORMAT=$FORMAT, base=$BASE_SEARCH)"

tmp_json="$(mktemp)"; tmp_out="$(mktemp)"
trap 'rm -f "$tmp_json" "$tmp_out"' EXIT

# 1) 후보 수집(JSON 선호)
if FORMAT=json K="$PRE_K" "$BASE_SEARCH" "$QUERY" >"$tmp_json" 2>/dev/null; then
  :
else
  # ids만 가능한 경우 → rank 포함해 JSON 합성
  tmp_ids="$(mktemp)"; trap 'rm -f "$tmp_json" "$tmp_out" "$tmp_ids"' EXIT
  FORMAT=ids K="$PRE_K" "$BASE_SEARCH" "$QUERY" >"$tmp_ids" 2>/dev/null || true
  if [[ -s "$tmp_ids" ]]; then
    if need jq; then
      awk '{printf("{\"id\":\"%s\",\"rank\":%d}\n",$0,NR-1)}' "$tmp_ids" | jq -s '.' > "$tmp_json"
    else
      log "⚠️ jq 없음 → fallback"
      FORMAT="$FORMAT" K="$K" "$BASE_SEARCH" "$QUERY"; exit 0
    fi
  else
    log "⚠️ base 결과 없음 → fallback"
    FORMAT="$FORMAT" K="$K" "$BASE_SEARCH" "$QUERY"; exit 0
  fi
fi

# 2) 리랭킹
if ! need python3; then
  log "⚠️ python3 없음 → fallback"
  FORMAT="$FORMAT" K="$K" "$BASE_SEARCH" "$QUERY"; exit 0
fi

if python3 tools/rerank.py --query "$QUERY" --top-k "$K" --input "$tmp_json" > "$tmp_out" 2>/dev/null; then
  case "$FORMAT" in
    ids)  jq -r '.[].id' "$tmp_out" ;;
    json) cat "$tmp_out" ;;
    *)    jq -r '.[] | "📄 \(.id): \(.title // "N/A") (score:\(.combined_score // .score // 0))"' "$tmp_out" ;;
  esac
else
  log "⚠️ 리랭크 실패 → fallback"
  FORMAT="$FORMAT" K="$K" "$BASE_SEARCH" "$QUERY"
fi
