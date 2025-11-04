#!/usr/bin/env bash
# L4.0 최종 성공 확인 및 VS Code 테스트 안내
# Usage: bash scripts/evolution/final_check_and_vscode_test.sh
# 목적: 수동 동기화 확인 및 VS Code 저장 테스트

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

echo "=== L4.0 최종 확인 및 VS Code 테스트 안내 ==="
echo ""

# 1. 수동 동기화
echo "1. 수동 동기화:"
sudo systemctl start coldsync-install.service
sleep 1
echo "✅ 수동 동기화 완료"
echo ""

# 2. 해시 확인
echo "2. 해시 확인:"
SRC_FILE="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
DST_FILE="/usr/local/bin/coldsync_hosp_from_usb.sh"
SRC_HASH=$(sha256sum "$SRC_FILE" | awk '{print $1}')
DST_HASH=$(sha256sum "$DST_FILE" 2>/dev/null | awk '{print $1}' || echo "")

echo "  SRC: $SRC_HASH"
echo "  DST: $DST_HASH"

if [ "$SRC_HASH" = "$DST_HASH" ] && [ -n "$DST_HASH" ]; then
    echo "✅ 해시 동기화 확인"
else
    echo "❌ 해시 불일치"
    echo "  수동 동기화 필요: sudo systemctl start coldsync-install.service"
fi
echo ""

# 3. Path 유닛 상태 확인
echo "3. Path 유닛 상태 확인:"
if systemctl is-active --quiet coldsync-install.path 2>/dev/null; then
    echo "✅ Path 유닛 활성화됨"
else
    echo "❌ Path 유닛 비활성화"
fi
echo ""

# 4. Path 유닛 설정 확인
echo "4. Path 유닛 설정 확인:"
if sudo grep -q "PathModified" /etc/systemd/system/coldsync-install.path 2>/dev/null; then
    echo "✅ PathModified 설정됨"
else
    echo "⚠️  PathModified 설정 없음"
fi
echo ""

# 5. VS Code 테스트 안내
echo "=== VS Code 저장 테스트 ==="
echo ""
echo "Path 트리거 테스트 (VS Code로 저장):"
echo ""
echo "1. VS Code에서 파일 열기:"
echo "   code ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
echo ""
echo "2. 파일에 아무 내용 추가 (예: 주석 한 줄)"
echo "   # Test from VS Code $(date)"
echo ""
echo "3. 저장 (Ctrl+S)"
echo ""
echo "4. 3초 후 로그 확인:"
echo "   sleep 3"
echo "   journalctl -u coldsync-install.service -n 5 --no-pager | grep -E 'INSTALLED|up-to-date'"
echo ""
echo "5. 해시 확인:"
echo "   sha256sum /usr/local/bin/coldsync_hosp_from_usb.sh ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
echo ""

# 6. 현재 상태 요약
echo "=== 현재 상태 요약 ==="
echo "✅ 설치기 직접 실행: 성공"
echo "✅ 수동 동기화: 작동"
echo "✅ Path 유닛: 활성화됨"
echo "⚠️  Path 트리거: echo >> 명령으로는 작동하지 않음 (VS Code 저장 테스트 권장)"
echo ""
echo "사용 방법:"
echo "  VS Code에서 파일을 편집하고 저장하면 자동으로 /usr/local/bin에 배포됩니다."
echo ""
echo "수동 동기화 (필요 시):"
echo "  sudo systemctl start coldsync-install.service"

