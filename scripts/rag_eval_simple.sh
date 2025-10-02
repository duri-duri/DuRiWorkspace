#!/usr/bin/env bash
set -euo pipefail

GT="${GT:-.reports/day62/ground_truth.tsv}"
K="${K:-3}"
SEARCH_SCRIPT="scripts/rag_search_day62_final.sh"

echo "🔍 RAG 검색 품질 평가 (간단버전)"
echo "Ground Truth: $GT"
echo "Precision@k with k=$K"
echo

OUT=".reports/day62/eval_simple_$(date +%F_%H%M).tsv"
mkdir -p "$(dirname "$OUT")"

printf "query\tk\thits\tp@k\tr@k\n" > "$OUT"

total_queries=0
sum_p=0
sum_r=0

while IFS=$'\t' read -r query cat pf expected || [[ -n "${query:-}" ]]; do
  [[ -z "${query// }" ]] && continue
  [[ "${query:0:1}" == "#" ]] && continue

  echo "📋 평가 중: '$query'..."

  # 검색 실행 및 결과 추출 (간단 버전)
  results=$(bash "$SEARCH_SCRIPT" "$query" "${cat:-}" "${pf:-}" "$K" "1" 2>/dev/null | grep "📄 " || echo "")
  found_ids=$(echo "$results" | sed 's/📄 \([^: (]*\).*/\1/' | grep -v "^$" || true)

  expected_ids=$(echo "${expected:-}" | tr ',' '\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | grep -v "^$" || true)

  if [[ -z "$expected_ids" ]]; then
    echo "  ⚠️ 예상 결과 없음 - 건너뜀"
    continue
  fi

  # 교집합 계산
  hits=0
  for exp_id in $expected_ids; do
    if echo "$found_ids" | grep -q "^$exp_id$"; then
      hits=$((hits + 1))
    fi
  done

  expected_count=$(echo "$expected_ids" | wc -l)
  k_reserved=$(echo "$found_ids" | wc -l)

  # 간단 분수 계산 (awk 사용)
  precision=$(awk -v hits="$hits" -v k="$K" 'BEGIN {printf "%.4f", (k > 0 ? hits/k : 0)}')
  recall=$(awk -v hits="$hits" -v expected="$expected_count" 'BEGIN {printf "%.4f", (expected > 0 ? hits/expected : 0)}')

  printf "%s\t%d\t%d\t%s\t%s\n" "$query" "$K" "$hits" "$precision" "$recall" >> "$OUT"

  echo "  📊 결과: hits=$hits, precision=${precision}, recall=${recall}"

  total_queries=$((total_queries + 1))
  sum_p=$(awk -v s="$sum_p" -v p="$precision" 'BEGIN {printf "%.6f", s+p}')
  sum_r=$(awk -v s="$sum_r" -v r="$recall" 'BEGIN {printf "%.6f", s+r}')

done < "$GT"

if [[ "$total_queries" -gt 0 ]]; then
  macro_p=$(awk -v s="$sum_p" -v n="$total_queries" 'BEGIN {printf "%.4f", s/n}')
  macro_r=$(awk -v s="$sum_r" -v n="$total_queries" 'BEGIN {printf "%.4f", s/n}')
else
  macro_p="0.0000"
  macro_r="0.0000"
fi

{
  echo "---"
  printf "총_쿼리수\t%d\n" "$total_queries"
  printf "macro_p@%d\t%s\n" "$K" "$macro_p"
  printf "macro_r@%d\t%s\n" "$K" "$macro_r"
} >> "$OUT"

echo
echo "📈 최종 평가 결과:"
echo "  총 쿼리 수 = $total_queries"
echo "  macro precision@$K = $macro_p"
echo "  macro recall@$K = $macro_r"
echo
echo "📝 상세 결과 파일: $OUT"
cat "$OUT"
