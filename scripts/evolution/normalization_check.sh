#!/usr/bin/env bash
# L4.0 정상화 검증 시퀀스 (WSL에서 실행)
# Usage: bash scripts/evolution/normalization_check.sh
# 목적: 전체 검증 시퀀스

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

echo "=== L4.0 정상화 검증 시퀀스 ==="
echo ""

# 1) 강제 1회 실행
echo "1. 강제 1회 실행 (에러 없어야 함):"
sudo systemctl start coldsync-install.service
echo "✅ 서비스 시작 완료"
echo ""

echo "로그 확인:"
journalctl -u coldsync-install.service -n 50 --no-pager | tail -20 || echo "로그 없음"
echo ""

# 2) Path 트리거 동작 확인
echo "2. Path 트리거 동작 확인:"
SRC_FILE="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
echo "# touch $(date)" >> "$SRC_FILE"
echo "✅ 소스 파일 수정 완료"
echo "Path 이벤트 소화 대기 (2초)..."
sleep 2

echo "로그에서 설치 성공 문자열 검사:"
SUCCESS_LOG=$(journalctl -u coldsync-install.service -n 30 --no-pager | grep -iE 'INSTALLED|up-to-date|DST_SHA|SRC_SHA|success' || echo "")
if [ -n "$SUCCESS_LOG" ]; then
    echo "✅ 성공 로그 확인됨"
    echo "$SUCCESS_LOG" | tail -5
else
    echo "⚠️  성공 로그 없음"
fi
echo ""

# 3) 최종 해시 일치 확인
echo "3. 최종 해시 일치 확인:"
SRC_FILE="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
DST_FILE="/usr/local/bin/coldsync_hosp_from_usb.sh"

echo "== working =="
sha256sum "$SRC_FILE" 2>/dev/null || echo "워킹트리 파일 없음"

echo "== installed =="
sha256sum "$DST_FILE" 2>/dev/null || echo "설치본 파일 없음"

if [ -f "$SRC_FILE" ] && [ -f "$DST_FILE" ]; then
    SRC_HASH=$(sha256sum "$SRC_FILE" | awk '{print $1}')
    DST_HASH=$(sha256sum "$DST_FILE" | awk '{print $1}')
    
    if [ "$SRC_HASH" = "$DST_HASH" ]; then
        echo "✅ 해시 일치"
    else
        echo "❌ 해시 불일치"
    fi
fi
echo ""

# 4) 검증 스크립트 재실행
echo "4. 검증 스크립트 재실행:"
bash scripts/evolution/verify_namespace_fix.sh
echo ""

echo "=== 정상화 검증 시퀀스 완료 ==="
echo ""
echo "통과 기준:"
echo "  ✅ status=0/SUCCESS"
echo "  ✅ 최근 로그에 설치/동기화 성공 메시지"
echo "  ✅ SRC == DST 해시 일치"
echo "  ✅ verify_namespace_fix.sh에서 더 이상 integer expression expected 미발생"

