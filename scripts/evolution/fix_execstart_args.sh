#!/usr/bin/env bash
# L4.0 ExecStart 인자 부여 + 즉시 동기화
# Usage: bash scripts/evolution/fix_execstart_args.sh
# 목적: ExecStart에 SRC/DST 명시 인자 부여 및 즉시 동기화

set -euo pipefail

echo "=== L4.0 ExecStart 인자 부여 + 즉시 동기화 ==="
echo ""

UNIT="$HOME/.config/systemd/user/coldsync-install.service"

# 백업
echo "1. 서비스 유닛 백업:"
if [ -f "$UNIT" ]; then
    cp -a "$UNIT" "$UNIT.bak.$(date +%s)"
    echo "✅ 백업 완료"
else
    echo "⚠️  서비스 유닛 없음: $UNIT"
fi
echo ""

# ExecStart에 인자 추가
echo "2. ExecStart에 SRC/DST 인자 부여:"
cat > "$UNIT" <<'UNIT'
[Unit]
Description=Install coldsync script into ~/.local/bin on change
Wants=coldsync-install.path

[Service]
Type=oneshot
ExecStart=%h/.local/bin/coldsync_install_debounced.sh %h/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh %h/.local/bin/coldsync_hosp_from_usb.sh

[Install]
WantedBy=default.target
UNIT
echo "✅ ExecStart 인자 부여 완료"
echo ""

# 데몬 리로드 및 재시작
echo "3. systemd 데몬 리로드 및 재시작:"
systemctl --user daemon-reload
systemctl --user restart coldsync-install.path
echo "✅ 재시작 완료"
echo ""

# 강제 1회 실행 + 검증
echo "4. 강제 동기화 실행:"
systemctl --user start coldsync-install.service
sleep 2
echo "✅ 실행 완료"
echo ""

# 해시 확인
echo "5. 해시 확인:"
SRC_HASH=$(sha256sum "$HOME/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh" 2>/dev/null | awk '{print $1}' || echo "")
DST_HASH=$(sha256sum "$HOME/.local/bin/coldsync_hosp_from_usb.sh" 2>/dev/null | awk '{print $1}' || echo "")

if [ "$SRC_HASH" = "$DST_HASH" ] && [ -n "$SRC_HASH" ]; then
    echo "✅ 해시 일치: ${SRC_HASH}"
else
    echo "⚠️  해시 불일치:"
    echo "   SRC: ${SRC_HASH}"
    echo "   DST: ${DST_HASH}"
    echo ""
    echo "   12초 대기 후 재시도..."
    sleep 12
    systemctl --user start coldsync-install.service
    sleep 2
    SRC_HASH2=$(sha256sum "$HOME/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh" 2>/dev/null | awk '{print $1}' || echo "")
    DST_HASH2=$(sha256sum "$HOME/.local/bin/coldsync_hosp_from_usb.sh" 2>/dev/null | awk '{print $1}' || echo "")
    if [ "$SRC_HASH2" = "$DST_HASH2" ] && [ -n "$SRC_HASH2" ]; then
        echo "✅ 재시도 후 해시 일치: ${SRC_HASH2}"
    else
        echo "⚠️  재시도 후에도 해시 불일치"
    fi
fi
echo ""

# ExecStart 확인
echo "6. ExecStart 확인:"
EXEC_START=$(systemctl --user cat coldsync-install.service 2>/dev/null | grep -E '^ExecStart=' | head -1 || echo "")
if [ -n "$EXEC_START" ]; then
    echo "✅ ExecStart 설정:"
    echo "$EXEC_START"
    if echo "$EXEC_START" | grep -q 'coldsync_hosp_from_usb.sh'; then
        echo "✅ 인자 포함 확인"
    else
        echo "⚠️  인자 미포함 가능성"
    fi
else
    echo "❌ ExecStart 설정 확인 실패"
fi
echo ""

echo "=== ExecStart 인자 부여 완료 ==="
echo ""
echo "다음 단계:"
echo "  ${HOME}/.local/bin/cold_hash"

