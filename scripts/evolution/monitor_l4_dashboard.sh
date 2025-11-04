#!/usr/bin/env bash
# L4.0 모니터링 대시보드 (5분 주기)
# Usage: bash scripts/evolution/monitor_l4_dashboard.sh [interval_seconds]
# Default: 300초 (5분)

set -euo pipefail

INTERVAL="${1:-300}"

echo "=== L4.0 모니터링 대시보드 (간격: ${INTERVAL}초) ==="
echo ""

while true; do
    clear
    echo "=== L4.0 모니터링 대시보드 ==="
    echo "시간: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "간격: ${INTERVAL}초"
    echo ""
    
    # 1. 서비스/타이머 상태
    echo "1. 서비스/타이머 상태"
    echo "---"
    systemctl is-active coldsync-install.path 2>/dev/null && echo "✅ install.path: active" || echo "❌ install.path: inactive"
    systemctl is-active coldsync-verify.timer 2>/dev/null && echo "✅ verify.timer: active" || echo "❌ verify.timer: inactive"
    echo ""
    
    # 2. SHA256 일치 확인
    echo "2. SHA256 일치 확인"
    echo "---"
    SRC="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
    DST="/usr/local/bin/coldsync_hosp_from_usb.sh"
    if [ -f "$SRC" ] && [ -f "$DST" ]; then
        SHA_SRC=$(sha256sum "$SRC" | awk '{print $1}')
        SHA_DST=$(sha256sum "$DST" | awk '{print $1}')
        if [ "$SHA_SRC" = "$SHA_DST" ]; then
            echo "✅ 일치: ${SHA_SRC:0:16}..."
        else
            echo "❌ 불일치"
        fi
    else
        echo "❌ 파일 없음"
    fi
    echo ""
    
    # 3. 최근 로그 (INSTALLED/No change)
    echo "3. 최근 로그 (최근 10분)"
    echo "---"
    sudo journalctl -u coldsync-install.service --since "10 minutes ago" --no-pager 2>/dev/null | grep -E 'INSTALLED|No change|ERR|FAIL' | tail -5 || echo "로그 없음"
    echo ""
    
    # 4. 게이트 결정 추적
    echo "4. 게이트 결정 추적 (최근 10건)"
    echo "---"
    find var/evolution -name "gate.json" 2>/dev/null | head -10 | while read f; do
        if [ -f "$f" ]; then
            DECISION=$(jq -r '.decision // "UNKNOWN"' "$f" 2>/dev/null || echo "UNKNOWN")
            TIMESTAMP=$(jq -r '.timestamp // "N/A"' "$f" 2>/dev/null || echo "N/A")
            echo "  ${TIMESTAMP:0:19}: $DECISION"
        fi
    done | tail -10 || echo "게이트 결과 없음"
    echo ""
    
    # 5. 핵심 KPI (메트릭이 있는 경우)
    echo "5. 핵심 KPI (가능한 경우)"
    echo "---"
    if command -v jq >/dev/null 2>&1; then
        find var/evolution -name "metrics.json" 2>/dev/null | head -10 | while read f; do
            if [ -f "$f" ]; then
                p_at3=$(jq -r '.p_at3 // 0' "$f" 2>/dev/null || echo "0")
                stability=$(jq -r '.stability // 0' "$f" 2>/dev/null || echo "0")
                halluc_rate=$(jq -r '.halluc_rate // 0' "$f" 2>/dev/null || echo "0")
                echo "  p@3: $p_at3, stability: $stability, halluc_rate: $halluc_rate"
            fi
        done | tail -5 || echo "메트릭 없음"
    else
        echo "jq 없음 (스킵)"
    fi
    echo ""
    
    # 6. 경고/에러 요약
    echo "6. 경고/에러 요약 (최근 30분)"
    echo "---"
    ERROR_COUNT=$(sudo journalctl -u coldsync-install.service --since "30 minutes ago" --no-pager 2>/dev/null | grep -ciE 'ERR|FAIL|ERROR' || echo "0")
    if [ "$ERROR_COUNT" -eq 0 ]; then
        echo "✅ 에러 없음"
    else
        echo "⚠️  에러: $ERROR_COUNT 건"
    fi
    echo ""
    
    echo "다음 업데이트: ${INTERVAL}초 후..."
    echo "(Ctrl+C로 종료)"
    
    sleep "$INTERVAL"
done

