#!/usr/bin/env bash
# L4.0 A안 coldsync 트리거 테스트
# Usage: bash scripts/evolution/test_coldsync_trigger.sh
# 목적: VS Code 저장 시 자동 동기화 테스트

set -euo pipefail

echo "=== L4.0 A안 coldsync 트리거 테스트 ==="
echo ""

# 1. Path 유닛 상태 확인
echo "1. Path 유닛 상태 확인:"
if systemctl --user is-active --quiet coldsync-install.path 2>/dev/null; then
    echo "✅ Path 유닛 활성화됨"
else
    echo "❌ Path 유닛 비활성화"
    echo "  활성화: systemctl --user enable --now coldsync-install.path"
    exit 1
fi
echo ""

# 2. 파일 변경 (PathChanged 이벤트 보장)
echo "2. 파일 변경 (PathChanged 이벤트 보장):"
SRC_FILE="$HOME/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
printf '\n# VSCode trigger test %s\n' "$(date)" >> "$SRC_FILE"
echo "✅ 파일 변경 완료"
echo ""

# 3. 3초 대기
echo "3. 3초 대기 (Path 트리거 대기)..."
sleep 3
echo ""

# 4. 로그 확인
echo "4. 로그 확인:"
LOG_OUTPUT=$(journalctl --user -u coldsync-install.service -n 8 --no-pager 2>/dev/null || echo "")
if echo "$LOG_OUTPUT" | grep -qE 'INSTALLED|up-to-date'; then
    echo "✅ 트리거 작동 확인"
    echo "$LOG_OUTPUT" | grep -E 'INSTALLED|up-to-date' | tail -1
else
    echo "⚠️  트리거 작동 안됨 (재시도)"
    echo ""
    echo "재시도:"
    systemctl --user daemon-reload
    systemctl --user restart coldsync-install.path
    printf '\n# retrigger %s\n' "$(date)" >> "$SRC_FILE"
    sleep 3
    LOG_OUTPUT=$(journalctl --user -u coldsync-install.service -n 8 --no-pager 2>/dev/null || echo "")
    if echo "$LOG_OUTPUT" | grep -qE 'INSTALLED|up-to-date'; then
        echo "✅ 재시도 후 트리거 작동 확인"
        echo "$LOG_OUTPUT" | grep -E 'INSTALLED|up-to-date' | tail -1
    else
        echo "❌ 재시도 후에도 트리거 작동 안됨"
    fi
fi
echo ""

# 5. 해시 확인
echo "5. 해시 확인:"
DST_FILE="$HOME/.local/bin/coldsync_hosp_from_usb.sh"
if [ -f "$DST_FILE" ]; then
    SRC_HASH=$(sha256sum "$SRC_FILE" | awk '{print $1}')
    DST_HASH=$(sha256sum "$DST_FILE" | awk '{print $1}')
    echo "  SRC: $SRC_HASH"
    echo "  DST: $DST_HASH"
    if [ "$SRC_HASH" = "$DST_HASH" ]; then
        echo "✅ 해시 동기화 확인"
    else
        echo "❌ 해시 불일치"
        echo "  수동 동기화: systemctl --user start coldsync-install.service"
    fi
else
    echo "❌ 대상 파일 없음: $DST_FILE"
fi
echo ""

echo "=== 테스트 완료 ==="

