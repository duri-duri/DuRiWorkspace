#!/usr/bin/env bash
# coldsync 자동 배포 시스템 - 회귀 테스트 (최종)
# Usage: bash scripts/bin/test_coldsync_autodeploy.sh

set -euo pipefail

SRC="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
DST="/usr/local/bin/coldsync_hosp_from_usb.sh"

echo "=== coldsync 자동 배포 회귀 테스트 (최종) ==="
echo ""

# 1. Path 유닛 상태 확인
echo "1. Path 유닛 상태 확인:"
if sudo systemctl is-enabled coldsync-install.path >/dev/null 2>&1; then
    echo "✅ enabled"
else
    echo "❌ not enabled"
    exit 1
fi

if sudo systemctl is-active coldsync-install.path >/dev/null 2>&1; then
    echo "✅ active"
else
    echo "❌ not active"
    exit 1
fi
echo ""

# 2. 검증 타이머 상태 확인
echo "2. 검증 타이머 상태 확인:"
if sudo systemctl is-enabled coldsync-verify.timer >/dev/null 2>&1; then
    echo "✅ enabled"
else
    echo "⚠️  not enabled (선택 사항)"
fi

if sudo systemctl is-active coldsync-verify.timer >/dev/null 2>&1; then
    echo "✅ active"
else
    echo "⚠️  not active (선택 사항)"
fi
echo ""

# 3. 파일 존재 확인
echo "3. 파일 존재 확인:"
if [ -f "$SRC" ]; then
    echo "✅ 소스 파일 존재: $SRC"
else
    echo "❌ 소스 파일 없음: $SRC"
    exit 1
fi

if [ -f "$DST" ]; then
    echo "✅ 설치본 파일 존재: $DST"
else
    echo "❌ 설치본 파일 없음: $DST"
    exit 1
fi
echo ""

# 4. 스모크 테스트 (변경 후 자동 배포)
echo "4. 스모크 테스트 (변경 후 자동 배포):"
echo "작업본에 테스트 변경 추가..."
echo "# Smoke test $(date +%F.%T)" >> "$SRC"
echo "변경 완료. Path 감지 대기 중 (2초)..."
sleep 2
echo ""

echo "최근 로그 (20줄, INSTALLED/installed sha/status=0/success 필터):"
sudo journalctl -u coldsync-install.service -n 20 --no-pager | grep -iE 'INSTALLED|installed sha|status=0|success' || echo "로그 필터링 결과 없음"
echo ""

echo "전체 최근 로그 (8줄):"
sudo journalctl -u coldsync-install.service -n 8 --no-pager || true
echo ""

# 5. 파일 동기화 확인
echo "5. 파일 동기화 확인:"
SHA_SRC=$(sha256sum "$SRC" | awk '{print $1}')
SHA_DST=$(sha256sum "$DST" | awk '{print $1}')

if [ "$SHA_SRC" = "$SHA_DST" ]; then
    echo "✅ PASS: 파일 동기화 OK (해시 일치)"
    echo "  해시: $SHA_SRC"
else
    echo "❌ FAIL: 파일 동기화 실패 (해시 불일치)"
    echo "  소스: $SHA_SRC"
    echo "  대상: $SHA_DST"
    exit 1
fi
echo ""

# 6. 무결성 확인
echo "6. 무결성 확인:"
if grep -qE '^#!/usr/bin/env bash' "$DST"; then
    echo "✅ PASS: 헤더 서명 검증 OK"
else
    echo "❌ FAIL: 헤더 서명 검증 실패"
    exit 1
fi

if bash -n "$DST" 2>/dev/null; then
    echo "✅ PASS: bash 문법 검증 OK"
else
    echo "❌ FAIL: bash 문법 검증 실패"
    exit 1
fi
echo ""

# 7. 보안 점수 확인
echo "7. 보안 점수 확인:"
sudo systemd-analyze security coldsync-install.service 2>/dev/null | head -20 || echo "보안 분석 스킵"
echo ""

echo "=== 회귀 테스트 완료 ==="
echo ""
echo "✅ 모든 테스트 통과"
