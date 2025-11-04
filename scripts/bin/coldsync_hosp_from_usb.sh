#!/usr/bin/env bash
set -Eeuo pipefail
USB=/mnt/usb/두리백업/latest
DST=/mnt/e/DuRiSafe_HOSP/latest
LOCK=/var/lock/coldsync_hosp.lock
LOG=/var/log/coldsync_hosp.log
exec 9>"$LOCK"; flock -n 9 || exit 0
exec >>"$LOG" 2>&1
[[ -d "$USB" ]] || { echo "[skip] USB not mounted"; exit 0; }
rsync -aH -L --safe-links --copy-unsafe-links \
  --delete-delay --mkpath --modify-window=2 \
  --no-perms --no-owner --no-group \
  "$USB/" "$DST/"
echo "[OK] HOSP cold synced $(date)"
# Auto-install test Tue Nov  4 10:57:45 KST 2025
# Auto-deploy test 2025-11-04 11:21:42
# Save trigger test 2025-11-04 11:24:57
