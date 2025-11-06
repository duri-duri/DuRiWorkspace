#!/usr/bin/env bash
# coldsync 자동 배포 시스템 - 완전 롤백 (원상복구)
# Usage: bash scripts/bin/rollback_coldsync.sh

set -euo pipefail

echo "=== coldsync 자동 배포 시스템 - 완전 롤백 (원상복구) ==="
echo ""

read -p "정말로 모든 coldsync 자동 배포 시스템을 제거하시겠습니까? (y/N): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "롤백 취소됨"
    exit 0
fi

echo ""

echo "1. 서비스 중지 및 제거"
sudo systemctl disable --now coldsync-install.path 2>/dev/null || true
sudo systemctl disable --now coldsync-verify.timer 2>/dev/null || true
echo "✅ 서비스 중지 완료"
echo ""

echo "2. 유닛 파일 제거"
sudo rm -f /etc/systemd/system/coldsync-install.{service,path} 2>/dev/null || true
sudo rm -f /etc/systemd/system/coldsync-verify.{service,timer} 2>/dev/null || true
sudo rm -f /etc/systemd/system/systemd-notify@.service 2>/dev/null || true
echo "✅ 유닛 파일 제거 완료"
echo ""

echo "3. 설치기 제거"
sudo rm -f /usr/local/sbin/coldsync-install 2>/dev/null || true
echo "✅ 설치기 제거 완료"
echo ""

echo "4. 상태 파일 제거"
sudo rm -rf /var/lib/coldsync-hosp 2>/dev/null || true
echo "✅ 상태 파일 제거 완료"
echo ""

echo "5. inotify 설정 제거"
sudo rm -f /etc/sysctl.d/99-coldsync.conf 2>/dev/null || true
sudo sysctl --system > /dev/null 2>&1 || true
echo "✅ inotify 설정 제거 완료"
echo ""

echo "6. systemd 재로드"
sudo systemctl daemon-reload
echo "✅ systemd 재로드 완료"
echo ""

echo "=== 완전 롤백 완료 ==="
echo ""
echo "📋 남은 파일:"
echo "  - 작업본: ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
echo "  - 설치본: /usr/local/bin/coldsync_hosp_from_usb.sh (수동 관리 필요)"
echo ""
echo "📋 재설치:"
echo "  bash scripts/bin/finalize_coldsync_autodeploy.sh"

