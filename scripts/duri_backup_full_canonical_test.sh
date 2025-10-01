#!/usr/bin/env bash
set -Eeuo pipefail
TS() { date '+%F %T'; }
log(){ echo "[$(TS)] $*"; }

SRC="${SRC:-/home/duri/DuRiWorkspace}"
TODAY="$(date +%Y/%m/%d)"
DESK_DIR="/mnt/c/Users/admin/Desktop/두리백업/${TODAY}"
USB_DIR="/mnt/usb"
HOST="$(hostname -s)"
BASENAME="FULL__$(date +%F__%H%M)__host-${HOST}.tar.zst"

ART_DESK="${DESK_DIR}/${BASENAME}"
ART_USB="${USB_DIR}/${BASENAME}"
TMP_DESK="${ART_DESK}.part"

mkdir -p "$DESK_DIR"

# 1) 데스크톱에 '정식 아티팩트' 생성 (USB에서 검증된 파이프라인 그대로)
log "creating canonical artifact on Desktop…"
if tar --numeric-owner --acls --xattrs -C "$SRC" -cpf - . | zstd -T0 -3 -q -o "$TMP_DESK"; then
  sync "$TMP_DESK" || true
  mv -f "$TMP_DESK" "$ART_DESK"
else
  rm -f "$TMP_DESK"; log "[FATAL] Desktop artifact creation failed"; exit 1
fi

# 2) 데스크톱 체크섬
( cd "$DESK_DIR" && sha256sum "$(basename "$ART_DESK")" > "SHA256SUMS.$(basename "$ART_DESK").txt" )
log "✅ Desktop artifact ready: $ART_DESK"

# 3) USB 미러(가능하면) + 체크섬 검증
USB_OK=false
if [ -d "$USB_DIR" ] && [ -w "$USB_DIR" ]; then
  log "mirroring to USB…"
  # USB에 올바른 디렉토리 구조 생성
  USB_BACKUP_DIR="${USB_DIR}/두리백업/${TODAY}"
  mkdir -p "$USB_BACKUP_DIR" || true

  # USB 백업 경로 수정
  ART_USB="${USB_BACKUP_DIR}/${BASENAME}"

  if command -v rsync >/dev/null 2>&1; then
    rsync --inplace --partial "$ART_DESK" "$ART_USB" && USB_OK=true || true
  else
    cp -f "$ART_DESK" "$ART_USB" && USB_OK=true || true
  fi
  if $USB_OK; then
    SUM_D="$(sha256sum "$ART_DESK" | awk '{print $1}')"
    SUM_U="$(sha256sum "$ART_USB"  | awk '{print $1}')"
    if [ "$SUM_D" = "$SUM_U" ]; then
      ( cd "$(dirname "$ART_USB")" && echo "$SUM_U  $(basename "$ART_USB")" > "SHA256SUMS.$(basename "$ART_USB").txt" )
      log "✅ USB mirror verified: $ART_USB"
    else
      log "[WARN] USB checksum mismatch"; USB_OK=false
    fi
  else
    log "[WARN] USB mirror failed"
  fi
else
  log "[INFO] USB not mounted/writable — skipping mirror"
fi

# 4) 보완 마커 + 종료 규칙
if $USB_OK; then
  log "SUMMARY: Desktop=OK, USB=OK → success"; exit 0
else
  echo "$(date -Iseconds) PENDING_USB $(basename "$ART_DESK")" >> "${DESK_DIR}/.pending_usb_mirror"
  log "SUMMARY: Desktop=OK, USB=MISS → success (보완 필요)"; exit 0
fi
