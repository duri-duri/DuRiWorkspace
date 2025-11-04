#!/usr/bin/env bash
# L4.0 NAMESPACE 에러 원인 검증 (WSL에서 실행)
# Usage: bash scripts/evolution/verify_namespace_fix.sh
# 목적: 증거 3점으로 확정

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

echo "=== L4.0 NAMESPACE 에러 원인 검증 (증거 3점) ==="
echo ""

PASS_COUNT=0
FAIL_COUNT=0

# A. 이름공간 오류 소거 확인
echo "A. 이름공간 오류 소거 확인 (최근 30줄):"
NAMESPACE_ERRORS=$(journalctl -xeu coldsync-install.service -n 30 2>/dev/null | grep -cE 'NAMESPACE|Failed to set up mount namespacing' || echo "0")
NAMESPACE_ERRORS=$(echo "$NAMESPACE_ERRORS" | tr -d '[:space:]')
NAMESPACE_ERRORS=${NAMESPACE_ERRORS:-0}
if [ "${NAMESPACE_ERRORS:-0}" -eq 0 ]; then
    echo "✅ [OK] no namespace errors"
    ((PASS_COUNT++))
else
    echo "❌ [FAIL] namespace errors detected ($NAMESPACE_ERRORS건)"
    journalctl -xeu coldsync-install.service -n 30 2>/dev/null | grep -E 'NAMESPACE|Failed to set up mount namespacing' | tail -5
    ((FAIL_COUNT++))
fi
echo ""

# B. 해시 일치
echo "B. 해시 일치 확인:"
SRC_FILE="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
DST_FILE="/usr/local/bin/coldsync_hosp_from_usb.sh"

if [ -f "$SRC_FILE" ] && [ -f "$DST_FILE" ]; then
    SRC_HASH=$(sha256sum "$SRC_FILE" | awk '{print $1}')
    DST_HASH=$(sha256sum "$DST_FILE" | awk '{print $1}')
    
    echo "  워킹트리: $SRC_HASH"
    echo "  설치본:   $DST_HASH"
    
    if [ "$SRC_HASH" = "$DST_HASH" ]; then
        echo "✅ 해시 일치"
        ((PASS_COUNT++))
    else
        echo "❌ 해시 불일치"
        ((FAIL_COUNT++))
    fi
else
    echo "❌ 파일 없음"
    ((FAIL_COUNT++))
fi
echo ""

# C. Path 유닛 자동 반응 확인
echo "C. Path 유닛 자동 반응 확인:"
echo "  작업본 1바이트 터치 후 3초 대기..."
echo "# noop $(date)" >> "$SRC_FILE"
sleep 3

INSTALLED_LOG=$(journalctl -u coldsync-install.service -n 20 2>/dev/null | grep -E 'INSTALLED|SRC=|DST=' || echo "")
if [ -n "$INSTALLED_LOG" ]; then
    echo "✅ Path 트리거 후 INSTALLED 로그 확인됨"
    echo "$INSTALLED_LOG" | tail -3
    ((PASS_COUNT++))
else
    echo "❌ Path 트리거 후 INSTALLED 로그 없음"
    ((FAIL_COUNT++))
fi
echo ""

# 최종 결과
echo "=== 원인 검증 결과 ==="
echo "통과: $PASS_COUNT/3"
echo "실패: $FAIL_COUNT/3"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo "✅ 모든 검증 통과"
    echo ""
    echo "다음 단계:"
    echo "  bash scripts/evolution/final_check_l4.sh   # 최종 체크리스트"
    exit 0
else
    echo "❌ 일부 검증 실패"
    echo ""
    echo "📋 재시도:"
    echo "  bash scripts/evolution/fix_namespace_wsl_minimal.sh"
    exit 1
fi

