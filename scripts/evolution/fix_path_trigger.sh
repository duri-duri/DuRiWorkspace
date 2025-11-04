#!/usr/bin/env bash
# L4.0 Path 트리거 문제 해결 및 최종 동기화
# Usage: bash scripts/evolution/fix_path_trigger.sh
# 목적: Path 트리거 문제 해결 및 즉시 동기화

set -euo pipefail

echo "=== L4.0 Path 트리거 문제 해결 ==="
echo ""

# 1. 수동 동기화 (즉시 해시 동기화)
echo "1. 수동 동기화 (즉시 해시 동기화):"
sudo systemctl start coldsync-install.service
if [ $? -eq 0 ]; then
    echo "✅ 수동 동기화 완료"
else
    echo "❌ 수동 동기화 실패"
    exit 1
fi
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
    exit 1
fi
echo ""

# 3. Path 유닛 재시작 (변경 감지 리셋)
echo "3. Path 유닛 재시작:"
sudo systemctl restart coldsync-install.path
if systemctl is-active --quiet coldsync-install.path 2>/dev/null; then
    echo "✅ Path 유닛 재시작 완료"
else
    echo "❌ Path 유닛 재시작 실패"
    exit 1
fi
echo ""

# 4. Path 트리거 테스트 (VS Code로 파일 저장 권장)
echo "4. Path 트리거 테스트:"
echo "  VS Code에서 파일을 저장하거나 아래 명령으로 테스트:"
echo ""
echo "  # 테스트 1: 직접 편집"
echo "  echo '# Path trigger test $(date)' >> $SRC_FILE"
echo "  sleep 3"
echo "  journalctl -u coldsync-install.service -n 3 --no-pager"
echo ""
echo "  # 테스트 2: touch로 메타데이터 변경"
echo "  touch $SRC_FILE"
echo "  sleep 3"
echo "  journalctl -u coldsync-install.service -n 3 --no-pager"
echo ""

# 5. 로그 확인
echo "5. 최근 로그 확인:"
journalctl -u coldsync-install.service -n 5 --no-pager | grep -E "INSTALLED|up-to-date" || echo "  (최근 로그 없음)"
echo ""

echo "=== Path 트리거 문제 해결 완료 ==="
echo ""
echo "참고:"
echo "  - PathChanged는 파일 내용 변경을 감지합니다"
echo "  - VS Code로 저장하면 자동으로 트리거됩니다"
echo "  - echo >> 명령은 때때로 inotify 이벤트를 발생시키지 않을 수 있습니다"

