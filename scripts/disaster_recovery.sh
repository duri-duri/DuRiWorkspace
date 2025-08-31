#!/usr/bin/env bash
set -Eeuo pipefail
TS(){ date "+%F %T"; }; log(){ echo "[$(TS)] $*"; }

# 백업 후보 목적지들 (깊이 제한 없이)
cands=(/mnt/hdd/ARCHIVE/FULL /mnt/usb /mnt/c/Users/admin/Desktop/두리백업)

# 최신 FULL 백업 찾기 (깊이 제한 없이)
LATEST="$(find "${cands[@]}" -type f -name 'FULL__*.tar.zst' \
         -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -1 | cut -d' ' -f2-)"

[ -n "${LATEST:-}" ] || { log "FATAL: no FULL backup found in ${cands[*]}"; exit 1; }

log "Using backup: $LATEST"

# 무결성 검증
if command -v unzstd >/dev/null 2>&1; then
  unzstd -t "$LATEST" && log "DR integrity test OK"
else
  zstd -t -q "$LATEST" && log "DR integrity test OK"
fi

# 백업 정보 출력
log "Backup details:"
log "  File: $LATEST"
log "  Size: $(du -h "$LATEST" | cut -f1)"
log "  Date: $(stat -c %y "$LATEST")"

echo "✅ Disaster recovery check completed successfully"
