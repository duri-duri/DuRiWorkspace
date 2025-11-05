#!/usr/bin/env bash
# L4.0 타임라인 체크포인트 검증
# Usage: bash scripts/evolution/check_l4_timeline.sh [checkpoint]
# checkpoint: T2, T15, T45, T24h

set -euo pipefail

CHECKPOINT="${1:-T15}"

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

echo "=== L4.0 타임라인 체크포인트 검증: $CHECKPOINT ==="
echo ""

case "$CHECKPOINT" in
    T2)
        echo "=== T+2분: AC 즉시검증 ==="
        echo ""
        bash scripts/evolution/check_l4_ac.sh
        ;;
    T15)
        echo "=== T+15분: 빠른 상태 + SLO 판정 ==="
        echo ""
        
        echo "1. 빠른 상태 확인:"
        bash scripts/evolution/quick_l4_check.sh
        echo ""
        
        echo "2. 설치 로그 확인:"
        LOG_OUTPUT=$(sudo journalctl -u coldsync-install.service -n 80 --no-pager 2>/dev/null || echo "")
        if echo "$LOG_OUTPUT" | grep -qE 'INSTALLED|No change'; then
            echo "✅ INSTALLED/No change 확인됨"
        else
            echo "❌ INSTALLED/No change 없음"
            exit 1
        fi
        echo ""
        
        echo "3. Gate 6/6 확인:"
        bash scripts/evolution/verify_l4_gate.sh
        echo ""
        
        echo "4. SLO 판정:"
        PASS_COUNT=0
        FAIL_COUNT=0
        
        # path/timer active
        if systemctl is-active coldsync-install.path >/dev/null 2>&1 && \
           systemctl is-active coldsync-verify.timer >/dev/null 2>&1; then
            echo "✅ path/timer = active"
            ((PASS_COUNT++))
        else
            echo "❌ path/timer ≠ active"
            ((FAIL_COUNT++))
        fi
        
        # SHA256 일치
        SRC="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
        DST="/usr/local/bin/coldsync_hosp_from_usb.sh"
        if [ -f "$SRC" ] && [ -f "$DST" ]; then
            SHA_SRC=$(sha256sum "$SRC" | awk '{print $1}')
            SHA_DST=$(sha256sum "$DST" | awk '{print $1}')
            if [ "$SHA_SRC" = "$SHA_DST" ]; then
                echo "✅ SHA256 일치"
                ((PASS_COUNT++))
            else
                echo "❌ SHA256 불일치"
                ((FAIL_COUNT++))
            fi
        else
            echo "❌ 파일 없음"
            ((FAIL_COUNT++))
        fi
        
        if [ $FAIL_COUNT -eq 0 ]; then
            echo ""
            echo "✅ T+15분 SLO 판정: PASS ($PASS_COUNT/2)"
            exit 0
        else
            echo ""
            echo "❌ T+15분 SLO 판정: FAIL ($FAIL_COUNT 실패)"
            exit 1
        fi
        ;;
    T45)
        echo "=== T+45분: 능동 모니터링 요약 ==="
        echo ""
        
        echo "1. 서비스/타이머 상태:"
        systemctl is-active coldsync-install.path 2>/dev/null && echo "✅ install.path: active" || echo "❌ install.path: inactive"
        systemctl is-active coldsync-verify.timer 2>/dev/null && echo "✅ verify.timer: active" || echo "❌ verify.timer: inactive"
        echo ""
        
        echo "2. 최근 로그 (30분):"
        sudo journalctl -u coldsync-install.service --since "30 minutes ago" --no-pager 2>/dev/null | grep -E 'INSTALLED|No change|ERR|FAIL' | tail -10 || echo "로그 없음"
        echo ""
        
        echo "3. 게이트 결정 추적:"
        find var/evolution -name "gate.json" 2>/dev/null | head -10 | while read f; do
            if [ -f "$f" ]; then
                DECISION=$(jq -r '.decision // "UNKNOWN"' "$f" 2>/dev/null || echo "UNKNOWN")
                TIMESTAMP=$(jq -r '.timestamp // "N/A"' "$f" 2>/dev/null || echo "N/A")
                echo "  ${TIMESTAMP:0:19}: $DECISION"
            fi
        done | tail -10 || echo "게이트 결과 없음"
        echo ""
        
        echo "4. 개입 트리거 체크:"
        TRIGGER_COUNT=0
        
        # halluc_rate > 0.10 또는 stability < 0.85
        if command -v jq >/dev/null 2>&1; then
            LATEST_METRICS=$(find var/evolution -name "metrics.json" 2>/dev/null | head -1)
            if [ -n "$LATEST_METRICS" ] && [ -f "$LATEST_METRICS" ]; then
                HALLUC=$(jq -r '.halluc_rate // 0' "$LATEST_METRICS" 2>/dev/null || echo "0")
                STABILITY=$(jq -r '.stability // 1' "$LATEST_METRICS" 2>/dev/null || echo "1")
                
                if (( $(echo "$HALLUC > 0.10" | bc -l 2>/dev/null || echo "0") )); then
                    echo "⚠️  경고: halluc_rate=$HALLUC > 0.10"
                    ((TRIGGER_COUNT++))
                fi
                
                if (( $(echo "$STABILITY < 0.85" | bc -l 2>/dev/null || echo "0") )); then
                    echo "⚠️  경고: stability=$STABILITY < 0.85"
                    ((TRIGGER_COUNT++))
                fi
            fi
        fi
        
        # ROLLBACK > 0
        ROLLBACK_COUNT=$(find var/evolution -name "gate.json" 2>/dev/null | xargs grep -h '"decision".*ROLLBACK' 2>/dev/null | wc -l || echo "0")
        if [ "$ROLLBACK_COUNT" -gt 0 ]; then
            echo "⚠️  경고: ROLLBACK=$ROLLBACK_COUNT"
            ((TRIGGER_COUNT++))
        fi
        
        if [ $TRIGGER_COUNT -eq 0 ]; then
            echo "✅ 개입 트리거 없음"
        else
            echo "❌ 개입 트리거 발생 ($TRIGGER_COUNT건)"
            exit 1
        fi
        ;;
    T24h)
        echo "=== T+24h: 안착 판정 ==="
        echo ""
        bash scripts/evolution/check_l4_settlement.sh
        ;;
    *)
        echo "알 수 없는 체크포인트: $CHECKPOINT"
        echo "사용법: $0 [T2|T15|T45|T24h]"
        exit 1
        ;;
esac

