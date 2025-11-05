#!/usr/bin/env bash
# L4.0 .bashrc 최종 고정 (storage.env 가드 확실히)
# Usage: bash scripts/evolution/fix_bashrc_final.sh
# 목적: storage.env 조건부 source 확실히 적용

set -euo pipefail

echo "=== L4.0 .bashrc 최종 고정 ==="
echo ""

# 백업
echo "1. .bashrc 백업:"
cp ~/.bashrc ~/.bashrc.bak.$(date +%s)
echo "✅ 백업 완료"
echo ""

# 2. 기존 storage.env source 제거 (있다면)
echo "2. 기존 storage.env source 제거:"
sed -i '/source.*storage\.env/d' ~/.bashrc 2>/dev/null || true
sed -i '/\. .*storage\.env/d' ~/.bashrc 2>/dev/null || true
echo "✅ 제거 완료"
echo ""

# 3. 가드 블록 추가 (맨 아래)
echo "3. 가드 블록 추가:"
if ! grep -q "=== begin: guard autosave_dev_context/storage.env ===" ~/.bashrc; then
    cat >> ~/.bashrc <<'GUARD'

# ==== begin: guard autosave_dev_context/storage.env ====
AS_DEV="$HOME/DuRiWorkspace/shared-scripts/autosave_dev_context.sh"
AS_ENV="$HOME/DuRiWorkspace/etc/storage.env"

# storage.env는 있을 때만 읽는다(무음 패스)
[ -f "$AS_ENV" ] && . "$AS_ENV"

# autosave 스크립트는 존재+실행권한 시에만 실행(무음 패스)
if [ -x "$AS_DEV" ]; then
  "$AS_DEV" || true
fi
# ==== end: guard autosave_dev_context/storage.env ====
GUARD
    echo "✅ 가드 블록 추가 완료"
else
    echo "✅ 가드 블록 이미 존재"
fi
echo ""

# 4. CRLF 제거
echo "4. CRLF 제거:"
sed -i 's/\r$//' ~/.bashrc
echo "✅ CRLF 제거 완료"
echo ""

# 5. 구문 검사
echo "5. 구문 검사:"
if bash -n ~/.bashrc 2>&1; then
    echo "✅ [OK] bashrc syntax clean"
else
    echo "❌ [FAIL] 구문 오류 발견"
    bash -n ~/.bashrc || true
    exit 1
fi
echo ""

# 6. 적용 테스트
echo "6. 적용 테스트:"
if bash --login -c 'echo "bashrc loaded OK"' 2>&1; then
    echo "✅ 적용 테스트 통과"
else
    echo "⚠️  적용 테스트 실패 (경고 무시 가능)"
fi
echo ""

echo "=== 최종 고정 완료 ==="
echo ""
echo "적용:"
echo "  source ~/.bashrc"

