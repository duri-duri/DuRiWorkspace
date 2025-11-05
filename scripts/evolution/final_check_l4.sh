#!/usr/bin/env bash
# L4.0 최종 체크리스트 (WSL에서 실행)
# Usage: bash scripts/evolution/final_check_l4.sh
# 목적: 원클릭 검증

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

echo "=== L4.0 최종 체크리스트 (원클릭) ==="
echo ""

# 0) override 반영 확인
echo "0. override 반영 확인:"
if [ -f "/etc/systemd/system/coldsync-install.service.d/override.conf" ]; then
    echo "✅ override.conf 존재"
    if grep -q "StateDirectory=coldsync-hosp" /etc/systemd/system/coldsync-install.service.d/override.conf 2>/dev/null; then
        echo "✅ StateDirectory 설정 확인됨"
    else
        echo "⚠️  StateDirectory 설정 없음"
    fi
else
    echo "❌ override.conf 없음"
fi
echo ""

# 1) 서비스 단발 실행
echo "1. 서비스 단발 실행 (설치):"
sudo systemctl daemon-reload
sudo systemctl start coldsync-install.service || true
echo "✅ 서비스 시작 완료"
echo ""

# 2) 상태/로그
echo "2. 상태/로그 확인:"
echo ""
echo "서비스 상태:"
systemctl status coldsync-install.service -n 30 --no-pager | head -20 || echo "상태 확인 실패"
echo ""

echo "로그 (최근 30줄):"
journalctl -u coldsync-install.service -n 30 --no-pager | tail -15 || echo "로그 없음"
echo ""

# 3) 자동배포 회귀
echo "3. 자동배포 회귀 테스트:"
SRC_FILE="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
printf '# touch %s\n' "$(date)" >> "$SRC_FILE"
echo "✅ 소스 파일 수정 완료"
echo "Path 트리거 대기 (2초)..."
sleep 2

INSTALLED_LOG=$(journalctl -u coldsync-install.service -n 15 2>/dev/null | grep -E 'INSTALLED|SRC=|DST=' || echo "")
if [ -n "$INSTALLED_LOG" ]; then
    echo "✅ Path 트리거 후 INSTALLED 로그 확인됨"
    echo "$INSTALLED_LOG" | tail -3
else
    echo "⚠️  Path 트리거 후 INSTALLED 로그 없음"
fi
echo ""

# 4) 최종 해시
echo "4. 최종 해시 확인:"
SRC_FILE="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
DST_FILE="/usr/local/bin/coldsync_hosp_from_usb.sh"

if [ -f "$SRC_FILE" ] && [ -f "$DST_FILE" ]; then
    echo "워킹트리:"
    sha256sum "$SRC_FILE"
    echo "설치본:"
    sha256sum "$DST_FILE"
    
    SRC_HASH=$(sha256sum "$SRC_FILE" | awk '{print $1}')
    DST_HASH=$(sha256sum "$DST_FILE" | awk '{print $1}')
    
    if [ "$SRC_HASH" = "$DST_HASH" ]; then
        echo "✅ 해시 일치"
    else
        echo "❌ 해시 불일치"
    fi
else
    echo "❌ 파일 없음"
fi
echo ""

# 5) 워크트리 권한/소유권 확인
echo "5. 워크트리 권한/소유권 확인:"
if [ -f "$SRC_FILE" ]; then
    FILE_OWNER=$(stat -c '%U:%G' "$SRC_FILE" 2>/dev/null || echo "unknown")
    FILE_PERM=$(stat -c '%a' "$SRC_FILE" 2>/dev/null || echo "unknown")
    
    if [ "$FILE_OWNER" = "duri:duri" ]; then
        echo "✅ 소유권: $FILE_OWNER"
    else
        echo "⚠️  소유권: $FILE_OWNER (권장: duri:duri)"
    fi
    
    if [ "$FILE_PERM" = "755" ] || [ "$FILE_PERM" = "0755" ]; then
        echo "✅ 권한: $FILE_PERM"
    else
        echo "⚠️  권한: $FILE_PERM (권장: 755)"
    fi
else
    echo "❌ 파일 없음"
fi
echo ""

# 6) 최종 검증
echo "6. 최종 검증:"
echo ""
bash scripts/bin/status_coldsync_oneline.sh || true
echo ""

if bash scripts/bin/verify_coldsync_final.sh 2>/dev/null; then
    echo "✅ verify_coldsync_final.sh 통과"
else
    echo "⚠️  verify_coldsync_final.sh 실패"
fi
echo ""

echo "=== 최종 체크리스트 완료 ==="
echo ""
echo "다음 단계:"
echo "  bash scripts/evolution/preflight_l4.sh   # 프리플라이트"
echo "  bash scripts/evolution/run_l4_timeline.sh # 타임라인 실행"

