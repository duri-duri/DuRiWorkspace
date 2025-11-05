#!/usr/bin/env bash
# L4.0 .bashrc 오류 원인 확인
# Usage: bash scripts/evolution/check_bashrc_errors.sh
# 목적: .bashrc 구문 오류 원인 진단

set -euo pipefail

echo "=== L4.0 .bashrc 오류 원인 확인 ==="
echo ""

# 1. 206번 줄 전후 확인
echo "1. 206번 줄 전후 확인:"
nl -ba ~/.bashrc | sed -n '190,220p'
echo ""

# 2. 제어문자 확인
echo "2. 제어문자 확인 (200-212줄):"
sed -n '200,212p' ~/.bashrc | sed -n l
echo ""

# 3. 구문 검사
echo "3. 구문 검사:"
if bash -n ~/.bashrc 2>&1; then
    echo "[OK] 구문 오류 없음"
else
    echo "[!] 구문 오류 존재"
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
fi
echo ""

# 4. storage.env source 확인
echo "4. storage.env source 확인:"
if grep -q 'DuRiWorkspace/etc/storage.env' ~/.bashrc; then
    echo "[!] storage.env source 발견:"
    grep -n 'DuRiWorkspace/etc/storage.env' ~/.bashrc
else
    echo "[OK] storage.env source 없음"
fi
echo ""

# 5. dus() 함수 확인
echo "5. dus() 함수 확인:"
if grep -q '^dus()' ~/.bashrc; then
    echo "[!] dus() 함수 발견:"
    grep -n '^dus()' ~/.bashrc
else
    echo "[OK] dus() 함수 없음"
fi
echo ""

echo "=== 확인 완료 ==="

