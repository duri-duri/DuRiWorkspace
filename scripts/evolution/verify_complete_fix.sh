#!/usr/bin/env bash
# L4.0 최종 검증 스크립트
# Usage: bash scripts/evolution/verify_complete_fix.sh
# 목적: 모든 버그 수정 확인 및 Path 트리거 테스트

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

echo "=== L4.0 최종 검증 ==="
echo ""

PASS_COUNT=0
FAIL_COUNT=0

# 1. override.conf 확인
echo "1. override.conf 확인:"
if sudo grep -q "ProtectHome=no" /etc/systemd/system/coldsync-install.service.d/override.conf 2>/dev/null; then
    echo "✅ ProtectHome=no"
    ((PASS_COUNT++))
else
    echo "❌ ProtectHome 설정 확인 실패"
    ((FAIL_COUNT++))
fi

if sudo grep -q "^ExecStartPre=$" /etc/systemd/system/coldsync-install.service.d/override.conf 2>/dev/null; then
    echo "✅ ExecStartPre 제거됨"
    ((PASS_COUNT++))
else
    echo "❌ ExecStartPre 제거 확인 실패"
    ((FAIL_COUNT++))
fi
echo ""

# 2. 설치기 exit 0 확인
echo "2. 설치기 exit 0 확인:"
if sudo /usr/local/sbin/coldsync-install >/dev/null 2>&1; then
    echo "✅ 설치기 exit 0 확인"
    ((PASS_COUNT++))
else
    echo "❌ 설치기 exit 0 실패"
    ((FAIL_COUNT++))
fi
echo ""

# 3. 서비스 상태 확인
echo "3. 서비스 상태 확인:"
SERVICE_RESULT=$(systemctl show coldsync-install.service -p Result --value 2>/dev/null || echo "unknown")
if [ "$SERVICE_RESULT" = "success" ]; then
    echo "✅ 서비스 결과: success"
    ((PASS_COUNT++))
else
    echo "⚠️  서비스 결과: $SERVICE_RESULT"
    # 최근 실행이 성공했는지 확인
    if systemctl status coldsync-install.service --no-pager 2>/dev/null | grep -q "status=0/SUCCESS"; then
        echo "✅ 최근 실행 성공 확인"
        ((PASS_COUNT++))
    else
        echo "❌ 최근 실행 실패"
        ((FAIL_COUNT++))
    fi
fi
echo ""

# 4. Path 유닛 상태 확인
echo "4. Path 유닛 상태 확인:"
if systemctl is-active --quiet coldsync-install.path 2>/dev/null; then
    echo "✅ Path 유닛 활성화됨"
    ((PASS_COUNT++))
else
    echo "❌ Path 유닛 비활성화"
    ((FAIL_COUNT++))
fi
echo ""

# 5. Path 트리거 테스트
echo "5. Path 트리거 테스트:"
echo "  소스 파일에 더미 변경 추가..."
SRC_FILE="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
echo "# Path trigger test $(date)" >> "$SRC_FILE"
sleep 3

TRIGGER_LOG=$(journalctl -u coldsync-install.service -n 5 --no-pager 2>/dev/null | grep -E "INSTALLED|up-to-date" || echo "")
if [ -n "$TRIGGER_LOG" ]; then
    echo "✅ Path 트리거 후 로그 확인됨"
    echo "$TRIGGER_LOG" | tail -1
    ((PASS_COUNT++))
else
    echo "❌ Path 트리거 후 로그 없음"
    ((FAIL_COUNT++))
fi
echo ""

# 6. 해시 동기화 확인
echo "6. 해시 동기화 확인:"
SRC_HASH=$(sha256sum "$SRC_FILE" | awk '{print $1}')
DST_FILE="/usr/local/bin/coldsync_hosp_from_usb.sh"
DST_HASH=$(sha256sum "$DST_FILE" 2>/dev/null | awk '{print $1}' || echo "")

if [ "$SRC_HASH" = "$DST_HASH" ] && [ -n "$DST_HASH" ]; then
    echo "✅ 해시 동기화 확인 (SRC=DST=$SRC_HASH)"
    ((PASS_COUNT++))
else
    echo "❌ 해시 불일치"
    echo "  SRC: $SRC_HASH"
    echo "  DST: $DST_HASH"
    ((FAIL_COUNT++))
fi
echo ""

# 최종 결과
echo "=== 최종 검증 결과 ==="
echo "통과: $PASS_COUNT"
echo "실패: $FAIL_COUNT"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo "✅ 모든 검증 통과!"
    echo ""
    echo "다음 단계:"
    echo "  bash scripts/evolution/preflight_l4.sh   # 프리플라이트"
    echo "  bash scripts/evolution/run_l4_timeline.sh # 타임라인 실행"
    exit 0
else
    echo "❌ 일부 검증 실패"
    echo ""
    echo "재시도:"
    echo "  bash scripts/evolution/fix_all_bugs.sh"
    exit 1
fi

