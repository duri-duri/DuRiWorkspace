#!/usr/bin/env bash
# L4.0 원클릭 패치 (모든 단계 통합)
# Usage: bash scripts/evolution/fix_namespace_complete.sh
# 목적: 최소 패치 → 원인 검증 → 권한 고정 → 최종 체크까지 한 번에

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

echo "=== L4.0 원클릭 패치 (모든 단계 통합) ==="
echo ""

# 1. 최소 패치
echo "=== 1단계: 최소 패치 (WSL 호환) ==="
bash scripts/evolution/fix_namespace_wsl_minimal.sh
echo ""

# 2. 원인 검증
echo "=== 2단계: 원인 검증 ==="
if bash scripts/evolution/verify_namespace_fix.sh; then
    echo "✅ 원인 검증 통과"
else
    echo "⚠️  원인 검증 실패, 재시도 권장"
fi
echo ""

# 3. 워크트리 권한 고정
echo "=== 3단계: 워크트리 권한/해시 드리프트 고정 ==="
bash scripts/evolution/fix_workspace_permissions.sh
echo ""

# 4. 최종 체크리스트
echo "=== 4단계: 최종 체크리스트 ==="
bash scripts/evolution/final_check_l4.sh
echo ""

echo "=== 원클릭 패치 완료 ==="
echo ""
echo "다음 단계:"
echo "  bash scripts/evolution/preflight_l4.sh   # 프리플라이트"
echo "  bash scripts/evolution/run_l4_timeline.sh # 타임라인 실행"

