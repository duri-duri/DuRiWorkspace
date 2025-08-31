#!/usr/bin/env bash
set -Eeuo pipefail
TS() { date '+%F %T'; }
log(){ echo "[$(TS)] $*"; }

# HDD→USB→Desktop 우선순위 선택자 로드
source scripts/duri_backup.dest.sh

SRC="${SRC:-/home/duri/DuRiWorkspace}"
TODAY="$(date +%Y/%m/%d)"
HOST="$(hostname -s)"
BASENAME="FULL__$(date +%F__%H%M)__host-${HOST}.tar.zst"

# HDD-우선 목적지 선택
DEST_MAIN="$(choose_dest)"
DEST_FILE_MAIN="${DEST_MAIN}/${BASENAME}"

# 미러 후보들 준비
USB="/mnt/usb"
DESK_DIR="/mnt/c/Users/admin/Desktop/두리백업/${TODAY}"
mkdir -p "$DESK_DIR" 2>/dev/null || true
DEST_FILE_USB="${USB}/두리백업/${TODAY}/${BASENAME}"
DEST_FILE_DESK="${DESK_DIR}/${BASENAME}"

log "PRIMARY=${DEST_FILE_MAIN}"
log "MIRRORS: USB=${DEST_FILE_USB} DESK=${DEST_FILE_DESK}"

# 1) PRIMARY 백업 생성 (HDD 우선)
log "📁 PRIMARY 백업 시작: ${DEST_FILE_MAIN}"
TMP_MAIN="${DEST_FILE_MAIN}.part"
mkdir -p "$(dirname "$DEST_FILE_MAIN")" 2>/dev/null || true

if tar --numeric-owner --acls --xattrs -C "$SRC" -cpf - . | zstd -T0 -19 -q -o "$TMP_MAIN"; then
  sync "$TMP_MAIN" || true
  mv -f "$TMP_MAIN" "$DEST_FILE_MAIN"
  # 목적지 스탬프(증적 남김)
  stamp_dest "$(dirname "$DEST_FILE_MAIN")" "$BASENAME"
  log "✅ PRIMARY 백업 완료: $DEST_FILE_MAIN"
else
  rm -f "$TMP_MAIN"
  log "[FATAL] PRIMARY 백업 실패: $DEST_FILE_MAIN"
  exit 1
fi

# 2) USB 미러 (PRIMARY가 USB가 아닐 때만)
USB_OK=false
if [[ -d "$USB" && "$(dirname "$DEST_FILE_MAIN")" != "$USB" ]]; then
  log "📁 USB 미러 시작: ${DEST_FILE_USB}"
  mkdir -p "$(dirname "$DEST_FILE_USB")" 2>/dev/null || true
  
  if command -v rsync >/dev/null 2>&1; then
    rsync --inplace --partial "$DEST_FILE_MAIN" "$DEST_FILE_USB" && USB_OK=true || true
  else
    cp -f "$DEST_FILE_MAIN" "$DEST_FILE_USB" && USB_OK=true || true
  fi
  
  if $USB_OK; then
    SUM_M="$(sha256sum "$DEST_FILE_MAIN" | awk '{print $1}')"
    SUM_U="$(sha256sum "$DEST_FILE_USB" | awk '{print $1}')"
    if [ "$SUM_M" = "$SUM_U" ]; then
      ( cd "$(dirname "$DEST_FILE_USB")" && echo "$SUM_U  $(basename "$DEST_FILE_USB")" > "SHA256SUMS.$(basename "$DEST_FILE_USB").txt" )
      log "✅ USB 미러 검증 완료: $DEST_FILE_USB"
    else
      log "[WARN] USB 체크섬 불일치"; USB_OK=false
    fi
  else
    log "[WARN] USB 미러 실패"
  fi
else
  log "ℹ️ USB 미러 스킵 (PRIMARY가 USB이거나 USB 마운트 안됨)"
fi

# 3) Desktop 미러 (PRIMARY가 Desktop이 아닐 때만)
if [[ "$(dirname "$DEST_FILE_MAIN")" != "$DESK_DIR" ]]; then
  log "📁 Desktop 미러 시작: ${DEST_FILE_DESK}"
  TMP_DESK="${DEST_FILE_DESK}.part"
  
  if tar --numeric-owner --acls --xattrs -C "$SRC" -cpf - . | zstd -T0 -19 -q -o "$TMP_DESK"; then
    sync "$TMP_DESK" || true
    mv -f "$TMP_DESK" "$DEST_FILE_DESK"
    ( cd "$DESK_DIR" && sha256sum "$(basename "$DEST_FILE_DESK")" > "SHA256SUMS.$(basename "$DEST_FILE_DESK").txt" )
    log "✅ Desktop 미러 완료: $DEST_FILE_DESK"
  else
    rm -f "$TMP_DESK"
    log "[WARN] Desktop 미러 실패"
  fi
else
  log "ℹ️ Desktop 미러 스킵 (PRIMARY가 Desktop)"
fi

# 4) 종료 규칙
if $USB_OK; then
  log "SUMMARY: PRIMARY=OK, USB=OK → success"
else
  log "SUMMARY: PRIMARY=OK, USB=MISS → success (보완 필요)"
fi
exit 0















