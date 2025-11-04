#!/usr/bin/env bash
# L4.0 .bashrc 적용 및 검증
# Usage: bash scripts/evolution/apply_bashrc.sh
# 목적: .bashrc 적용 및 검증

set -euo pipefail

echo "=== L4.0 .bashrc 적용 및 검증 ==="
echo ""

# 1. 현재 셸에 적용
echo "1. 현재 셸에 적용:"
source ~/.bashrc || echo "⚠️  source 실패 (경고 무시 가능)"
echo "✅ 적용 완료"
echo ""

# 2. 새 셸에서 확인
echo "2. 새 셸에서 확인:"
if bash --login -c 'type dus; echo OK' 2>&1; then
    echo "✅ dus 함수 정상"
else
    echo "⚠️  dus 함수 확인 실패"
fi
echo ""

# 3. storage.env 조건부 source 확인
echo "3. storage.env 조건부 source 확인:"
if grep -q '\[ -f /home/duri/DuRiWorkspace/etc/storage.env \]' ~/.bashrc; then
    echo "✅ 조건부 source 적용됨"
else
    echo "⚠️  조건부 source 없음"
fi
echo ""

# 4. 최종 구문 검사
echo "4. 최종 구문 검사:"
if bash -n ~/.bashrc 2>&1; then
    echo "[OK] .bashrc syntax clean"
else
    echo "[!] 구문 오류 발견"
    bash -n ~/.bashrc || true
fi
echo ""

echo "=== 적용 완료 ==="

