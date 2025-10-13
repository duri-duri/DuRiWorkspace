#!/usr/bin/env bash
# Day64 긴급 롤백 스크립트 - 베이스라인으로 복귀
set -euo pipefail

echo "🔄 Day64 긴급 롤백: 베이스라인으로 복귀"
echo "========================================"

# 롤백 환경변수 설정
export SEARCH=scripts/rag_search_day62_final.sh
export HYBRID_ALPHA=0.3
export THRESH_P=0.30

echo "✅ 롤백 환경변수 설정:"
echo "   SEARCH=$SEARCH"
echo "   HYBRID_ALPHA=$HYBRID_ALPHA"
echo "   THRESH_P=$THRESH_P"

# 베이스라인 성능 확인
echo ""
echo "📊 베이스라인 성능 확인:"
bash scripts/rag_gate_day62.sh

echo ""
echo "🎯 롤백 완료! 베이스라인 설정으로 복귀되었습니다."
