#!/usr/bin/env bash
# L4.0 서비스 실패 원인 진단 (WSL에서 실행)
# Usage: bash scripts/evolution/diagnose_service_failure.sh

set -euo pipefail

echo "=== L4.0 서비스 실패 원인 진단 ==="
echo ""

# 1. 서비스 상태 확인
echo "1. 서비스 상태:"
systemctl status coldsync-install.service --no-pager | head -30 || true
echo ""

# 2. 최근 로그 확인
echo "2. 최근 로그 (최근 100줄):"
journalctl -xeu coldsync-install.service -n 100 --no-pager | tail -50 || echo "로그 없음"
echo ""

# 3. override.conf 확인
echo "3. override.conf 내용:"
cat /etc/systemd/system/coldsync-install.service.d/override.conf 2>/dev/null || echo "override.conf 없음"
echo ""

# 4. 전체 서비스 파일 확인
echo "4. 전체 서비스 파일 (systemctl cat):"
systemctl cat coldsync-install.service || echo "서비스 파일 없음"
echo ""

# 5. 설치기 파일 확인
echo "5. 설치기 파일 확인:"
INSTALLER="/usr/local/sbin/coldsync-install"
if [ -f "$INSTALLER" ]; then
    echo "✅ 설치기 존재: $INSTALLER"
    ls -la "$INSTALLER"
    echo ""
    echo "첫 5줄:"
    head -5 "$INSTALLER"
    echo ""
    echo "문법 검사:"
    bash -n "$INSTALLER" 2>&1 || echo "문법 오류 있음"
else
    echo "❌ 설치기 없음: $INSTALLER"
fi
echo ""

# 6. 소스 파일 확인
echo "6. 소스 파일 확인:"
SRC_FILE="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
if [ -f "$SRC_FILE" ]; then
    echo "✅ 소스 파일 존재: $SRC_FILE"
    ls -la "$SRC_FILE"
else
    echo "❌ 소스 파일 없음: $SRC_FILE"
fi
echo ""

# 7. 권한 확인
echo "7. 권한 확인:"
echo "설치기 실행 권한:"
test -x "$INSTALLER" && echo "✅ 실행 가능" || echo "❌ 실행 불가"
echo ""

# 8. 수동 실행 테스트
echo "8. 설치기 수동 실행 테스트:"
if [ -f "$INSTALLER" ] && [ -x "$INSTALLER" ]; then
    echo "테스트 실행 중..."
    sudo "$INSTALLER" 2>&1 || echo "수동 실행 실패"
else
    echo "⚠️  설치기 파일 없음 또는 실행 불가"
fi
echo ""

echo "=== 진단 완료 ==="

