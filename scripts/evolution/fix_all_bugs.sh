#!/usr/bin/env bash
# L4.0 원클릭 핫픽스 (모든 버그 수정 통합)
# Usage: bash scripts/evolution/fix_all_bugs.sh
# 목적: ProtectSystem 버그 + 설치기 exit 0 + 검증 스크립트 파싱 버그 모두 수정

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

echo "=== L4.0 원클릭 핫픽스 (모든 버그 수정) ==="
echo ""

# 1. ProtectSystem 버그 수정
echo "=== 1단계: ProtectSystem 버그 수정 ==="
bash scripts/evolution/fix_protectsystem_bug.sh
echo ""

# 2. 설치기 exit 0 보장
echo "=== 2단계: 설치기 exit 0 보장 ==="
bash scripts/evolution/fix_installer_exit.sh
echo ""

# 3. 검증 스크립트 파싱 버그 수정
echo "=== 3단계: 검증 스크립트 파싱 버그 수정 ==="
bash scripts/evolution/fix_verify_parsing_bug.sh
echo ""

# 4. 정상화 검증
echo "=== 4단계: 정상화 검증 ==="
bash scripts/evolution/normalization_check.sh
echo ""

echo "=== 원클릭 핫픽스 완료 ==="
echo ""
echo "다음 단계:"
echo "  bash scripts/evolution/preflight_l4.sh   # 프리플라이트"
echo "  bash scripts/evolution/run_l4_timeline.sh # 타임라인 실행"

