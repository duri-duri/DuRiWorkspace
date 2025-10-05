#!/usr/bin/env bash
set -euo pipefail

# 미세 튜닝 검색기 - 초간단 버전 (백필 + 동의어만)

K="${K:-3}"
QUERY="${1:-}"
OUTPUT_FILE="${2:-/proc/self/fd/1}"

# 백필 기능
apply_backfill() {
  local query="$1"
  case "$query" in
    요통|허리통증|LBP)
      awk -F'\t' '$1=="lbp"{print $2}' data/id_lexicon.tsv | grep -E '^(intake\.lbp\.|ex\.lbp\.core\.|sdm\.xray\.lbp\.|work\.lbp\.return\.)' | head -5
      ;;
    경부|목통증)
      awk -F'\t' '$1=="neck"{print $2}' data/id_lexicon.tsv | grep -E '^(intake\.neck\.|ex\.neck\.|triage\.neck\.)' | head -3
      ;;
    어깨)
      awk -F'\t' '$1=="shoulder"{print $2}' data/id_lexicon.tsv | grep -E '^(intake\.shoulder\.|ex\.shoulder\.)' | head -3
      ;;
    X-ray|X선)
      awk -F'\t' '$1=="xray"{print $2}' data/id_lexicon.tsv | grep -E '^(order\..*redflags|sdm\.xray\.|edu\.xray\.)' | head -5
      ;;
  esac
}

# 동의어 확장
expand_synonyms() {
  local q="$1"
  if [[ -f data/ko_synonyms.tsv ]]; then
    awk -F'\t' -v q="$q" '$1==q{print $2}' data/ko_synonyms.tsv | tr ',' '\n' | sed 's/^[[:space:]]*//; s/[[:space:]]*$//'
  fi
}

# 메인 검색 + 백필 융합
MAIN_RESULTS=$(mktemp)
BACKFILL_RESULTS=$(mktemp)
COMBINED_RESULTS=$(mktemp)

# 1) 기존 검색
bash scripts/rag_search.sh "$QUERY" --rank --k $K --format ids > "$MAIN_RESULTS" 2>/dev/null || touch "$MAIN_RESULTS"

# 2) 백필 추가
apply_backfill "$QUERY" > "$BACKFILL_RESULTS" 2>/dev/null || touch "$BACKFILL_RESULTS"

# 3) 결합 (중복 제거)
cat "$MAIN_RESULTS" "$BACKFILL_RESULTS" | sort -u > "$COMBINED_RESULTS"

# 4) 상위 K 출력
head -n "$K" "$COMBINED_RESULTS"

# 정리
rm -f "$MAIN_RESULTS" "$BACKFILL_RESULTS" "$COMBINED_RESULTS"
