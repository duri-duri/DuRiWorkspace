#!/usr/bin/env bash
set -euo pipefail

GT="${GT:-.reports/day62/ground_truth_clean.tsv}"
K="${K:-3}"
SEARCH_SCRIPT="scripts/rag_search_day62_final.sh"

echo "🔍 RAG 검색 품질 평가 (최종 버전)"
echo "Ground Truth: $GT"
echo "Precision@k 의 k=$K"
echo

OUT=".reports/day62/eval_final_$(date +%F_%H%M).tsv"
mkdir -p "$(dirname "$OUT")"

printf "query\tk\thits\tp@k\tr@k\n" > "$OUT"

total_queries=0
sum_precision=0
sum_recall=0

# 헤더 스킵하고 라인별 처리
tail -n +2 "$GT" | tee /dev/stderr | while IFS=$'\t' read -r query cat pf expected || [[ -n "${query:-}" ]]; do
  echo "📋 평가 중: '$query'..."

  # 예상 결과 파싱 (콤마로 분리)
  expected_ids=$(echo "${expected:-}" | tr ',' '\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | grep -v '^$')

  if [[ -z "$expected_ids" ]]; then
    echo "  ⚠️ 예상 결과 없음 또는 비어있음 - 건너뜀"
    continue
  fi

  echo "  📝 예상 ID들: $(echo "$expected_ids" | tr '\n' ' ')"

  # 실제 검색 실행
  search_output=$(bash "$SEARCH_SCRIPT" "$query" "${cat:-}" "${pf:-}" "$K" "1" 2>/dev/null || echo "")

  if [[ -z "$search_output" ]]; then
    echo "  ❌ 검색 실행 실패 또는 결과 없음"
    hits=0
  else
    # 검색 결과에서 ID 추출 (중복 제거)
    found_ids=$(echo "$search_output" | grep "📄 " | sed 's/📄 \([^: (]*\).*/\1/' | sort -u)
    echo "  🔍 검색된 ID들: $(echo "$found_ids" | tr '\n' ' ')"

    # 교집합 계산
    hits=0
    for exp_id in $expected_ids; do
      if echo "$found_ids" | grep -q "^$exp_id$"; then
        hits=$((hits + 1))
        echo "    ✅ 매치: $exp_id"
      fi
    done
  fi

  expected_count=$(echo "$expected_ids" | wc -l)

  # precision 및 recall 계산
  precision=$(awk -v hits="$hits" -v k="$K" 'BEGIN {printf "%.4f", (k > 0 ? hits/k : 0)}')
  recall=$(awk -v hits="$hits" -v expected="$expected_count" 'BEGIN {printf "%.4f", (expected > 0 ? hits/expected : 0)}')

  printf "%s\t%d\t%d\t%s\t%s\n" "$query" "$K" "$hits" "$precision" "$recall" >> "$OUT"

  echo "  📊 결과: hits=$hits, precision=${precision}, recall=${recall}"
  echo

  total_queries=$((total_queries + 1))
  sum_precision=$(awk -v s="$sum_precision" -v p="$precision" 'BEGIN {printf "%.6f", s+p}')
  sum_recall=$(awk -v s="$sum_recall" -v r="$recall" 'BEGIN {printf "%.6f", s+r}')
done

# 전체 통계 계산
if [[ "$total_queries" -gt 0 ]]; then
  macro_precision=$(awk -v s="$sum_precision" -v n="$total_queries" 'BEGIN {printf "%.4f", s/n}')
  macro_recall=$(awk -v s="$sum_recall" -v n="$total_queries" 'BEGIN {printf "%.4f", s/n}')
else
  macro_precision="0.0000"
  macro_recall="0.0000"
fi

{
  echo "---"
  printf "총_쿼리수\t%d\n" "$total_queries"
  printf "macro_p@%d\t%s\n" "$K" "$macro_precision"
  printf "macro_r@%d\t%s\n" "$K" "$macro_recall"
} >> "$OUT"

echo "🎯 평가 완료!"
echo "  총 쿼리 수 = $total_queries"
echo "  macro precision@$K = $macro_precision"
echo "  macro recall@$K = $macro_recall"
echo "📝 상세 결과: $OUT"
echo
cat "$OUT"
