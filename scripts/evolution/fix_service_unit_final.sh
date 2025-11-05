#!/usr/bin/env bash
# L4.0 서비스 유닛 최종 정규화 (Unknown key name 경고 완전 제거)
# Usage: bash scripts/evolution/fix_service_unit_final.sh
# 목적: 서비스 유닛을 최소 스펙으로 완전 재작성하여 잔여 쉘 조각 제거

set -euo pipefail

echo "=== L4.0 서비스 유닛 최종 정규화 ==="
echo ""

UNIT="$HOME/.config/systemd/user/coldsync-install.service"
WRAP="$HOME/.local/bin/coldsync_install_debounced.sh"

# 백업
echo "1. 서비스 유닛 백업:"
if [ -f "$UNIT" ]; then
    cp -a "$UNIT" "$UNIT.bak.$(date +%s)"
    echo "✅ 백업 완료"
else
    echo "⚠️  서비스 유닛 없음: $UNIT"
fi
echo ""

# 잔여 쉘 조각 제거
echo "2. 잔여 쉘 조각 제거:"
if [ -f "$UNIT" ]; then
    sed -i '/set -Eeuo/d;/SRC=/d;/DST=/d' "$UNIT" 2>/dev/null || true
    echo "✅ 잔여 조각 제거 완료"
fi
echo ""

# 혹시 override 남아있는지 제거
echo "3. override 제거:"
rm -f ~/.config/systemd/user/coldsync-install.service.d/override.conf 2>/dev/null || true
rm -rf ~/.config/systemd/user/coldsync-install.service.d 2>/dev/null || true
echo "✅ override 제거 완료"
echo ""

# 완전 재작성 (최소 스펙)
echo "4. 서비스 유닛 완전 재작성:"
cat > "$UNIT" <<'EOF'
[Unit]
Description=Install coldsync script into ~/.local/bin on change
Wants=coldsync-install.path

[Service]
Type=oneshot
ExecStart=%h/.local/bin/coldsync_install_debounced.sh %h/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh %h/.local/bin/coldsync_hosp_from_usb.sh

[Install]
WantedBy=default.target
EOF
echo "✅ 재작성 완료"
echo ""

# 반영
echo "5. systemd 데몬 리로드 및 재시작:"
systemctl --user daemon-reload
systemctl --user reset-failed coldsync-install.service 2>/dev/null || true
systemctl --user restart coldsync-install.path
systemctl --user restart coldsync-install.service || true
echo "✅ 반영 완료"
echo ""

# 최근 5분 경고 확인 (과거 로그 무시)
echo "6. 최근 5분 경고 확인:"
WARNINGS=$(journalctl --user -u coldsync-install.service --since "5 min ago" --no-pager 2>&1 | grep -i 'Unknown key name' || echo "")
if [ -z "$WARNINGS" ]; then
    echo "✅ [OK] 최근 5분 경고 없음"
else
    echo "⚠️  경고 발견:"
    echo "$WARNINGS"
fi
echo ""

# 최근 로그 확인
echo "7. 최근 로그 확인:"
journalctl --user -u coldsync-install.service --since "2 min ago" --no-pager | head -10 || true
echo ""

echo "=== 서비스 유닛 최종 정규화 완료 ==="
echo ""
echo "다음 단계:"
echo "  # 최근 경고 확인 (과거 로그 무시)"
echo "  journalctl --user -u coldsync-install.service --since \"-2 min\" --no-pager | grep -i 'Unknown key name' || echo '[OK]'"

