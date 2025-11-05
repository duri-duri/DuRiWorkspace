#!/usr/bin/env bash
# coldsync-install 디버깅 스크립트
# Usage: bash scripts/bin/debug_coldsync_install.sh

set -euo pipefail

echo "=== coldsync-install 디버깅 ==="
echo ""

echo "1. Service 상태:"
sudo systemctl status coldsync-install.service --no-pager -l || true
echo ""

echo "2. 최근 로그:"
sudo journalctl -u coldsync-install.service -n 50 --no-pager || true
echo ""

echo "3. 소스 파일 확인:"
SRC="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
if [ -f "$SRC" ]; then
    echo "✅ 소스 파일 존재: $SRC"
    ls -lh "$SRC"
    echo ""
    echo "첫 줄 (shebang):"
    head -1 "$SRC"
    echo ""
    echo "bash 문법 검증:"
    bash -n "$SRC" && echo "✅ 문법 OK" || echo "❌ 문법 오류"
else
    echo "❌ 소스 파일 없음: $SRC"
fi
echo ""

echo "4. 설치기 직접 실행 테스트:"
sudo /usr/local/sbin/coldsync-install 2>&1 || echo "실패 (위 로그 확인)"
echo ""

echo "5. Service 유닛 설정 확인:"
sudo systemctl cat coldsync-install.service | grep -E "ReadWritePaths|ExecStart" || true
echo ""

echo "6. Path 유닛 상태:"
sudo systemctl status coldsync-install.path --no-pager -l | head -15 || true

