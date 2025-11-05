#!/usr/bin/env bash
# L4.0 coldsync 회귀 테스트 (강화 버전)
# Usage: bash scripts/evolution/coldsync_regression.sh
# 목적: 자동 배포 시스템 회귀 테스트

set -euo pipefail

SRC="$HOME/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
DST="$HOME/.local/bin/coldsync_hosp_from_usb.sh"

echo "=== L4.0 coldsync 회귀 테스트 ==="
echo ""

# 1. 파일 변경
echo "1. 파일 변경 (회귀 테스트용):"
echo "# regression $(date +%s)" >> "$SRC"
echo "✅ 파일 변경 완료"
echo ""

# 2. 대기
echo "2. 3초 대기 (Path 트리거 대기)..."
sleep 3
echo ""

# 3. 로그 확인
echo "3. 로그 확인:"
LOG_OUTPUT=$(journalctl --user -u coldsync-install.service -n 5 --no-pager 2>/dev/null || echo "")
if echo "$LOG_OUTPUT" | grep -qE '\[INSTALLED\]|\[up-to-date\]'; then
    echo "✅ 트리거 작동 확인"
    echo "$LOG_OUTPUT" | grep -E '\[INSTALLED\]|\[up-to-date\]' | tail -1
else
    echo "❌ 트리거 작동 안됨"
    echo "  로그:"
    echo "$LOG_OUTPUT"
    exit 1
fi
echo ""

# 4. 해시 확인 (안전 파싱)
echo "4. 해시 확인:"
SRC_HASH=$(sha256sum "$SRC" 2>/dev/null | awk '{print $1}' || echo "")
DST_HASH=$(sha256sum "$DST" 2>/dev/null | awk '{print $1}' || echo "")

# 숫자 강제 정규화 (안전 파싱)
SRC_HASH="${SRC_HASH//[^0-9a-f]/}"
DST_HASH="${DST_HASH//[^0-9a-f]/}"

if [ -z "$SRC_HASH" ] || [ -z "$DST_HASH" ]; then
    echo "❌ [FAIL] 해시 추출 실패"
    echo "  SRC: $SRC_HASH"
    echo "  DST: $DST_HASH"
    exit 1
fi

UNIQ_COUNT=$(echo -e "$SRC_HASH\n$DST_HASH" | sort -u | wc -l | tr -cd '0-9')
UNIQ_COUNT="${UNIQ_COUNT:-0}"

if [ "$UNIQ_COUNT" -eq 1 ]; then
    echo "✅ [OK] hash match"
    echo "  해시: $SRC_HASH"
else
    echo "❌ [FAIL] hash mismatch"
    echo "  SRC: $SRC_HASH"
    echo "  DST: $DST_HASH"
    exit 1
fi
echo ""

echo "=== 회귀 테스트 통과 ==="
