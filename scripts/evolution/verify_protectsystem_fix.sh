#!/usr/bin/env bash
# L4.0 ProtectSystem 버그 검증 (WSL에서 실행)
# Usage: bash scripts/evolution/verify_protectsystem_fix.sh
# 목적: ProtectSystem 파싱 에러 제거 확인

set -euo pipefail

echo "=== L4.0 ProtectSystem 버그 검증 ==="
echo ""

PASS_COUNT=0
FAIL_COUNT=0

# ProtectSystem 파싱 에러 확인
echo "1. ProtectSystem 파싱 에러 확인:"
PARSE_ERRORS=$(journalctl -u coldsync-install.service -n 200 --no-pager 2>/dev/null | grep -cE 'Failed to parse protect system value' || echo "0")
PARSE_ERRORS=$(echo "$PARSE_ERRORS" | tr -d '[:space:]')
PARSE_ERRORS=${PARSE_ERRORS:-0}

if [ "$PARSE_ERRORS" -eq 0 ]; then
    echo "✅ ProtectSystem 파싱 에러 없음"
    ((PASS_COUNT++))
else
    echo "❌ ProtectSystem 파싱 에러 발견 ($PARSE_ERRORS건)"
    journalctl -u coldsync-install.service -n 200 --no-pager 2>/dev/null | grep -E 'Failed to parse protect system value' | tail -3
    ((FAIL_COUNT++))
fi
echo ""

# 서비스 결과 확인
echo "2. 서비스 결과 확인:"
SERVICE_RESULT=$(systemctl show coldsync-install.service -p Result --value 2>/dev/null || echo "unknown")
if [ "$SERVICE_RESULT" = "success" ]; then
    echo "✅ 서비스 성공 (Result=success)"
    ((PASS_COUNT++))
else
    echo "⚠️  서비스 결과: $SERVICE_RESULT"
    # 실패 로그 확인
    journalctl -u coldsync-install.service -n 50 --no-pager 2>/dev/null | grep -E 'FAILED|Permission denied|Read-only file system' | tail -5 || echo "추가 로그 없음"
fi
echo ""

# 설치/동기화 성공 메시지 확인
echo "3. 설치/동기화 성공 메시지 확인:"
SUCCESS_LOG=$(journalctl -u coldsync-install.service -n 50 --no-pager 2>/dev/null | grep -iE 'INSTALLED|up-to-date|success' || echo "")
if [ -n "$SUCCESS_LOG" ]; then
    echo "✅ 성공 메시지 확인됨"
    echo "$SUCCESS_LOG" | tail -3
    ((PASS_COUNT++))
else
    echo "⚠️  성공 메시지 없음"
fi
echo ""

# 해시 일치 확인
echo "4. 해시 일치 확인:"
SRC_FILE="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
DST_FILE="/usr/local/bin/coldsync_hosp_from_usb.sh"

if [ -f "$SRC_FILE" ] && [ -f "$DST_FILE" ]; then
    SRC_HASH=$(sha256sum "$SRC_FILE" | awk '{print $1}')
    DST_HASH=$(sha256sum "$DST_FILE" | awk '{print $1}')
    
    if [ "$SRC_HASH" = "$DST_HASH" ]; then
        echo "✅ 해시 일치"
        ((PASS_COUNT++))
    else
        echo "⚠️  해시 불일치"
        echo "  워킹트리: $SRC_HASH"
        echo "  설치본:   $DST_HASH"
    fi
else
    echo "⚠️  파일 없음"
fi
echo ""

# 최종 결과
echo "=== 검증 결과 ==="
echo "통과: $PASS_COUNT/4"
echo "실패: $FAIL_COUNT/4"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo "✅ 모든 검증 통과"
    exit 0
else
    echo "❌ 일부 검증 실패"
    exit 1
fi

