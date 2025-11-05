#!/usr/bin/env bash
# L4.0 Kill-Switch 통합
# Usage: bash scripts/evolution/l4_killswitch.sh [action]
# action: recover (일시 차단), rollback (완전 롤백), status (상태 확인)

set -euo pipefail

ACTION="${1:-status}"

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

echo "=== L4.0 Kill-Switch: $ACTION ==="
echo ""

case "$ACTION" in
    recover)
        echo "일시 차단 시작..."
        bash scripts/bin/recover_coldsync.sh
        echo ""
        echo "✅ 일시 차단 완료"
        echo ""
        echo "📋 다음 단계:"
        echo "  1. 원인 확인: bash scripts/bin/snapshot_coldsync_security.sh"
        echo "  2. 복구: bash scripts/bin/finalize_coldsync_autodeploy.sh"
        echo "  3. 재시도: bash scripts/evolution/execute_l4_promotion.sh"
        ;;
    rollback)
        echo "완전 롤백 시작..."
        echo "⚠️  경고: 모든 변경사항이 롤백됩니다."
        read -p "계속하시겠습니까? (yes/no): " CONFIRM
        if [ "$CONFIRM" != "yes" ]; then
            echo "롤백 취소됨"
            exit 0
        fi
        bash scripts/bin/rollback_coldsync.sh
        echo ""
        echo "✅ 완전 롤백 완료"
        ;;
    status)
        echo "현재 상태 확인:"
        echo ""
        
        echo "1. 서비스/타이머 상태:"
        systemctl is-active coldsync-install.path 2>/dev/null && echo "✅ install.path: active" || echo "❌ install.path: inactive"
        systemctl is-active coldsync-verify.timer 2>/dev/null && echo "✅ verify.timer: active" || echo "❌ verify.timer: inactive"
        echo ""
        
        echo "2. SHA256 일치 확인:"
        SRC="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
        DST="/usr/local/bin/coldsync_hosp_from_usb.sh"
        if [ -f "$SRC" ] && [ -f "$DST" ]; then
            SHA_SRC=$(sha256sum "$SRC" | awk '{print $1}')
            SHA_DST=$(sha256sum "$DST" | awk '{print $1}')
            if [ "$SHA_SRC" = "$SHA_DST" ]; then
                echo "✅ SHA256 일치"
            else
                echo "❌ SHA256 불일치"
            fi
        else
            echo "❌ 파일 없음"
        fi
        echo ""
        
        echo "3. 최근 로그 (10분):"
        sudo journalctl -u coldsync-install.service --since "10 minutes ago" --no-pager 2>/dev/null | grep -E 'INSTALLED|No change|ERR|FAIL' | tail -5 || echo "로그 없음"
        echo ""
        
        echo "4. 게이트 결정 (최근 5건):"
        find var/evolution -name "gate.json" 2>/dev/null | head -5 | while read f; do
            if [ -f "$f" ]; then
                DECISION=$(jq -r '.decision // "UNKNOWN"' "$f" 2>/dev/null || echo "UNKNOWN")
                TIMESTAMP=$(jq -r '.timestamp // "N/A"' "$f" 2>/dev/null || echo "N/A")
                echo "  ${TIMESTAMP:0:19}: $DECISION"
            fi
        done || echo "게이트 결과 없음"
        echo ""
        
        echo "📋 사용 가능한 액션:"
        echo "  bash scripts/evolution/l4_killswitch.sh recover   # 일시 차단"
        echo "  bash scripts/evolution/l4_killswitch.sh rollback   # 완전 롤백"
        ;;
    *)
        echo "알 수 없는 액션: $ACTION"
        echo "사용법: $0 [recover|rollback|status]"
        exit 1
        ;;
esac

