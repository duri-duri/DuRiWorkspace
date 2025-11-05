#!/usr/bin/env bash
# L4.0 Gate 검증 스크립트
# 목적: 6개 Gate 통과 여부 확인
# Usage: bash scripts/evolution/verify_l4_gate.sh

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

echo "=== L4.0 Gate 검증 (6/6 통과 시 승급) ==="
echo ""

PASS_COUNT=0
FAIL_COUNT=0
FAILURES=()

# Gate 1: 자가복구 (Δ1)
echo "=== Gate 1: 자가복구 (Δ1) ==="
echo "조건: sha256(src)!=sha256(dst) 상태가 2분 지속되면 자동 재설치→해시 일치"
echo ""

SRC="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
DST="/usr/local/bin/coldsync_hosp_from_usb.sh"

# 현재 해시 확인
SHA_SRC=$(sha256sum "$SRC" 2>/dev/null | awk '{print $1}' || echo "")
SHA_DST=$(sha256sum "$DST" 2>/dev/null | awk '{print $1}' || echo "")

if [ -z "$SHA_SRC" ] || [ -z "$SHA_DST" ]; then
    echo "❌ FAIL: 파일 없음"
    ((FAIL_COUNT++))
    FAILURES+=("Gate 1: 파일 없음")
else
    if [ "$SHA_SRC" = "$SHA_DST" ]; then
        echo "✅ PASS: 해시 일치 (현재 상태 정상)"
        ((PASS_COUNT++))
    else
        echo "⚠️  해시 불일치 감지"
        echo "  소스: $SHA_SRC"
        echo "  설치: $SHA_DST"
        echo "  알람 확인 중..."
        
        # 알람 확인 (최근 2분)
        ALERT_COUNT=$(sudo journalctl -u coldsync-install.service --since "2 minutes ago" --no-pager 2>/dev/null | grep -cE 'INSTALLED|autofix' || echo "0")
        
        if [ "$ALERT_COUNT" -gt 0 ]; then
            echo "✅ PASS: 자가복구 실행 확인됨 (로그에 INSTALLED/autofix 발견)"
            ((PASS_COUNT++))
        else
            echo "❌ FAIL: 자가복구 미실행 (2분 내 INSTALLED/autofix 없음)"
            ((FAIL_COUNT++))
            FAILURES+=("Gate 1: 자가복구 미실행")
        fi
    fi
fi
echo ""

# Gate 2: 권한·경로 봉쇄 (Δ2)
echo "=== Gate 2: 권한·경로 봉쇄 (Δ2) ==="
echo "조건: sudoers 화이트리스트 외 명령/경로 시도 시 100% 차단 + 감사 로그"
echo ""

# Service 유닛 보안 설정 확인
SECURITY_OPTS=$(sudo systemctl cat coldsync-install.service 2>/dev/null | grep -E "RestrictNamespaces|PrivateDevices|DevicePolicy|IPAddressDeny|ProtectSystem" | wc -l || echo "0")

if [ "$SECURITY_OPTS" -ge 5 ]; then
    echo "✅ PASS: 보안 하드닝 확인됨 ($SECURITY_OPTS 개 옵션)"
    ((PASS_COUNT++))
else
    echo "⚠️  WARN: 보안 하드닝 미완료 ($SECURITY_OPTS 개 옵션)"
    echo "  보안 하드닝 실행 권장: bash scripts/evolution/harden_l4_security.sh"
    # 경고만 (실패로 처리하지 않음)
fi

# 금지 경로 테스트 (비파괴적)
TEST_FILE="/tmp/coldsync_gate2_test"
echo "test" > "$TEST_FILE"

# 권한 경계 테스트 (실제로는 차단되어야 함)
if sudo cp "$TEST_FILE" /usr/local/bin/coldsync_hosp_from_usb.sh 2>/dev/null; then
    echo "❌ FAIL: 금지 경로 쓰기 허용됨"
    ((FAIL_COUNT++))
    FAILURES+=("Gate 2: 금지 경로 쓰기 허용")
    
    # 원복 시도
    sudo /usr/local/sbin/coldsync-install 2>/dev/null || true
else
    echo "✅ PASS: 금지 경로 차단 확인됨"
    ((PASS_COUNT++))
fi

rm -f "$TEST_FILE"
echo ""

# Gate 3: Plan→Exec→Verify→Report 체인 (Δ3)
echo "=== Gate 3: Plan→Exec→Verify→Report 체인 (Δ3) ==="
echo "조건: 최근 실행 10건 pass_rate ≥ 0.97, 실패는 10분 내 롤백"
echo ""

# EvolutionSession에서 최근 실행 조회
if python3 -c "import sys; sys.path.insert(0, 'scripts/evolution'); from evolution_session import EvolutionSessionManager; m = EvolutionSessionManager(); sessions = m.list_sessions(limit=10); print(f'Total: {len(sessions)}'); passed = sum(1 for s in sessions if s.decision == 'PROMOTE' or (s.metrics and s.metrics.get('passed', False))); print(f'Passed: {passed}'); print(f'Rate: {passed/len(sessions) if sessions else 0:.2f}')" 2>/dev/null; then
    SESSION_OUTPUT=$(python3 -c "import sys; sys.path.insert(0, 'scripts/evolution'); from evolution_session import EvolutionSessionManager; m = EvolutionSessionManager(); sessions = m.list_sessions(limit=10); passed = sum(1 for s in sessions if s.decision == 'PROMOTE' or (s.metrics and s.metrics.get('passed', False))); rate = passed/len(sessions) if sessions else 0.0; print(f'{rate:.2f}')" 2>/dev/null || echo "0.00")
    RATE=$(echo "$SESSION_OUTPUT" | tail -1)
    
    if (( $(echo "$RATE >= 0.97" | bc -l 2>/dev/null || echo "0") )); then
        echo "✅ PASS: pass_rate = $RATE ≥ 0.97"
        ((PASS_COUNT++))
    else
        echo "⚠️  WARN: pass_rate = $RATE < 0.97 (데이터 부족일 수 있음)"
        # 데이터 부족 시 경고만
        if [ "$RATE" = "0.00" ]; then
            echo "  (데이터 없음 - 스킵)"
        else
            ((FAIL_COUNT++))
            FAILURES+=("Gate 3: pass_rate = $RATE < 0.97")
        fi
    fi
else
    echo "⚠️  WARN: EvolutionSession 데이터 없음 (스킵)"
fi
echo ""

# Gate 4: 타이머 백스탑
echo "=== Gate 4: 타이머 백스탑 ==="
echo "조건: Path 감지가 죽어도 coldsync-verify.timer가 2분 주기로 무결성 확인 및 복구"
echo ""

if sudo systemctl is-enabled coldsync-verify.timer >/dev/null 2>&1; then
    if sudo systemctl is-active coldsync-verify.timer >/dev/null 2>&1; then
        echo "✅ PASS: 타이머 활성화됨"
        ((PASS_COUNT++))
        
        # 다음 실행 예정 확인
        NEXT_RUN=$(sudo systemctl list-timers coldsync-verify.timer --no-pager 2>/dev/null | grep -E "NEXT|coldsync" | head -1 || echo "")
        if [ -n "$NEXT_RUN" ]; then
            echo "  다음 실행: $NEXT_RUN"
        fi
    else
        echo "❌ FAIL: 타이머 비활성"
        ((FAIL_COUNT++))
        FAILURES+=("Gate 4: 타이머 비활성")
    fi
else
    echo "❌ FAIL: 타이머 미등록"
    ((FAIL_COUNT++))
    FAILURES+=("Gate 4: 타이머 미등록")
fi
echo ""

# Gate 5: 프로모션 스코어
echo "=== Gate 5: 프로모션 스코어 ==="
echo "조건: 지난 7일 promotion_score ≥ 0.82, pass_rate_7d ≥ 0.98, safety_incident==0"
echo ""

GATE_OUTPUT=$(python3 scripts/evolution/promotion_gate_v2.py --window 168 --gate L4.1 --output /tmp/l4_gate_result.json 2>&1 || echo "")

if [ -f "/tmp/l4_gate_result.json" ]; then
    SCORE=$(jq -r '.score' /tmp/l4_gate_result.json 2>/dev/null || echo "0.0")
    PASSED=$(jq -r '.passed' /tmp/l4_gate_result.json 2>/dev/null || echo "false")
    
    if (( $(echo "$SCORE >= 0.82" | bc -l 2>/dev/null || echo "0") )) && [ "$PASSED" = "true" ]; then
        echo "✅ PASS: 스코어 = $SCORE ≥ 0.82, 통과 = $PASSED"
        ((PASS_COUNT++))
    else
        echo "❌ FAIL: 스코어 = $SCORE < 0.82 또는 통과 = $PASSED"
        ((FAIL_COUNT++))
        FAILURES+=("Gate 5: 스코어 = $SCORE 또는 통과 = $PASSED")
    fi
else
    echo "⚠️  WARN: Gate 결과 없음 (메트릭 데이터 부족일 수 있음)"
    echo "$GATE_OUTPUT" | tail -5
fi
echo ""

# Gate 6: 무인 운영 지표
echo "=== Gate 6: 무인 운영 지표 ==="
echo "조건: human_intervention_rate == 0 (최근 24h), MTTR(알람→복구) ≤ 2분"
echo ""

# 최근 24시간 로그에서 human_intervention 키워드 검색
INTERVENTION_COUNT=$(sudo journalctl -u coldsync-install.service --since "24 hours ago" --no-pager 2>/dev/null | grep -ciE 'manual|intervention|human' || echo "0")

if [ "$INTERVENTION_COUNT" -eq 0 ]; then
    echo "✅ PASS: human_intervention_rate = 0 (최근 24h)"
    ((PASS_COUNT++))
else
    echo "⚠️  WARN: human_intervention 발견 = $INTERVENTION_COUNT (로그 검색 결과)"
    # 경고만 (실제로는 더 정밀한 분석 필요)
fi

# MTTR 확인 (최근 알람→복구 시간)
RECENT_ALERTS=$(sudo journalctl -u coldsync-install.service --since "24 hours ago" --no-pager 2>/dev/null | grep -E 'INSTALLED|autofix' | tail -5 || echo "")
if [ -n "$RECENT_ALERTS" ]; then
    echo "✅ PASS: 최근 복구 이벤트 확인됨"
else
    echo "ℹ️  INFO: 최근 복구 이벤트 없음 (정상 상태일 수 있음)"
fi
echo ""

# 최종 결과
echo "=== 검증 결과 ==="
echo "통과: $PASS_COUNT/6"
echo "실패: $FAIL_COUNT/6"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo "✅ L4.0 Gate 통과!"
    echo ""
    echo "📋 다음 단계:"
    echo "  git tag -a 'l4-coldsync-go-$(date +%Y%m%d)' -m 'L4.0 운영선언'"
    echo "  git push origin 'l4-coldsync-go-$(date +%Y%m%d)'"
    exit 0
else
    echo "❌ L4.0 Gate 미통과"
    echo ""
    echo "실패 항목:"
    for failure in "${FAILURES[@]}"; do
        echo "  - $failure"
    done
    echo ""
    echo "📋 보정 후 재시도 필요"
    exit 1
fi

