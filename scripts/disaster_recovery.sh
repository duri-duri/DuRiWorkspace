#!/usr/bin/env bash
set -Eeuo pipefail
TS(){ date "+%F %T"; }; log(){ echo "[$(TS)] $*"; }

# 백업 후보 목적지들
cands=(/mnt/hdd/ARCHIVE/FULL /mnt/usb/두리백업 "$HOME/Desktop/두리백업")

# 최신 FULL 백업 찾기
LATEST="$(find "${cands[@]}" -maxdepth 2 -type f -name 'FULL__*.tar.zst' -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -1 | cut -d' ' -f2-)"

[ -n "$LATEST" ] || { log "FATAL: no FULL backup found"; exit 1; }

log "Using backup: $LATEST"

# 무결성 검증
if unzstd -t "$LATEST"; then
  log "DR dry-run OK: backup integrity verified"
else
  log "FATAL: backup integrity check failed"
  exit 1
fi

# 백업 정보 출력
log "Backup details:"
log "  File: $LATEST"
log "  Size: $(du -h "$LATEST" | cut -f1)"
log "  Date: $(stat -c %y "$LATEST")"

echo "✅ Disaster recovery check completed successfully"
