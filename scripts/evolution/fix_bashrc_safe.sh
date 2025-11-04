#!/usr/bin/env bash
# L4.0 .bashrc 안전 패치 (조건부 source + CRLF 제거 + 함수 재정의)
# Usage: bash scripts/evolution/fix_bashrc_safe.sh
# 목적: .bashrc 구문 오류 완전 수정

set -euo pipefail

echo "=== L4.0 .bashrc 안전 패치 ==="
echo ""

# 백업
echo "1. .bashrc 백업:"
cp ~/.bashrc ~/.bashrc.bak.$(date +%s)
echo "✅ 백업 완료: ~/.bashrc.bak.$(date +%s)"
echo ""

# 2-1) storage.env 조건부 source
echo "2-1. storage.env 조건부 source 패치:"
if grep -q 'DuRiWorkspace/etc/storage.env' ~/.bashrc; then
    sed -i 's|\(source\|\. \)\s\+/home/duri/DuRiWorkspace/etc/storage.env|[ -f /home/duri/DuRiWorkspace/etc/storage.env ] \&\& source /home/duri/DuRiWorkspace/etc/storage.env|' ~/.bashrc
    echo "✅ storage.env 조건부 source 적용"
else
    echo "⚠️  storage.env source 없음 (스킵)"
fi
echo ""

# 2-2) CRLF 제거
echo "2-2. CRLF 제거:"
sed -i 's/\r$//' ~/.bashrc
echo "✅ CRLF 제거 완료"
echo ""

# 2-3) dus() 함수 재정의
echo "2-3. dus() 함수 재정의:"
awk '{
  if ($0 ~ /^dus\(\)/) {print "dus() { systemctl --user \"$@\"; }"; skip=1; next}
  if (skip) { if ($0 ~ /^\}/) {skip=0; next} else {next} }
  print
}' ~/.bashrc > ~/.bashrc.fixed && mv ~/.bashrc.fixed ~/.bashrc
echo "✅ dus() 함수 재정의 완료"
echo ""

# 2-4) 구문 검사
echo "2-4. 구문 검사:"
if bash -n ~/.bashrc 2>&1; then
    echo "[OK] .bashrc syntax clean"
else
    echo "[!] 여전히 오류"
    echo ""
    echo "오류 상세:"
    bash -n ~/.bashrc 2>&1 | sed -n l
    echo ""
    ERR_LINE=$(bash -n ~/.bashrc 2>&1 | grep -oE 'line [0-9]+' | head -1 | grep -oE '[0-9]+' || echo "")
    if [ -n "$ERR_LINE" ]; then
        echo "오류 줄 번호: $ERR_LINE"
        echo "오류 줄 전후:"
        nl -ba ~/.bashrc | sed -n "$((ERR_LINE-5)),$((ERR_LINE+5))p"
    fi
    exit 1
fi
echo ""

echo "=== 패치 완료 ==="
echo ""
echo "다음 단계:"
echo "  source ~/.bashrc"

