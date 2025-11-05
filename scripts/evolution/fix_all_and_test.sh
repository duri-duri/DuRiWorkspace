#!/usr/bin/env bash
# L4.0 .bashrc 오류 수정 및 coldsync 테스트 통합
# Usage: bash scripts/evolution/fix_all_and_test.sh
# 목적: .bashrc 수정 + coldsync 트리거 테스트를 한 번에

set -euo pipefail

echo "=== L4.0 .bashrc 수정 및 coldsync 테스트 통합 ==="
echo ""

# 1. .bashrc 오류 확인
echo "=== 1단계: .bashrc 오류 확인 ==="
bash scripts/evolution/check_bashrc_errors.sh
echo ""

# 2. .bashrc 안전 패치
echo "=== 2단계: .bashrc 안전 패치 ==="
bash scripts/evolution/fix_bashrc_safe.sh
echo ""

# 3. .bashrc 적용
echo "=== 3단계: .bashrc 적용 ==="
bash scripts/evolution/apply_bashrc.sh
echo ""

# 4. coldsync 트리거 테스트
echo "=== 4단계: coldsync 트리거 테스트 ==="
bash scripts/evolution/test_coldsync_trigger.sh
echo ""

echo "=== 모든 단계 완료 ==="

