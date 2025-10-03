#!/usr/bin/env bash
set -euo pipefail

GT="${GT:-.reports/day62/ground_truth.tsv}"
K="${K:-3}"
THRESHOLD_P="${THRESHOLD_P:-0.60}"
THRESHOLD_R="${THRESHOLD_R:-}"

echo "🚪 RAG 검색 품질 게이트 체크"
echo "Ground Truth: $GT"
echo "K: $K"
echo "Precision 기준: $THRESHOLD_P"
[[ -n "$THRESHOLD_R" ]] && echo "Recall 기준: $THRESHOLD_R"
echo

# 평가 실행
TMP_OUT="$(mktemp)"
bash scripts/rag_eval_day62.sh > "$TMP_OUT"
trap 'rm -f "$TMP_OUT"' EXIT

# 수치 추출
mp="$(grep "^micro_p@" "$TMP_OUT" | cut -f2 | tail -1)"
mr="$(grep "^micro_r@" "$TMP_OUT" | cut -f2 | tail -1)"

echo
echo "🎯 게이트 결과:"
echo "  micro precision@$K = $mp"
echo "  micro recall@$K = $mr"

echo
echo "✅ 게이트 통과 기준 검사:"
echo "  precision >= $THRESHOLD_P ... "

if awk "BEGIN {if(($mp + 0) < ($THRESHOLD_P + 0)) exit 1; else exit 0}" 2>/dev/null; then
  echo "    ✅ 통과 ($mp >= $THRESHOLD_P)"
  precision_pass=1
else
  echo "    ❌ 실패 ($mp < $THRESHOLD_P)"
  precision_pass=0
fi

if [[ -n "$THRESHOLD_R" ]]; then
  echo "  recall >= $THRESHOLD_R ... "
  if awk "BEGIN {if(($mr + 0) < ($THRESHOLD_R + 0)) exit 1; else exit 0}" 2>/dev/null; then
    echo "    ✅ 통과 ($mr >= $THRESHOLD_R)"
    recall_pass=1
  else
    echo "    ❌ 실패 ($mr < $THRESHOLD_R)"
    recall_pass=0
  fi
else
  recall_pass=1  # recall 기준 없음
fi

if [[ "$precision_pass" == "1" && "$recall_pass" == "1" ]]; then
  echo
  echo "🎉 게이트 통과! RAG 검색 품질 기준 충족"
  exit 0
else
  echo
  echo "💢 게이트 실패! RAG 검색 품질 개선 필요"
  echo "개선 방안:"
  echo "  1. ground_truth.tsv 추가/수정"
  echo "  2. rag 데이터 품질 향상"
  echo "  3. 검색 알고리즘 튜닝"
  exit 1
fi
