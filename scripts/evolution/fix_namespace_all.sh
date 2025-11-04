#!/usr/bin/env bash
# L4.0 원클릭 패치 (모든 단계 통합)
# Usage: bash scripts/evolution/fix_namespace_all.sh
# 목적: 최소 패치 → 영구 패치 → 회귀 테스트까지 한 번에

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

echo "=== L4.0 원클릭 패치 (모든 단계 통합) ==="
echo ""

# 1. 최소 패치
echo "=== 1단계: 최소 패치 ==="
bash scripts/evolution/fix_namespace_minimal.sh
echo ""

# 2. 영구 패치
echo "=== 2단계: 영구 패치 ==="
bash scripts/evolution/fix_namespace_permanent.sh
echo ""

# 3. 끝점 체크
echo "=== 3단계: 끝점 체크 ==="
if bash scripts/evolution/endpoint_check.sh; then
    echo "✅ 끝점 체크 통과"
else
    echo "⚠️  끝점 체크 실패, WSL 특이점 완화 시도..."
    bash scripts/evolution/fix_namespace_wsl.sh
    bash scripts/evolution/endpoint_check.sh
fi
echo ""

# 4. 회귀 테스트
echo "=== 4단계: 회귀 테스트 ==="
bash scripts/evolution/regression_test.sh
echo ""

echo "=== 원클릭 패치 완료 ==="
echo ""
echo "다음 단계:"
echo "  bash scripts/evolution/run_l4_timeline.sh   # 타임라인 실행"

