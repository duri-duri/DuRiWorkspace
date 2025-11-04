#!/usr/bin/env bash
# L4.0 최소 감시 래퍼 (watch와 함께 사용)
# Usage: watch -n5 'bash scripts/evolution/spotcheck_l4.sh'

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

# 시간 표시
echo "=== L4.0 빠른 스팟체크 $(date '+%H:%M:%S') ==="
echo ""

# 1. 서비스/타이머 상태 (한 줄)
PATH_STATUS=$(systemctl is-active coldsync-install.path 2>/dev/null || echo "inactive")
TIMER_STATUS=$(systemctl is-active coldsync-verify.timer 2>/dev/null || echo "inactive")
if [ "$PATH_STATUS" = "active" ] && [ "$TIMER_STATUS" = "active" ]; then
    echo "✅ Services: path=active timer=active"
else
    echo "❌ Services: path=$PATH_STATUS timer=$TIMER_STATUS"
fi

# 2. SHA256 일치 (한 줄)
SRC="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
DST="/usr/local/bin/coldsync_hosp_from_usb.sh"
if [ -f "$SRC" ] && [ -f "$DST" ]; then
    SHA_SRC=$(sha256sum "$SRC" | awk '{print $1}')
    SHA_DST=$(sha256sum "$DST" | awk '{print $1}')
    if [ "$SHA_SRC" = "$SHA_DST" ]; then
        echo "✅ SHA256: 일치"
    else
        echo "❌ SHA256: 불일치"
    fi
else
    echo "❌ SHA256: 파일 없음"
fi

# 3. 게이트 결정 (최근 1건)
LATEST_DECISION=$(find var/evolution -name "gate.json" 2>/dev/null | head -1)
if [ -n "$LATEST_DECISION" ] && [ -f "$LATEST_DECISION" ]; then
    DECISION=$(jq -r '.decision // "UNKNOWN"' "$LATEST_DECISION" 2>/dev/null || echo "UNKNOWN")
    TIMESTAMP=$(jq -r '.timestamp // "N/A"' "$LATEST_DECISION" 2>/dev/null || echo "N/A")
    echo "📊 Gate: ${TIMESTAMP:11:8} → $DECISION"
else
    echo "📊 Gate: 데이터 없음"
fi

# 4. 개입 트리거 체크 (간략)
TRIGGER_COUNT=0
TRIGGER_MSG=""

# halluc_rate > 0.10 또는 stability < 0.85
if command -v jq >/dev/null 2>&1; then
    LATEST_METRICS=$(find var/evolution -name "metrics.json" 2>/dev/null | head -1)
    if [ -n "$LATEST_METRICS" ] && [ -f "$LATEST_METRICS" ]; then
        HALLUC=$(jq -r '.halluc_rate // 0' "$LATEST_METRICS" 2>/dev/null || echo "0")
        STABILITY=$(jq -r '.stability // 1' "$LATEST_METRICS" 2>/dev/null || echo "1")
        
        if (( $(echo "$HALLUC > 0.10" | bc -l 2>/dev/null || echo "0") )); then
            TRIGGER_MSG="${TRIGGER_MSG}halluc=$HALLUC "
            ((TRIGGER_COUNT++))
        fi
        
        if (( $(echo "$STABILITY < 0.85" | bc -l 2>/dev/null || echo "0") )); then
            TRIGGER_MSG="${TRIGGER_MSG}stability=$STABILITY "
            ((TRIGGER_COUNT++))
        fi
    fi
fi

# ROLLBACK > 0
ROLLBACK_COUNT=$(find var/evolution -name "gate.json" 2>/dev/null | xargs grep -h '"decision".*ROLLBACK' 2>/dev/null | wc -l || echo "0")
if [ "$ROLLBACK_COUNT" -gt 0 ]; then
    TRIGGER_MSG="${TRIGGER_MSG}ROLLBACK=$ROLLBACK_COUNT "
    ((TRIGGER_COUNT++))
fi

if [ $TRIGGER_COUNT -eq 0 ]; then
    echo "✅ Triggers: 없음"
else
    echo "⚠️  Triggers: $TRIGGER_COUNT건 ($TRIGGER_MSG)"
fi

echo ""
echo "--- 다음 업데이트: 5초 후 ---"
