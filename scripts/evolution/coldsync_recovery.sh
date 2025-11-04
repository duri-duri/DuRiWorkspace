#!/usr/bin/env bash
# L4.0 coldsync 실패 복구 원샷
# Usage: bash scripts/evolution/coldsync_recovery.sh
# 목적: 유닛 재정규화 + 데몬 리로드 + 최근 경고 검증

set -euo pipefail

echo "=== L4.0 coldsync 실패 복구 원샷 ==="
echo ""

SVC="$HOME/.config/systemd/user/coldsync-install.service"

# 백업
echo "1. 서비스 유닛 백업:"
if [ -f "$SVC" ]; then
    cp -a "$SVC" "$SVC.bak.$(date +%s)"
    echo "✅ 백업 완료"
else
    echo "⚠️  서비스 유닛 없음: $SVC"
fi
echo ""

# 서비스 유닛 재정규화
echo "2. 서비스 유닛 재정규화:"
cat > "$SVC" <<'UNIT'
[Unit]
Description=Install coldsync script into ~/.local/bin on change
Wants=coldsync-install.path

[Service]
Type=oneshot
ExecStart=%h/.local/bin/coldsync_install_debounced.sh

[Install]
WantedBy=default.target
UNIT
echo "✅ 재정규화 완료"
echo ""

# 데몬 리로드 및 재시작
echo "3. systemd 데몬 리로드 및 재시작:"
systemctl --user daemon-reload
systemctl --user restart coldsync-install.path
systemctl --user restart coldsync-install.service || true
echo "✅ 재시작 완료"
echo ""

# 최근 3분 경고 검증
echo "4. 최근 3분 경고 검증:"
WARNINGS=$(journalctl --user -u coldsync-install.service --since "3 min ago" --no-pager 2>&1 | grep -i 'Unknown key name' || echo "")
if [ -z "$WARNINGS" ]; then
    echo "✅ [OK] 정규화 완료"
else
    echo "⚠️  [WARN] 잔여 경고 발견:"
    echo "$WARNINGS"
fi
echo ""

# 최근 로그 확인
echo "5. 최근 로그 확인:"
journalctl --user -u coldsync-install.service --since "2 min ago" --no-pager | head -10 || true
echo ""

echo "=== 복구 완료 ==="
echo ""
echo "다음 단계:"
echo "  cold-status"
echo "  cold-hash"

