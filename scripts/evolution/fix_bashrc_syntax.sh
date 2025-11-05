#!/usr/bin/env bash
# L4.0 .bashrc 문법 오류 수정
# Usage: bash scripts/evolution/fix_bashrc_syntax.sh
# 목적: line 206 문법 오류 수정

set -euo pipefail

echo "=== L4.0 .bashrc 문법 오류 수정 ==="
echo ""

# 백업
echo "1. .bashrc 백업:"
cp ~/.bashrc ~/.bashrc.bak.$(date +%s)
echo "✅ 백업 완료"
echo ""

# line 206 수정
echo "2. line 206 수정:"
if grep -q "^dus()" ~/.bashrc; then
    # 기존 라인 찾아서 수정
    sed -i 's/^dus() *{.*systemctl --user.*}/dus() { systemctl --user "$@"; }/' ~/.bashrc
    echo "✅ line 206 수정 완료"
else
    echo "⚠️  line 206에 dus() 함수 없음 (추가 예정)"
    echo 'dus() { systemctl --user "$@"; }' >> ~/.bashrc
fi
echo ""

# CRLF 제거
echo "3. CRLF 제거:"
sed -i 's/\r$//' ~/.bashrc
echo "✅ CRLF 제거 완료"
echo ""

# 문법 검사
echo "4. 문법 검사:"
if bash -n ~/.bashrc 2>/dev/null; then
    echo "✅ 문법 검사 통과"
else
    echo "❌ 문법 오류 발견"
    bash -n ~/.bashrc || true
fi
echo ""

echo "=== .bashrc 수정 완료 ==="
echo ""
echo "적용:"
echo "  source ~/.bashrc"

