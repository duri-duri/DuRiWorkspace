#!/usr/bin/env bash
# L4.0 승급 절차 - 검증→선언→관측 원클릭
# Usage: bash scripts/evolution/promote_to_l4.sh

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

echo "=== L3.9 → L4.0 승급 절차 ==="
echo ""

# 1. 브랜치 생성
echo "1. 브랜치 생성"
BRANCH="ops/coldsync-l4-gate"
git switch -c "$BRANCH" 2>/dev/null || git switch "$BRANCH"
echo "✅ 브랜치: $BRANCH"
echo ""

# 2. L4.0 Gate 검증
echo "2. L4.0 Gate 검증 (6/6)"
bash scripts/evolution/verify_l4_gate.sh
VERIFY_RESULT=$?

if [ $VERIFY_RESULT -ne 0 ]; then
    echo ""
    echo "❌ Gate 검증 실패. L4.0 승급 불가."
    echo ""
    echo "📋 보정 후 재시도:"
    echo "  bash scripts/evolution/verify_l4_gate.sh"
    exit 1
fi

echo ""
echo "✅ 모든 Gate 통과 확인"
echo ""

# 3. 프로모션 스코어 확인 (7일)
echo "3. 프로모션 스코어 확인 (7일)"
SCORE_OUTPUT=$(python3 scripts/evolution/promotion_gate_v2.py --window 168 --gate L4.1 --print 2>&1 || echo "NO_METRICS")
echo "$SCORE_OUTPUT"
echo ""

# 4. L4.0 선언 및 태깅
echo "4. L4.0 선언 및 태깅"
bash scripts/evolution/declare_l4.sh
DECLARE_RESULT=$?

if [ $DECLARE_RESULT -ne 0 ]; then
    echo ""
    echo "❌ 선언 실패"
    exit 1
fi

echo ""
echo "=== L4.0 승급 완료 ==="
echo ""
echo "📋 다음 단계:"
echo "  1. 운영 관측: bash scripts/bin/status_coldsync_oneline.sh"
echo "  2. 24h 드릴: bash scripts/bin/verify_coldsync_final.sh"
echo "  3. L4.1 진화: bash scripts/evolution/start_l4_evolution.sh"

