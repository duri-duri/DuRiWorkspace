#!/usr/bin/env bash
set -euo pipefail
CMD="${1:-help}"; shift || true

case "$CMD" in
  mirror)
    ./scripts/auto_mirror_latest.sh
    ;;
  watch)
    nohup ./scripts/watch_full_backup.sh > logs/watch_full_backup.out 2>&1 &
    echo "[OK] watcher 백그라운드 시작 (logs/watch_full_backup.out)"
    ;;
  status)
    tail -n 50 logs/watch_full_backup.out || true
    ls -l /mnt/e/DuRiSafe_HOSP/FULL/LATEST.txt || true
    [ -s /mnt/e/DuRiSafe_HOSP/FULL/LATEST.txt ] && \
      echo "LATEST -> $(cat /mnt/e/DuRiSafe_HOSP/FULL/LATEST.txt)"
    ;;
  meta)
    ./scripts/meta_refresh.sh "$@"
    ;;
  stop)
    pkill -f watch_full_backup.sh || true
    echo "[OK] watcher 중지"
    ;;
  help|*)
    echo "Usage: scripts/backup_ops.sh {mirror|watch|status|meta [GOLD_FILE]|stop}"
    ;;
esac
