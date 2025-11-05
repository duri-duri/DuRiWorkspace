#!/usr/bin/env bash
# L4.0 승급 실행 - 타임라인 기반 능동 모니터링 (수동 스팟체크 포함)
# Usage: bash scripts/evolution/run_l4_timeline.sh
# 목적: 실행 후 능동 모니터링 및 단계별 검증
# 참고: 스크립트가 자동 대기+검증하지만, 체크포인트마다 수동 스팟체크 필요

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

echo "=== L4.0 승급 실행 - 타임라인 기반 능동 모니터링 ==="
echo ""
echo "시작 시간: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "📋 중요: 스크립트가 자동 대기+검증하지만, 체크포인트마다 수동 스팟체크 필요!"
echo ""

START_TIME=$(date +%s)
T0=$START_TIME

# 0) T+0: 실행
echo "=== T+0: 실행 ==="
echo ""

bash scripts/evolution/run_l4_promotion.sh
EXEC_RESULT=$?

if [ $EXEC_RESULT -ne 0 ]; then
    echo ""
    echo "❌ 승급 실행 실패"
    echo "📋 복구:"
    echo "  bash scripts/bin/recover_coldsync.sh"
    exit 1
fi

echo ""
echo "✅ 실행 완료"
echo ""

# 1) T+2분: AC 즉시검증
echo "=== T+2분: AC 즉시검증 (대기 중...) ==="
sleep 120  # 2분 대기

T2=$(date +%s)
ELAPSED=$((T2 - T0))
echo "경과 시간: ${ELAPSED}초"
echo ""

echo "AC 검증 시작:"
bash scripts/evolution/check_l4_ac.sh
AC_RESULT=$?

if [ $AC_RESULT -ne 0 ]; then
    echo ""
    echo "❌ AC 검증 실패"
    echo "📋 복구:"
    echo "  bash scripts/bin/recover_coldsync.sh"
    echo "  bash scripts/bin/finalize_coldsync_autodeploy.sh"
    exit 1
fi

echo ""
echo "✅ AC 검증 통과"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 T+2분 체크포인트: 수동 스팟체크 필요"
echo ""
echo "다음 명령을 실행하여 확인하세요:"
echo ""
echo "  bash scripts/evolution/check_l4_timeline.sh T2"
echo "  systemctl --no-pager status coldsync-install.path coldsync-verify.timer | egrep 'active|enabled'"
echo "  journalctl -u coldsync-install.service -n 80 --no-pager | egrep 'INSTALLED|No change'"
echo ""
echo "GO/NO-GO 기준:"
echo "  ✅ path/timer = active & enabled"
echo "  ✅ 설치 로그에 INSTALLED/No change ≥1회"
echo "  ✅ SHA256 불일치 0건"
echo ""
echo "실패 시: bash scripts/evolution/l4_killswitch.sh recover"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 2) T+15분: 빠른 상태 + SLO 판정
echo "=== T+15분: 빠른 상태 + SLO 판정 (대기 중...) ==="
sleep 780  # 13분 추가 대기 (총 15분)

T15=$(date +%s)
ELAPSED=$((T15 - T0))
echo "경과 시간: ${ELAPSED}초"
echo ""

echo "빠른 상태 확인:"
bash scripts/evolution/quick_l4_check.sh
QUICK_RESULT=$?

echo ""
echo "설치 로그 확인:"
LOG_OUTPUT=$(sudo journalctl -u coldsync-install.service -n 80 --no-pager 2>/dev/null || echo "")
if echo "$LOG_OUTPUT" | grep -qE 'INSTALLED|No change'; then
    echo "✅ INSTALLED/No change 확인됨"
    LOG_PASS=0
else
    echo "❌ INSTALLED/No change 없음"
    LOG_PASS=1
fi

echo ""
echo "Gate 6/6 확인:"
bash scripts/evolution/verify_l4_gate.sh
GATE_RESULT=$?

echo ""
echo "=== T+15분 SLO 판정 ==="
echo ""

SLO_FAIL=0
FAILURES=()

# 판정 조건 1: path/timer active
if systemctl is-active coldsync-install.path >/dev/null 2>&1 && \
   systemctl is-active coldsync-verify.timer >/dev/null 2>&1; then
    echo "✅ PASS: path/timer = active"
else
    echo "❌ FAIL: path/timer ≠ active"
    ((SLO_FAIL++))
    FAILURES+=("path/timer inactive")
fi

# 판정 조건 2: 설치 로그
if [ $LOG_PASS -eq 0 ]; then
    echo "✅ PASS: 설치 로그 확인됨"
else
    echo "❌ FAIL: 설치 로그 없음"
    ((SLO_FAIL++))
    FAILURES+=("설치 로그 없음")
fi

# 판정 조건 3: Gate 6/6
if [ $GATE_RESULT -eq 0 ]; then
    echo "✅ PASS: Gate 6/6 통과"
else
    echo "❌ FAIL: Gate 일부 실패"
    ((SLO_FAIL++))
    FAILURES+=("Gate 실패")
fi

# 판정 조건 4: SHA256 일치
SRC="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
DST="/usr/local/bin/coldsync_hosp_from_usb.sh"
if [ -f "$SRC" ] && [ -f "$DST" ]; then
    SHA_SRC=$(sha256sum "$SRC" | awk '{print $1}')
    SHA_DST=$(sha256sum "$DST" | awk '{print $1}')
    if [ "$SHA_SRC" = "$SHA_DST" ]; then
        echo "✅ PASS: SHA256 일치"
    else
        echo "❌ FAIL: SHA256 불일치"
        ((SLO_FAIL++))
        FAILURES+=("SHA256 불일치")
    fi
else
    echo "❌ FAIL: 파일 없음"
    ((SLO_FAIL++))
    FAILURES+=("파일 없음")
fi

if [ $SLO_FAIL -eq 0 ]; then
    echo ""
    echo "✅ T+15분 SLO 판정: PASS"
    echo ""
else
    echo ""
    echo "❌ T+15분 SLO 판정: FAIL"
    echo "실패 항목:"
    for failure in "${FAILURES[@]}"; do
        echo "  - $failure"
    done
    echo ""
    echo "📋 복구:"
    echo "  bash scripts/bin/recover_coldsync.sh"
    echo "  bash scripts/bin/finalize_coldsync_autodeploy.sh"
    echo "  bash scripts/evolution/execute_l4_promotion.sh"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 T+15분 체크포인트: 수동 스팟체크 필요"
echo ""
echo "다음 명령을 실행하여 확인하세요:"
echo ""
echo "  bash scripts/evolution/check_l4_timeline.sh T15"
echo "  bash scripts/evolution/quick_l4_check.sh"
echo "  bash scripts/evolution/verify_l4_gate.sh"
echo ""
echo "GO/NO-GO 기준:"
echo "  ✅ path/timer = active & enabled"
echo "  ✅ 설치 로그에 INSTALLED/No change ≥1회"
echo "  ✅ SHA256 불일치 0건"
echo "  ✅ Gate 6/6 = PASS"
echo ""
echo "실패 시: bash scripts/evolution/l4_killswitch.sh recover"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 3) T+15~45분: 능동 모니터링 루프
echo "=== T+15~45분: 능동 모니터링 루프 (5분 주기, 6회) ==="
echo ""

MONITOR_DURATION=1800  # 30분
MONITOR_INTERVAL=300   # 5분
MONITOR_COUNT=$((MONITOR_DURATION / MONITOR_INTERVAL))

for i in $(seq 1 $MONITOR_COUNT); do
    T_CURRENT=$(date +%s)
    ELAPSED=$((T_CURRENT - T0))
    echo "--- 모니터링 #$i (경과: ${ELAPSED}초) ---"
    echo ""
    
    bash scripts/evolution/monitor_l4_dashboard.sh $MONITOR_INTERVAL || true
    
    # 개입 트리거 체크
    INTERVENTION=0
    
    # 트리거 1: halluc_rate > 0.10 또는 stability < 0.85
    if command -v jq >/dev/null 2>&1; then
        LATEST_METRICS=$(find var/evolution -name "metrics.json" 2>/dev/null | head -1)
        if [ -n "$LATEST_METRICS" ] && [ -f "$LATEST_METRICS" ]; then
            HALLUC=$(jq -r '.halluc_rate // 0' "$LATEST_METRICS" 2>/dev/null || echo "0")
            STABILITY=$(jq -r '.stability // 1' "$LATEST_METRICS" 2>/dev/null || echo "1")
            
            if (( $(echo "$HALLUC > 0.10" | bc -l 2>/dev/null || echo "0") )) || \
               (( $(echo "$STABILITY < 0.85" | bc -l 2>/dev/null || echo "0") )); then
                echo "⚠️  경고: halluc_rate=$HALLUC 또는 stability=$STABILITY"
                INTERVENTION=1
            fi
        fi
    fi
    
    # 트리거 2: ROLLBACK > 0
    ROLLBACK_COUNT=$(find var/evolution -name "gate.json" 2>/dev/null | xargs grep -h '"decision".*ROLLBACK' 2>/dev/null | wc -l || echo "0")
    if [ "$ROLLBACK_COUNT" -gt 0 ]; then
        echo "⚠️  경고: ROLLBACK=$ROLLBACK_COUNT"
        INTERVENTION=1
    fi
    
    # 트리거 3: SHA256 불일치
    if [ -f "$SRC" ] && [ -f "$DST" ]; then
        SHA_SRC=$(sha256sum "$SRC" | awk '{print $1}')
        SHA_DST=$(sha256sum "$DST" | awk '{print $1}')
        if [ "$SHA_SRC" != "$SHA_DST" ]; then
            echo "⚠️  경고: SHA256 불일치"
            INTERVENTION=1
        fi
    fi
    
    if [ $INTERVENTION -eq 1 ]; then
        echo ""
        echo "❌ 개입 트리거 발생"
        echo "📋 복구:"
        echo "  bash scripts/bin/recover_coldsync.sh"
        echo "  bash scripts/bin/snapshot_coldsync_security.sh"
        exit 1
    fi
    
    if [ $i -lt $MONITOR_COUNT ]; then
        echo ""
        echo "다음 모니터링까지 대기 중..."
        sleep $MONITOR_INTERVAL
    fi
done

echo ""
echo "✅ 능동 모니터링 루프 완료"
echo ""

# T+45분 체크포인트 안내
T45=$(date +%s)
ELAPSED=$((T45 - T0))
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 T+45분 체크포인트: 수동 스팟체크 필요"
echo ""
echo "다음 명령을 실행하여 확인하세요:"
echo ""
echo "  bash scripts/evolution/check_l4_timeline.sh T45"
echo "  bash scripts/evolution/monitor_l4_dashboard.sh 300"
echo ""
echo "개입 트리거 감지 시:"
echo "  bash scripts/evolution/l4_killswitch.sh recover"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 4) T+24h 안착 판정 안내
echo "=== T+24h 안착 판정 안내 ==="
echo ""
echo "24시간 후 다음 명령으로 안착 판정:"
echo "  bash scripts/evolution/check_l4_timeline.sh T24h"
echo "  bash scripts/evolution/check_l4_settlement.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 T+24h 체크포인트: 안착 판정"
echo ""
echo "안착 기준:"
echo "  ✅ PROMOTE ≥ 1, ROLLBACK = 0"
echo "  ✅ stability ≥ 0.90, halluc_rate ≤ 0.08 (연속 2 윈도우)"
echo "  ✅ 게이트 점수 G ≥ 0.70 (2회 연속)"
echo ""
echo "안착 후 선언:"
echo "  bash scripts/bin/snapshot_coldsync_security.sh"
echo "  bash scripts/bin/tag_coldsync_baseline.sh && git push --tags"
echo "  bash scripts/evolution/declare_l4.sh"
echo ""
echo "그레이존 (0.80 ≤ promotion_score_7d < 0.82):"
echo "  지터/가중치/격리 적용 후 12h 추가 드릴"
echo ""
echo "실패 시: bash scripts/evolution/l4_killswitch.sh rollback"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 최종 요약
END_TIME=$(date +%s)
TOTAL_ELAPSED=$((END_TIME - START_TIME))
echo "=== 실행 완료 ==="
echo "총 경과 시간: ${TOTAL_ELAPSED}초"
echo ""
echo "✅ 실행 단계 완료"
echo "✅ T+2분 AC 검증 통과"
echo "✅ T+15분 SLO 판정 통과"
echo "✅ T+15~45분 능동 모니터링 완료"
echo ""
echo "📋 다음 단계:"
echo "  T+45분: bash scripts/evolution/check_l4_timeline.sh T45"
echo "  T+24h: bash scripts/evolution/check_l4_settlement.sh"
echo ""
echo "🔴 Kill-Switch:"
echo "  상태: bash scripts/evolution/l4_killswitch.sh status"
echo "  일시 차단: bash scripts/evolution/l4_killswitch.sh recover"
echo "  완전 롤백: bash scripts/evolution/l4_killswitch.sh rollback"
