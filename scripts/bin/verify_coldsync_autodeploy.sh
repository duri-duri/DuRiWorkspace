#!/usr/bin/env bash
# coldsync 자동 배포 시스템 - 동작 확인 스크립트
# Usage: bash scripts/bin/verify_coldsync_autodeploy.sh

set -euo pipefail

echo "=== coldsync 자동 배포 시스템 검증 ==="
echo ""

echo "1. 설치기 확인:"
if [ -x /usr/local/sbin/coldsync-install ]; then
    echo "✅ 설치기 존재: /usr/local/sbin/coldsync-install"
    ls -lh /usr/local/sbin/coldsync-install
else
    echo "❌ 설치기 없음"
    exit 1
fi
echo ""

echo "2. systemd 유닛 확인:"
if systemctl list-unit-files | grep -q coldsync-install.path; then
    echo "✅ Path 유닛 등록됨"
else
    echo "❌ Path 유닛 없음"
    exit 1
fi
echo ""

echo "3. Path 유닛 상태:"
sudo systemctl status coldsync-install.path --no-pager -l | head -15 || true
echo ""

echo "4. 수동 트리거 테스트:"
sudo systemctl start coldsync-install.service
sleep 1
echo ""
echo "Service 상태:"
sudo systemctl status coldsync-install.service --no-pager -l | head -25 || true
echo ""

echo "5. 로그 확인:"
sudo journalctl -u coldsync-install.service -n 20 --no-pager || true
echo ""

echo "6. 파일 동기화 확인:"
SRC="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
DST="/usr/local/bin/coldsync_hosp_from_usb.sh"

if [ -f "$SRC" ] && [ -f "$DST" ]; then
    echo "SHA256 비교:"
    SHA_SRC=$(sha256sum "$SRC" | awk '{print $1}')
    SHA_DST=$(sha256sum "$DST" | awk '{print $1}')
    
    if [ "$SHA_SRC" = "$SHA_DST" ]; then
        echo "✅ 파일 동기화 OK (해시 일치)"
    else
        echo "⚠️  파일 동기화 안됨 (해시 불일치)"
        echo "  소스: $SHA_SRC"
        echo "  대상: $SHA_DST"
    fi
    
    echo ""
    echo "파일 정보:"
    ls -lh "$SRC" "$DST"
else
    echo "❌ 파일 없음"
    echo "  소스: $SRC ($([ -f "$SRC" ] && echo "존재" || echo "없음"))"
    echo "  대상: $DST ($([ -f "$DST" ] && echo "존재" || echo "없음"))"
fi
echo ""

echo "7. 저장 트리거 검증:"
echo "작업본에 테스트 변경 추가..."
echo "# Auto-deploy test $(date +%F\ %T)" >> "$SRC"
echo "변경 완료. Path 감지 대기 중 (2초)..."
sleep 2
echo ""
echo "최근 로그 (10줄):"
sudo journalctl -u coldsync-install.service -n 10 --no-pager || true
echo ""

echo "8. 최종 검증:"
if [ -f "$SRC" ] && [ -f "$DST" ]; then
    SHA_SRC=$(sha256sum "$SRC" | awk '{print $1}')
    SHA_DST=$(sha256sum "$DST" | awk '{print $1}')
    
    if [ "$SHA_SRC" = "$SHA_DST" ]; then
        echo "✅ 자동 배포 성공! 두 파일의 해시가 일치합니다."
    else
        echo "⚠️  자동 배포 실패 또는 진행 중"
    fi
else
    echo "❌ 파일 확인 실패"
fi
echo ""

echo "9. Path 유닛 활성 상태:"
if sudo systemctl is-active coldsync-install.path >/dev/null 2>&1; then
    echo "✅ Path 유닛 활성"
else
    echo "❌ Path 유닛 비활성"
fi

if sudo systemctl is-enabled coldsync-install.path >/dev/null 2>&1; then
    echo "✅ Path 유닛 자동 시작 설정됨"
else
    echo "⚠️  Path 유닛 자동 시작 설정 안됨"
fi
echo ""

echo "=== 검증 완료 ==="
echo ""
echo "📋 사용법:"
echo "  code ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
echo "  (저장하면 자동 배포됨)"
echo ""
echo "📋 로그 확인:"
echo "  sudo journalctl -u coldsync-install.service -f"

