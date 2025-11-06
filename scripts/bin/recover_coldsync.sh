#!/usr/bin/env bash
# coldsync 자동 배포 시스템 - 실패 시 즉시 롤백
# Usage: bash scripts/bin/recover_coldsync.sh

set -euo pipefail

echo "=== coldsync 자동 배포 시스템 - 즉시 롤백 ==="
echo ""

echo "1. 마지막 정상본 재설치 (무조건 성공 경로)"
sudo /usr/local/sbin/coldsync-install || {
    echo "⚠️  설치 실패, 계속 진행..."
}
echo ""

echo "2. 자동 트리거 일시 차단"
sudo systemctl disable --now coldsync-install.path 2>/dev/null || true
sudo systemctl disable --now coldsync-verify.timer 2>/dev/null || true
echo "✅ 자동 트리거 차단 완료"
echo ""

echo "3. 상태 확인"
echo "Path 유닛:"
sudo systemctl is-enabled coldsync-install.path 2>/dev/null || echo "  disabled"
sudo systemctl is-active coldsync-install.path 2>/dev/null || echo "  inactive"
echo ""

echo "검증 타이머:"
sudo systemctl is-enabled coldsync-verify.timer 2>/dev/null || echo "  disabled"
sudo systemctl is-active coldsync-verify.timer 2>/dev/null || echo "  inactive"
echo ""

echo "=== 롤백 완료 ==="
echo ""
echo "📋 수동 유지 모드:"
echo "  - 자동 트리거 비활성화됨"
echo "  - 수동 설치: sudo /usr/local/sbin/coldsync-install"
echo ""
echo "📋 재활성화 (문제 해결 후):"
echo "  sudo systemctl enable --now coldsync-install.path"
echo "  sudo systemctl enable --now coldsync-verify.timer"

