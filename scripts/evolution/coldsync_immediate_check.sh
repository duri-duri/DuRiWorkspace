#!/usr/bin/env bash
# L4.0 coldsync 즉시 조치 3-step 검증
# Usage: bash scripts/evolution/coldsync_immediate_check.sh
# 목적: 강제 동기화, Path 유닛 확인, ExecStart 확인

set -euo pipefail

echo "=== L4.0 coldsync 즉시 조치 3-step 검증 ==="
echo ""

# Step 1: 강제 동기화 + 확인
echo "=== Step 1: 강제 동기화 + 확인 ==="
cold-run && sleep 1 && cold-hash
echo ""

# Step 2: Path 유닛 확인
echo "=== Step 2: Path 유닛 확인 ==="
SRC_ABS="$HOME/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
EXPECTED_PATH="PathChanged=${SRC_ABS}"

ACTUAL_PATH=$(systemctl --user cat coldsync-install.path 2>/dev/null | grep -E '^(PathChanged|PathModified)=' | head -1 || echo "")

if [ -n "$ACTUAL_PATH" ]; then
    echo "✅ Path 유닛 설정:"
    systemctl --user cat coldsync-install.path | grep -E '^(PathChanged|PathModified|Unit)=' || true
else
    echo "❌ Path 유닛 설정 확인 실패"
fi
echo ""

# 절대 경로 확인
if echo "$ACTUAL_PATH" | grep -q "^PathChanged=${SRC_ABS}\|^PathModified=${SRC_ABS}"; then
    echo "✅ 절대 경로 사용 확인"
else
    echo "⚠️  경로가 절대 경로가 아닐 수 있음"
    echo "   기대: PathChanged=${SRC_ABS}"
    echo "   실제: ${ACTUAL_PATH}"
fi
echo ""

# Step 3: ExecStart 확인
echo "=== Step 3: ExecStart 확인 ==="
EXEC_START=$(systemctl --user cat coldsync-install.service 2>/dev/null | grep -E '^ExecStart=' | head -1 || echo "")

if [ -n "$EXEC_START" ]; then
    echo "✅ ExecStart 설정:"
    echo "$EXEC_START"
    
    # 래퍼 경로 확인
    if echo "$EXEC_START" | grep -q 'coldsync_install_debounced.sh'; then
        echo "✅ 디바운스 래퍼 사용 확인"
    else
        echo "⚠️  디바운스 래퍼 미사용 가능성"
    fi
else
    echo "❌ ExecStart 설정 확인 실패"
fi
echo ""

# 해시 일치 확인
echo "=== 최종 해시 확인 ==="
SRC_HASH=$(sha256sum "$SRC_ABS" 2>/dev/null | awk '{print $1}' || echo "")
DST_HASH=$(sha256sum "$HOME/.local/bin/coldsync_hosp_from_usb.sh" 2>/dev/null | awk '{print $1}' || echo "")

if [ "$SRC_HASH" = "$DST_HASH" ] && [ -n "$SRC_HASH" ]; then
    echo "✅ 해시 일치: ${SRC_HASH}"
else
    echo "⚠️  해시 불일치:"
    echo "   SRC: ${SRC_HASH}"
    echo "   DST: ${DST_HASH}"
fi
echo ""

echo "=== 즉시 조치 검증 완료 ==="

