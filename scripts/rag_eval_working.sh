#!/usr/bin/env bash
set -euo pipefail

GT="${GT:-.reports/day62/ground_truth_clean.tsv}"
K="${K:-3}"

echo "🔍 RAG 품질 평가 실행"
echo "Ground Truth: $GT"
echo "k=$K"
echo

# 첫 번째 쿼리 "요통" 테스트
echo "📋 테스트: '요통' 쿼리..."

# 예상 결과
expected="intake.lbp.v1.001,ex.lbp.core.v1.001,edu.xray.expectation.v1.001"
echo "📝 예상 ID들: $expected"

# 실제 검색 실행
search_result=$(bash scripts/rag_search_day62_final.sh "요통" "" "" "3" "1" 2>/dev/null)
echo "🔍 검색 결과 (상위 3개):"
echo "$search_result" | head -3

# 매칭 계산
found_ids=$(echo "$search_result" | grep "📄 " | sed 's/📄 \([^: (]*\).*/\1/' | sort -u)
echo "🎯 검색된 ID들: $(echo "$found_ids" | tr '\n' ' ')"

hits=0
for exp_id in $(echo "$expected" | tr ',' '\n'); do
  exp_id=$(echo "$exp_id" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
  if echo "$found_ids" | grep -q "^$exp_id$"; then
    hits=$((hits + 1))
    echo "  ✅ 매치: $exp_id"
  else
    echo "  ❌ 누락: $exp_id"
  fi
done

expected_count=$(echo "$expected" | tr ',' '\n' | wc -l)
precision=$(awk -v hits="$hits" -v k="$K" 'BEGIN {printf "%.4f", hits/k}')
recall=$(awk -v hits="$hits" -v expected_count="$expected_count" 'BEGIN {printf "%.4f", hits/expected_count}')

echo
echo "📊 평가 결과:"
echo "  hits: $hits / $expected_count"
echo "  precision@$K = $precision"
echo "  recall@$K = $recall"

if (( $(echo "$precision >= 0.7" | bc -l) )); then
  echo "✅ Precision 기준 통과 (>= 0.7)"
else
  echo "❌ Precision 기준 실패 (< 0.7)"
fi
