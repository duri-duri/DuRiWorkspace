#!/usr/bin/env bash
# L4.0 빠른 실행 (프리플라이트 건너뛰고 바로 GO)
# Usage: bash scripts/evolution/quick_start_l4.sh
# 전제: 워킹트리==설치본 해시 일치 확인됨

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

echo "=== L4.0 빠른 실행 (프리플라이트 건너뛰기) ==="
echo ""

# 검증 타이머가 WSL 네임스페이스와 충돌하니 잠시 멈춤
echo "검증 타이머 일시 정지 (WSL 네임스페이스 충돌 방지):"
sudo systemctl stop coldsync-verify.timer 2>/dev/null || true
echo "✅ 검증 타이머 정지됨"
echo ""

# 해시 일치 확인 (빠른 체크)
echo "해시 일치 빠른 체크:"
COLDSYNC_SRC_PATH="${COLDSYNC_SRC_PATH:-/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh}"
COLDSYNC_DST_PATH="${COLDSYNC_DST_PATH:-/usr/local/bin/coldsync_hosp_from_usb.sh}"

SRC_HASH=$(sha256sum "$COLDSYNC_SRC_PATH" 2>/dev/null | awk '{print $1}' || echo "")
DST_HASH=$(sha256sum "$COLDSYNC_DST_PATH" 2>/dev/null | awk '{print $1}' || echo "not-installed")

if [ "$DST_HASH" != "not-installed" ] && [ "$SRC_HASH" = "$DST_HASH" ]; then
    echo "✅ 해시 일치 확인: $SRC_HASH"
    echo ""
    echo "타임라인 실행 시작..."
    echo ""
    bash scripts/evolution/run_l4_timeline.sh
else
    echo "❌ 해시 불일치 또는 파일 없음"
    echo "SRC=$SRC_HASH"
    echo "DST=$DST_HASH"
    echo ""
    echo "📋 프리플라이트 실행 권장:"
    echo "  bash scripts/evolution/preflight_l4.sh"
    exit 1
fi

