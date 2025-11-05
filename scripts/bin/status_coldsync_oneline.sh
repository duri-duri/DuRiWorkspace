#!/usr/bin/env bash
# coldsync 자동 배포 시스템 - 원라인 상태 확인
# Usage: bash scripts/bin/status_coldsync_autodeploy.sh
# 또는: bash -lc 'SRC=~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh DST=/usr/local/bin/coldsync_hosp_from_usb.sh; echo "[UNIT]"; systemctl is-enabled coldsync-install.path; systemctl is-active coldsync-install.path || true; echo "[HASH]"; sha256sum "$SRC" "$DST" || true; echo "[LOG]"; sudo journalctl -u coldsync-install.service -n 10 --no-pager || true'

set -euo pipefail

SRC="$HOME/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
DST="/usr/local/bin/coldsync_hosp_from_usb.sh"

echo "[UNIT]"
systemctl is-enabled coldsync-install.path 2>/dev/null || echo "path-enabled: not-enabled"
systemctl is-active coldsync-install.path 2>/dev/null || echo "path-active: not-active"

echo "[HASH]"
if [ -f "$SRC" ] && [ -f "$DST" ]; then
    sha256sum "$SRC" "$DST" || true
else
    echo "파일 없음: SRC=$([ -f "$SRC" ] && echo "OK" || echo "MISS"), DST=$([ -f "$DST" ] && echo "OK" || echo "MISS")"
fi

echo "[LOG]"
sudo journalctl -u coldsync-install.service -n 10 --no-pager 2>/dev/null || echo "로그 확인 실패 (sudo 필요)"

