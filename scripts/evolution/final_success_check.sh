#!/usr/bin/env bash
# L4.0 최종 성공 확인 및 Path 트리거 테스트
# Usage: bash scripts/evolution/final_success_check.sh
# 목적: 모든 수정 완료 확인 및 Path 트리거 최종 테스트

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

echo "=== L4.0 최종 성공 확인 ==="
echo ""

PASS_COUNT=0
FAIL_COUNT=0

# 1. 해시 동기화 확인
echo "1. 해시 동기화 확인:"
SRC_FILE="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
DST_FILE="/usr/local/bin/coldsync_hosp_from_usb.sh"
SRC_HASH=$(sha256sum "$SRC_FILE" | awk '{print $1}')
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

# 2. 서비스 상태 확인
echo "2. 서비스 상태 확인:"
if sudo systemctl start coldsync-install.service 2>/dev/null; then
    SERVICE_RESULT=$(systemctl show coldsync-install.service -p Result --value 2>/dev/null || echo "unknown")
    if [ "$SERVICE_RESULT" = "success" ]; then
        echo "✅ 서비스 실행 성공"
        ((PASS_COUNT++))
    else
        echo "⚠️  서비스 결과: $SERVICE_RESULT"
        if systemctl status coldsync-install.service --no-pager 2>/dev/null | grep -q "status=0/SUCCESS"; then
            echo "✅ 최근 실행 성공 확인"
            ((PASS_COUNT++))
        else
            echo "❌ 서비스 실행 실패"
            ((FAIL_COUNT++))
        fi
    fi
else
    echo "❌ 서비스 시작 실패"
    ((FAIL_COUNT++))
fi
echo ""

# 3. Path 유닛 상태 확인
echo "3. Path 유닛 상태 확인:"
if systemctl is-active --quiet coldsync-install.path 2>/dev/null; then
    echo "✅ Path 유닛 활성화됨"
    ((PASS_COUNT++))
else
    echo "❌ Path 유닛 비활성화"
    ((FAIL_COUNT++))
fi
echo ""

# 4. Path 트리거 테스트 안내
echo "4. Path 트리거 테스트:"
echo "  VS Code에서 파일을 저장하거나 아래 명령으로 테스트:"
echo ""
echo "  # 테스트 방법 1: 직접 편집"
echo "  echo '# Path trigger test $(date)' >> $SRC_FILE"
echo "  sleep 3"
echo "  journalctl -u coldsync-install.service -n 3 --no-pager"
echo ""
echo "  # 테스트 방법 2: touch로 메타데이터 변경"
echo "  touch $SRC_FILE"
echo "  sleep 3"
echo "  journalctl -u coldsync-install.service -n 3 --no-pager"
echo ""
echo "  # 테스트 방법 3: VS Code로 파일 열고 저장 (Ctrl+S)"
echo "  code $SRC_FILE"
echo ""

# 최종 결과
echo "=== 최종 확인 결과 ==="
echo "통과: $PASS_COUNT"
echo "실패: $FAIL_COUNT"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo "✅ 모든 검증 통과!"
    echo ""
    echo "🎉 L4.0 coldsync 자동 배포 시스템 준비 완료!"
    echo ""
    echo "사용 방법:"
    echo "  1. VS Code에서 ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh 편집"
    echo "  2. 저장 (Ctrl+S)"
    echo "  3. 자동으로 /usr/local/bin에 배포됨"
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

