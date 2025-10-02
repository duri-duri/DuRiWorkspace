#!/usr/bin/env bash
set -euo pipefail

GT="${GT:-.reports/day62/ground_truth.tsv}"
K="${K:-3}"
SEARCH_SCRIPT="scripts/rag_search_day62_final.sh"

echo "🔍 RAG 검색 품질 평가 (Day 62)"
echo "Ground Truth: $GT"
echo "Precision@k with k=$K"
echo "검색 스크립트: $SEARCH_SCRIPT"
echo

OUT=".reports/day62/eval_$(date +%F_%H%M).tsv"
mkdir -p "$(dirname "$OUT")"

printf "query\tk\thits\tp@k\tr@k\n" > "$OUT"

total_queries=0
total_hits=0
total_results=0
total_expected=0
macro_p_sum=0
macro_r_sum=0

while IFS=$'\t' read -r query cat pf expected || [[ -n "${query:-}" ]]; do
  [[ -z "${query// }" ]] && continue
  [[ "${query:0:1}" == "#" ]] && continue

  echo "📋 평가 중: '$query'..."

  # 예상 결과 파일 준비
  E="$(mktemp)"
  echo "${expected:-}" | tr ',' '\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | sort -u > "$E"

  # 실제 검색 실행
  G="$(mktemp)"
  bash "$SEARCH_SCRIPT" "$query" "${cat:-}" "${pf:-}" "$K" "1" 2>/dev/null \
    | grep "📄 " | sed 's/📄 \([^:]*\):.*/\1/' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | sort -u > "$G"

  if ! [[ -s "$E" ]]; then
    echo "  ⚠️ 예상 결과 없음 - 건너뜀"
    continue
  fi

  hits="$(comm -12 "$E" "$G" | wc -l)"
  expected_count="$(wc -l < "$E")"
  k_results="$(wc -l < "$G")"

  precision="$(echo "scale=6; $hits / $K" | bc -l 2>/dev/null || echo "0")"
  recall="$(echo "scale=6; $hits / $expected_count" | bc -l 2>/dev/null || echo "0")"

  printf "%s\t%d\t%d\t%.4f\t%.4f\n" "$query" "$K" "$hits" "$precision" "$recall" >> "$OUT"

  echo "  📊 결과: hits=$hits, precision=${precision}, recall=${recall}"

  total_queries=$((total_queries + 1))
  total_hits=$((total_hits + hits))
  total_results=$((total_results + k_results))
  total_expected=$((total_expected + expected_count))

  macro_p_sum="$(echo "scale=6; $macro_p_sum + $precision" | bc -l 2>/dev/null || echo "$macro_p_sum")"
  macro_r_sum="$(echo "scale=6; $macro_r_sum + $recall" | bc -l 2>/dev/null || echo "$macro_r_sum")"

  rm -f "$E" "$G"
done < "$GT"

# 전체 통계 계산
micro_p="$(echo "scale=6; $total_hits / $total_results" | bc -l 2>/dev/null || echo "0")"
micro_r="$(echo "scale=6; $total_hits / $total_expected" | bc -l 2>/dev/null || echo "0")"
macro_p="$(echo "scale=6; $macro_p_sum / $total_queries" | bc -l 2>/dev/null || echo "0")"
macro_r="$(echo "scale=6; $macro_r_sum / $total_queries" | bc -l 2>/dev/null || echo "0")"

{
  echo "---"
  printf "총_쿼리수\t%d\n" "$total_queries"
  printf "micro_p@%d\t%.4f\n" "$K" "$micro_p"
  printf "micro_r@%d\t%.4f\n" "$K" "$micro_r"
  printf "macro_p@%d\t%.4f\n" "$K" "$macro_p"
  printf "macro_r@%d\t%.4f\n" "$K" "$macro_r"
} >> "$OUT"

echo
echo "📈 최종 평가 결과:"
echo "  micro precision@$K = $micro_p"
echo "  micro recall@$K = $micro_r"
echo "  macro precision@$K = $macro_p"
echo "  macro recall@$K = $macro_r"
echo
echo "📝 상세 결과 파일: $OUT"
cat "$OUT"
