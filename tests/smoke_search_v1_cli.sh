#!/usr/bin/env bash
set -euo pipefail

# v1-CLI 계약 회귀 방지 스모크 테스트
echo "🧪 v1-CLI 계약 스모크 테스트"

# 1) 순수 ID 3줄 출력 확인
out=$(bash scripts/rag_search_fusion_v1.sh "요통" ---rank --k 3 --format ids | wc -l | tr -d ' ')
if [[ "$out" -eq 3 ]]; then
    echo "✅ 순수 ID 3줄 출력 확인"
else
    echo "❌ ID 출력 개수 불일치: $out (기대: 3)"
    exit 1
fi

# 2) stderr 출력 없음 확인
stderr_out=$(bash scripts/rag_search_fusion_v1.sh "요통" ---rank --k 3 --format ids 2>&1 >/dev/null | wc -l | tr -d ' ')
if [[ "$stderr_out" -eq 0 ]]; then
    echo "✅ stderr 출력 없음 확인"
else
    echo "❌ stderr 출력 발견: $stderr_out 줄"
    exit 1
fi

# 3) 게이트 호환성 확인
if SEARCH=scripts/rag_search_fusion_v1.sh THRESH_P=0.30 bash scripts/rag_gate_day62.sh >/dev/null 2>&1; then
    echo "✅ 게이트 호환성 확인"
else
    echo "❌ 게이트 호환성 실패"
    exit 1
fi

echo "🎉 모든 v1-CLI 계약 테스트 통과!"
