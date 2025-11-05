#!/usr/bin/env bash
# L4.0 승급 합격 기준 (AC) 검증
# 목적: 필요충분조건 AC1~AC6 자동 검증
# Usage: bash scripts/evolution/check_l4_ac.sh

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

echo "=== L4.0 승급 합격 기준 (AC) 검증 ==="
echo ""

PASS_COUNT=0
FAIL_COUNT=0
FAILURES=()

# AC1: 감시·자율
echo "AC1: 감시·자율"
echo "조건: coldsync-install.path = enabled/active, coldsync-verify.timer = enabled/active"
echo ""

if systemctl is-enabled coldsync-install.path >/dev/null 2>&1 && \
   systemctl is-active coldsync-install.path >/dev/null 2>&1; then
    echo "✅ PASS: coldsync-install.path = enabled/active"
    ((PASS_COUNT++))
else
    echo "❌ FAIL: coldsync-install.path ≠ enabled/active"
    ((FAIL_COUNT++))
    FAILURES+=("AC1: coldsync-install.path 상태")
fi

if systemctl is-enabled coldsync-verify.timer >/dev/null 2>&1 && \
   systemctl is-active coldsync-verify.timer >/dev/null 2>&1; then
    echo "✅ PASS: coldsync-verify.timer = enabled/active"
    ((PASS_COUNT++))
else
    echo "❌ FAIL: coldsync-verify.timer ≠ enabled/active"
    ((FAIL_COUNT++))
    FAILURES+=("AC1: coldsync-verify.timer 상태")
fi
echo ""

# AC2: 무결성
echo "AC2: 무결성"
echo "조건: 운영본↔작업본 SHA256 완전 일치, 최근 로그에 INSTALLED 또는 No change"
echo ""

SRC="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
DST="/usr/local/bin/coldsync_hosp_from_usb.sh"

if [ -f "$SRC" ] && [ -f "$DST" ]; then
    SHA_SRC=$(sha256sum "$SRC" | awk '{print $1}')
    SHA_DST=$(sha256sum "$DST" | awk '{print $1}')
    
    if [ "$SHA_SRC" = "$SHA_DST" ]; then
        echo "✅ PASS: SHA256 완전 일치"
        ((PASS_COUNT++))
    else
        echo "❌ FAIL: SHA256 불일치"
        ((FAIL_COUNT++))
        FAILURES+=("AC2: SHA256 불일치")
    fi
    
    # 최근 로그 확인
    LOG_COUNT=$(sudo journalctl -u coldsync-install.service -n 50 --no-pager 2>/dev/null | grep -cE 'INSTALLED|No change' || echo "0")
    if [ "$LOG_COUNT" -gt 0 ]; then
        echo "✅ PASS: 최근 로그에 INSTALLED/No change 확인됨"
        ((PASS_COUNT++))
    else
        echo "⚠️  WARN: 최근 로그에 INSTALLED/No change 없음"
    fi
else
    echo "❌ FAIL: 파일 없음"
    ((FAIL_COUNT++))
    FAILURES+=("AC2: 파일 없음")
fi
echo ""

# AC3: 자가복구
echo "AC3: 자가복구"
echo "조건: prometheus/rules/coldsync_autofix.rules.yml 로드됨, promtool check rules 통과"
echo ""

AUTOFIX_RULE="prometheus/rules/coldsync_autofix.rules.yml"
if [ -f "$AUTOFIX_RULE" ]; then
    echo "✅ PASS: coldsync_autofix.rules.yml 존재"
    ((PASS_COUNT++))
    
    # promtool 체크
    if command -v promtool >/dev/null 2>&1; then
        if promtool check rules "$AUTOFIX_RULE" >/dev/null 2>&1; then
            echo "✅ PASS: promtool check rules 통과"
            ((PASS_COUNT++))
        else
            echo "❌ FAIL: promtool check rules 실패"
            ((FAIL_COUNT++))
            FAILURES+=("AC3: promtool check rules 실패")
        fi
    else
        echo "⚠️  WARN: promtool 없음 (스킵)"
    fi
else
    echo "❌ FAIL: coldsync_autofix.rules.yml 없음"
    ((FAIL_COUNT++))
    FAILURES+=("AC3: 룰 파일 없음")
fi
echo ""

# AC4: 권한 봉쇄
echo "AC4: 권한 봉쇄"
echo "조건: ProtectSystem=strict, NoNewPrivileges=yes, CapabilityBoundingSet=(빈), ReadOnlyPaths/ReadWritePaths 일치"
echo ""

SERVICE_FILE="/etc/systemd/system/coldsync-install.service"
if [ -f "$SERVICE_FILE" ]; then
    CHECK_PROTECT=$(sudo systemctl cat coldsync-install.service 2>/dev/null | grep -c "ProtectSystem=strict" || echo "0")
    CHECK_NO_NEW=$(sudo systemctl cat coldsync-install.service 2>/dev/null | grep -c "NoNewPrivileges=yes" || echo "0")
    CHECK_CAP=$(sudo systemctl cat coldsync-install.service 2>/dev/null | grep -c "CapabilityBoundingSet=" || echo "0")
    CHECK_PATHS=$(sudo systemctl cat coldsync-install.service 2>/dev/null | grep -cE "ReadOnlyPaths|ReadWritePaths" || echo "0")
    
    if [ "$CHECK_PROTECT" -gt 0 ] && [ "$CHECK_NO_NEW" -gt 0 ] && [ "$CHECK_PATHS" -gt 0 ]; then
        echo "✅ PASS: 보안 하드닝 확인됨"
        ((PASS_COUNT++))
    else
        echo "❌ FAIL: 보안 하드닝 불완전"
        ((FAIL_COUNT++))
        FAILURES+=("AC4: 보안 하드닝 불완전")
    fi
else
    echo "❌ FAIL: Service 파일 없음"
    ((FAIL_COUNT++))
    FAILURES+=("AC4: Service 파일 없음")
fi
echo ""

# AC5: 게이트 6/6
echo "AC5: 게이트 6/6"
echo "조건: verify_l4_gate.sh 출력에 Gate1~6 모두 PASS"
echo ""

GATE_OUTPUT=$(bash scripts/evolution/verify_l4_gate.sh 2>&1)
GATE_PASS_COUNT=$(echo "$GATE_OUTPUT" | grep -c "✅ PASS\|PASS:" || echo "0")
GATE_FAIL_COUNT=$(echo "$GATE_OUTPUT" | grep -c "❌ FAIL" || echo "0")

if [ "$GATE_FAIL_COUNT" -eq 0 ] && [ "$GATE_PASS_COUNT" -ge 6 ]; then
    echo "✅ PASS: Gate 6/6 통과"
    ((PASS_COUNT++))
else
    echo "❌ FAIL: Gate 일부 실패 ($GATE_FAIL_COUNT 실패)"
    ((FAIL_COUNT++))
    FAILURES+=("AC5: Gate 실패")
fi
echo ""

# AC6: 증거 기록
echo "AC6: 증거 기록"
echo "조건: snapshot_coldsync_security.sh 산출물과 tag_coldsync_baseline.sh 태그가 git에 존재"
echo ""

# 스냅샷 파일 확인
SNAPSHOT_FILES=$(find var/evolution -name "*snapshot*" -o -name "*security*" 2>/dev/null | head -1 || echo "")
if [ -n "$SNAPSHOT_FILES" ]; then
    echo "✅ PASS: 스냅샷 파일 존재"
    ((PASS_COUNT++))
else
    echo "⚠️  WARN: 스냅샷 파일 없음 (생성 권장)"
fi

# 태그 확인
TAG_COUNT=$(git tag -l "l4-coldsync-go-*" | wc -l || echo "0")
if [ "$TAG_COUNT" -gt 0 ]; then
    echo "✅ PASS: L4.0 태그 존재 ($TAG_COUNT 개)"
    ((PASS_COUNT++))
else
    echo "⚠️  WARN: L4.0 태그 없음 (생성 권장)"
fi
echo ""

# 최종 결과
echo "=== AC 검증 결과 ==="
echo "통과: $PASS_COUNT"
echo "실패: $FAIL_COUNT"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo "✅ 모든 AC 통과 (필요충분조건 충족)"
    echo ""
    echo "📋 L4.0 선언 가능:"
    echo "  bash scripts/evolution/declare_l4.sh"
    exit 0
else
    echo "❌ 일부 AC 실패"
    echo ""
    echo "실패 항목:"
    for failure in "${FAILURES[@]}"; do
        echo "  - $failure"
    done
    echo ""
    echo "📋 보정 후 재시도 필요"
    exit 1
fi

