#!/usr/bin/env bash
# L4.0 마지막 3점 고정 (30초)
# Usage: bash scripts/evolution/finalize_l4_preflight.sh

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

echo "=== L4.0 마지막 3점 고정 (30초) ==="
echo ""

FAILED=0

# (1) 유닛/타이머 AC 스냅샷
echo "1. 유닛/타이머 AC 스냅샷:"
echo ""
UNIT_STATUS=$(systemctl status coldsync-install.path coldsync-verify.timer --no-pager 2>/dev/null || true)
if echo "$UNIT_STATUS" | grep -qE 'Loaded|Active'; then
    echo "$UNIT_STATUS" | grep -E 'Loaded|Active'
    echo "✅ 유닛 상태 확인됨"
else
    echo "⚠️  유닛 상태 확인 실패"
    ((FAILED++))
fi
echo ""

# (2) 해시 드리프트
echo "2. 해시 드리프트:"
echo ""
# 워킹트리 경로 우선 + ENV override
COLDSYNC_SRC_PATH="${COLDSYNC_SRC_PATH:-/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh}"
COLDSYNC_DST_PATH="${COLDSYNC_DST_PATH:-/usr/local/bin/coldsync_hosp_from_usb.sh}"

SRC_HASH=$(sha256sum "$COLDSYNC_SRC_PATH" 2>/dev/null | awk '{print $1}' || echo "")
DST_HASH=$(sha256sum "$COLDSYNC_DST_PATH" 2>/dev/null | awk '{print $1}' || echo "not-installed")

echo "SRC=$SRC_HASH"
echo "DST=$DST_HASH"

if [ "$DST_HASH" != "not-installed" ]; then
    if [ "$SRC_HASH" = "$DST_HASH" ]; then
        echo "✅ 해시 일치"
    else
        echo "⚠️  해시 불일치 감지"
        echo "📋 finalize 재실행 권장: bash scripts/bin/finalize_coldsync_autodeploy.sh"
        ((FAILED++))
    fi
else
    echo "ℹ️  아직 설치되지 않음 (정상)"
fi
echo ""

# (3) oneline 스크립트 일관성
echo "3. oneline 스크립트 일관성:"
echo ""
if test -x scripts/bin/status_coldsync_oneline.sh; then
    echo "✅ status_coldsync_oneline.sh 존재/실행권한 OK"
else
    echo "❌ status_coldsync_oneline.sh 없음/실행권한 없음"
    ((FAILED++))
fi
echo ""

# 최종 결과
if [ $FAILED -eq 0 ]; then
    echo "=== 마지막 3점 고정 완료 ==="
    echo "✅ 모든 체크 통과"
    echo ""
    echo "📋 다음 단계:"
    echo "  bash scripts/evolution/preflight_l4.sh"
    echo "  bash scripts/evolution/run_l4_timeline.sh"
    exit 0
else
    echo "=== 마지막 3점 고정 실패 ==="
    echo "❌ 일부 체크 실패 ($FAILED건)"
    echo ""
    echo "📋 복구 후 재시도 필요"
    exit 1
fi

