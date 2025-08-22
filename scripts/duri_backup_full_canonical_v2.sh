#!/usr/bin/env bash
set -Eeuo pipefail
TS(){ date '+%F %T'; }; log(){ echo "[$(TS)] $*"; }

SRC="${SRC:-/home/duri/DuRiWorkspace}"
TODAY="$(date +%Y/%m/%d)"
DESK_DIR="/mnt/c/Users/admin/Desktop/두리백업/${TODAY}"
USB_DIR="/mnt/usb/두리백업/${TODAY}"
HOST="$(hostname -s)"
BASENAME="FULL__$(date +%F__%H%M)__host-${HOST}.tar.zst"

ART_DESK="${DESK_DIR}/${BASENAME}"
ART_USB="${USB_DIR}/${BASENAME}"
TMP_DESK="${ART_DESK}.part"

mkdir -p "$DESK_DIR" "$USB_DIR"

log "creating canonical artifact on Desktop…"
if tar --numeric-owner --acls --xattrs \
  --exclude-from="$SRC/backup_exclude.txt" \
  --exclude='.git/**' \
  --exclude='var/test_restore/**' \
  --exclude='**/node_modules/**' \
  -C "$SRC" -cpf - . \
  | zstd -T0 -19 -q -o "$TMP_DESK"; then
  sync "$TMP_DESK" || true
  mv -f "$TMP_DESK" "$ART_DESK"
else
  rm -f "$TMP_DESK"; log "[FATAL] Desktop artifact creation failed"; exit 1
fi

# Desktop 체크섬 생성
( cd "$DESK_DIR" && sha256sum "$(basename "$ART_DESK")" > "SHA256SUMS.$(basename "$ART_DESK").txt" )
log "✅ Desktop artifact ready: $ART_DESK"

# USB 미러링
log "mirroring to USB…"
if command -v rsync >/dev/null 2>&1; then
  rsync --inplace --partial "$ART_DESK" "$ART_USB"
else
  cp -f "$ART_DESK" "$ART_USB"
fi

# 체크섬 검증
SUM_D="$(sha256sum "$ART_DESK" | awk '{print $1}')"
SUM_U="$(sha256sum "$ART_USB"  | awk '{print $1}')"
[ "$SUM_D" = "$SUM_U" ] || { log "[FATAL] USB mirror checksum mismatch"; exit 1; }
log "✅ USB mirror verified: $ART_USB"
log "SUMMARY: Desktop=OK, USB=OK → success"
