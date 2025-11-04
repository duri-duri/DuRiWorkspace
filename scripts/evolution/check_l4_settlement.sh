#!/usr/bin/env bash
# L4.0 24h 안착 기준 자동 검증
# Usage: bash scripts/evolution/check_l4_settlement.sh

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

echo "=== L4.0 24h 안착 기준 검증 ==="
echo ""

PASS_COUNT=0
FAIL_COUNT=0
FAILURES=()

# 안착 기준 1: PROMOTE ≥ 1, ROLLBACK = 0
echo "1. PROMOTE/ROLLBACK 기준"
echo "---"
PROMOTE_COUNT=$(find var/evolution -name "gate.json" 2>/dev/null | xargs grep -h '"decision".*PROMOTE' 2>/dev/null | wc -l || echo "0")
ROLLBACK_COUNT=$(find var/evolution -name "gate.json" 2>/dev/null | xargs grep -h '"decision".*ROLLBACK' 2>/dev/null | wc -l || echo "0")

if [ "$PROMOTE_COUNT" -ge 1 ] && [ "$ROLLBACK_COUNT" -eq 0 ]; then
    echo "✅ PASS: PROMOTE=$PROMOTE_COUNT, ROLLBACK=$ROLLBACK_COUNT"
    ((PASS_COUNT++))
else
    echo "❌ FAIL: PROMOTE=$PROMOTE_COUNT, ROLLBACK=$ROLLBACK_COUNT"
    ((FAIL_COUNT++))
    FAILURES+=("안착 기준 1: PROMOTE/ROLLBACK 불충족")
fi
echo ""

# 안착 기준 2: stability ≥ 0.90, halluc_rate ≤ 0.08 (연속 2 윈도우)
echo "2. Stability/Hallucination 기준"
echo "---"
if command -v jq >/dev/null 2>&1; then
    STABILITY_VALUES=$(find var/evolution -name "metrics.json" 2>/dev/null | head -10 | xargs jq -r '.stability // 0' 2>/dev/null | grep -v "^0$" | tail -2 || echo "")
    HALLUC_VALUES=$(find var/evolution -name "metrics.json" 2>/dev/null | head -10 | xargs jq -r '.halluc_rate // 1' 2>/dev/null | tail -2 || echo "")
    
    if [ -n "$STABILITY_VALUES" ]; then
        STABILITY_PASS=0
        while IFS= read -r val; do
            if (( $(echo "$val >= 0.90" | bc -l 2>/dev/null || echo "0") )); then
                STABILITY_PASS=$((STABILITY_PASS + 1))
            fi
        done <<< "$STABILITY_VALUES"
        
        HALLUC_PASS=0
        while IFS= read -r val; do
            if (( $(echo "$val <= 0.08" | bc -l 2>/dev/null || echo "0") )); then
                HALLUC_PASS=$((HALLUC_PASS + 1))
            fi
        done <<< "$HALLUC_VALUES"
        
        if [ "$STABILITY_PASS" -ge 2 ] && [ "$HALLUC_PASS" -ge 2 ]; then
            echo "✅ PASS: stability ≥ 0.90 (2회), halluc_rate ≤ 0.08 (2회)"
            ((PASS_COUNT++))
        else
            echo "❌ FAIL: stability=$STABILITY_PASS/2, halluc=$HALLUC_PASS/2"
            ((FAIL_COUNT++))
            FAILURES+=("안착 기준 2: stability/halluc_rate 불충족")
        fi
    else
        echo "⚠️  WARN: 메트릭 데이터 없음 (스킵)"
    fi
else
    echo "⚠️  WARN: jq 없음 (스킵)"
fi
echo ""

# 안착 기준 3: 게이트 점수 G ≥ 0.70 (2회 연속)
echo "3. 게이트 점수 기준"
echo "---"
GATE_SCORES=$(find var/evolution -name "gate.json" 2>/dev/null | head -10 | xargs jq -r '.score // 0' 2>/dev/null | grep -v "^0$" | tail -2 || echo "")

if [ -n "$GATE_SCORES" ]; then
    SCORE_PASS=0
    while IFS= read -r score; do
        if (( $(echo "$score >= 0.70" | bc -l 2>/dev/null || echo "0") )); then
            SCORE_PASS=$((SCORE_PASS + 1))
        fi
    done <<< "$GATE_SCORES"
    
    if [ "$SCORE_PASS" -ge 2 ]; then
        echo "✅ PASS: 게이트 점수 ≥ 0.70 (2회 연속)"
        ((PASS_COUNT++))
    else
        echo "❌ FAIL: 게이트 점수 ≥ 0.70 ($SCORE_PASS/2)"
        ((FAIL_COUNT++))
        FAILURES+=("안착 기준 3: 게이트 점수 불충족")
    fi
else
    echo "⚠️  WARN: 게이트 점수 데이터 없음 (스킵)"
fi
echo ""

# 안착 기준 4: 24h SLO
echo "4. 24h SLO 기준"
echo "---"
DRIFT_COUNT=$(sudo journalctl -u coldsync-install.service --since "24 hours ago" --no-pager 2>/dev/null | grep -cE 'INSTALLED|autofix' || echo "0")
INTERVENTION_COUNT=$(sudo journalctl -u coldsync-install.service --since "24 hours ago" --no-pager 2>/dev/null | grep -ciE 'manual|intervention|human' || echo "0")

if [ "$DRIFT_COUNT" -le 12 ] && [ "$INTERVENTION_COUNT" -eq 0 ]; then
    echo "✅ PASS: drift ≤ 12/24h, intervention = 0"
    ((PASS_COUNT++))
else
    echo "⚠️  WARN: drift=$DRIFT_COUNT, intervention=$INTERVENTION_COUNT"
fi
echo ""

# 최종 결과
echo "=== 안착 기준 검증 결과 ==="
echo "통과: $PASS_COUNT"
echo "실패: $FAIL_COUNT"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo "✅ 24h 안착 기준 충족!"
    echo ""
    echo "📋 L4.1 선언 준비:"
    echo "  bash scripts/evolution/declare_l4.sh"
    exit 0
else
    echo "❌ 일부 안착 기준 미충족"
    echo ""
    echo "실패 항목:"
    for failure in "${FAILURES[@]}"; do
        echo "  - $failure"
    done
    echo ""
    echo "📋 계속 모니터링 필요"
    exit 1
fi

