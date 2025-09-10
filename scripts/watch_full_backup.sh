#!/usr/bin/env bash
set -euo pipefail

SRC_WATCH=(
  "/mnt/h/ARCHIVE/FULL"
  "/mnt/hdd/ARCHIVE/FULL"
)

log(){ echo "[WATCH] $*" ; }

# inotify 지원 여부
if command -v inotifywait >/dev/null 2>&1; then
  log "inotify 모드 시작"
  for D in "${SRC_WATCH[@]}"; do
    [ -d "$D" ] || continue
    inotifywait -m -e close_write,create,move --format '%w%f' "$D" |
    while read -r PATH; do
      if [[ "$PATH" == *.tar.zst ]]; then
        log "TRIGGER: $PATH"
        ./scripts/auto_mirror_latest.sh || true
      fi
    done &
  done
  wait
else
  log "inotify 미사용 → 폴링 모드(60s)"
  while true; do
    ./scripts/auto_mirror_latest.sh || true
    sleep 60
  done
fi
