#!/usr/bin/env bash
# 즉시 관측·판독 원라인
# Usage: bash scripts/evolution/quick_l4_check.sh

set -euo pipefail

echo "=== L4.0 즉시 관측·판독 ==="
echo ""

echo "1. 서비스/타이머 상태:"
systemctl --no-pager --type=timer 2>/dev/null | grep -E 'coldsync|l4-(evolution|queue)' || echo "타이머 정보 없음"
echo ""

echo "2. 활성 상태 확인:"
systemctl is-active coldsync-verify.timer && echo "✅ verify.timer: active" || echo "❌ verify.timer: inactive"
systemctl is-active coldsync-install.path && echo "✅ install.path: active" || echo "❌ install.path: inactive"
echo ""

echo "3. 최신 로그 스캔 (설치/무변경):"
sudo journalctl -u coldsync-install.service -n 30 --no-pager 2>/dev/null | grep -E 'INSTALLED|No change' || echo "로그 없음"
echo ""

echo "4. 게이트 결과 샘플:"
find var/evolution -name "gate.json" -o -name "*.log" 2>/dev/null | head -5 | while read f; do
    if grep -qE 'PROMOTE|ROLLBACK|RETRY' "$f" 2>/dev/null; then
        echo "  $f:"
        grep -hE 'PROMOTE|ROLLBACK|RETRY' "$f" 2>/dev/null | tail -1
    fi
done || echo "게이트 결과 없음"
echo ""

echo "5. SHA256 일치 확인:"
SRC="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
DST="/usr/local/bin/coldsync_hosp_from_usb.sh"
if [ -f "$SRC" ] && [ -f "$DST" ]; then
    SHA_SRC=$(sha256sum "$SRC" | awk '{print $1}')
    SHA_DST=$(sha256sum "$DST" | awk '{print $1}')
    if [ "$SHA_SRC" = "$SHA_DST" ]; then
        echo "✅ 일치: $SHA_SRC"
    else
        echo "❌ 불일치"
        echo "  소스: $SHA_SRC"
        echo "  설치: $SHA_DST"
    fi
else
    echo "❌ 파일 없음"
fi
echo ""

echo "=== 관측 완료 ==="

