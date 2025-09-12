#!/usr/bin/env bash
set -euo pipefail
SNAP=${1:?Usage: ssd_fast_restore.sh SNAP_NAME}
zstd -d /mnt/i/DURISSD/FAST_RESTORE/$SNAP.tar.zst -c | tar -xf - -C ~/
echo "[OK] RESTORED <= $SNAP"
