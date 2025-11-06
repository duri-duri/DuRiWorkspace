#!/usr/bin/env bash
# coldsync 자동 배포 시스템 - 최종 검증 (완전 자동)
# 목적: GO/NO-GO 결정을 위한 완전 자동 검증
# Usage: bash scripts/bin/verify_coldsync_final.sh

set -euo pipefail

echo "=== coldsync 자동 배포 시스템 - 최종 검증 (GO/NO-GO) ==="
echo ""

PASS=0
FAIL=0

# 1. 유닛 상태 확인
echo "1. 유닛 상태 확인"
echo ""

# Path 유닛
if sudo systemctl is-enabled coldsync-install.path >/dev/null 2>&1; then
    echo "✅ coldsync-install.path: enabled"
    ((PASS++))
else
    echo "❌ coldsync-install.path: not enabled"
    ((FAIL++))
fi

if sudo systemctl is-active coldsync-install.path >/dev/null 2>&1; then
    echo "✅ coldsync-install.path: active"
    ((PASS++))
else
    echo "❌ coldsync-install.path: not active"
    ((FAIL++))
fi

# 검증 타이머
if sudo systemctl is-enabled coldsync-verify.timer >/dev/null 2>&1; then
    echo "✅ coldsync-verify.timer: enabled"
    ((PASS++))
else
    echo "⚠️  coldsync-verify.timer: not enabled (선택 사항)"
fi

if sudo systemctl is-active coldsync-verify.timer >/dev/null 2>&1; then
    echo "✅ coldsync-verify.timer: active"
    ((PASS++))
else
    echo "⚠️  coldsync-verify.timer: not active (선택 사항)"
fi

echo ""

# 2. 저장 트리거 스모크 테스트
echo "2. 저장 트리거 스모크 테스트"
SRC="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
DST="/usr/local/bin/coldsync_hosp_from_usb.sh"

if [ ! -f "$SRC" ]; then
    echo "❌ 소스 파일 없음: $SRC"
    ((FAIL++))
    exit 1
fi

echo "작업본에 테스트 변경 추가..."
echo "# final smoke $(date +%F.%T)" >> "$SRC"
echo "변경 완료. Path 감지 대기 중 (2초)..."
sleep 2
echo ""

echo "최근 로그 (15줄):"
LOG_OUTPUT=$(sudo journalctl -u coldsync-install.service -n 15 --no-pager 2>/dev/null || echo "")
echo "$LOG_OUTPUT"

if echo "$LOG_OUTPUT" | grep -qE 'INSTALLED|installed sha='; then
    echo "✅ 로그에 INSTALLED 확인됨"
    ((PASS++))
else
    echo "❌ 로그에 INSTALLED 없음"
    ((FAIL++))
fi

echo ""

# 3. 해시 동등성 확인 (원자 설치 확인)
echo "3. 해시 동등성 확인 (원자 설치 확인)"
if [ ! -f "$DST" ]; then
    echo "❌ 설치본 파일 없음: $DST"
    ((FAIL++))
    exit 1
fi

SHA_SRC=$(sha256sum "$SRC" | awk '{print $1}')
SHA_DST=$(sha256sum "$DST" | awk '{print $1}')

echo "소스: $SHA_SRC"
echo "설치: $SHA_DST"

if [ "$SHA_SRC" = "$SHA_DST" ]; then
    echo "✅ SHA256 완전 일치"
    ((PASS++))
else
    echo "❌ SHA256 불일치"
    ((FAIL++))
fi

echo ""

# 4. 파일 무결성 확인
echo "4. 파일 무결성 확인"
if grep -qE '^#!/usr/bin/env bash' "$DST"; then
    echo "✅ 헤더 서명 검증 OK"
    ((PASS++))
else
    echo "❌ 헤더 서명 검증 실패"
    ((FAIL++))
fi

if bash -n "$DST" 2>/dev/null; then
    echo "✅ bash 문법 검증 OK"
    ((PASS++))
else
    echo "❌ bash 문법 검증 실패"
    ((FAIL++))
fi

echo ""

# 최종 결과
echo "=== 검증 결과 ==="
echo "통과: $PASS"
echo "실패: $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "✅ GO: 모든 검증 통과"
    echo ""
    echo "📋 합격 기준 (AC):"
    echo "  ✅ coldsync-install.path = enabled/active"
    echo "  ✅ coldsync-verify.timer = enabled/active (선택)"
    echo "  ✅ 로그에 INSTALLED 확인됨"
    echo "  ✅ SHA256 완전 일치"
    echo "  ✅ 파일 무결성 검증 통과"
    exit 0
else
    echo "❌ NO-GO: 검증 실패 ($FAIL 건)"
    echo ""
    echo "📋 실패 항목 확인 후 복구:"
    echo "  bash scripts/bin/recover_coldsync.sh"
    exit 1
fi

