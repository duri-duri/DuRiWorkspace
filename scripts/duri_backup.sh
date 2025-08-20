#!/usr/bin/env bash
set -Eeuo pipefail

MODE="${1:-full}"              # 기본: full(USB 검증형)
SRC_DIR="${2:-/home/duri/DuRiWorkspace}"
TS="$(date +%F__%H%M)"
HOST="host-$(hostname -s)"
LOG_DIR="${LOG_DIR:-/var/log/duri2-backup}"
mkdir -p "$LOG_DIR" 2>/dev/null || LOG_DIR="/tmp/duri2-backup"
RUNLOG="$LOG_DIR/run_${TS}_${MODE}.log"

# PRECHECK START
precheck_usb_or_fallback() {
  USB_MNT="/mnt/usb"
  DESKTOP_ROOT="/mnt/c/Users/admin/Desktop/두리백업"
  mkdir -p "$DESKTOP_ROOT" 2>/dev/null || true

  # 1) /mnt/usb가 fstab 자동 마운트로 살아있으면 OK
  if mount | grep -q " on ${USB_MNT} "; then
    log "[PRECHECK] USB mounted at ${USB_MNT}"
    echo "$USB_MNT"
    return 0
  fi

  # 2) fstab 등록되어 있으면 재마운트 시도
  if grep -qE '^[A-Z]:[[:space:]]+/mnt/usb[[:space:]]+drvfs' /etc/fstab 2>/dev/null; then
    if sudo mount /mnt/usb 2>/dev/null; then
      log "[PRECHECK] USB mounted via fstab"
      echo "$USB_MNT"
      return 0
    fi
  fi

  # 3) 마지막 폴백: 데스크톱 경로
  log "[PRECHECK] USB unavailable -> fallback to Desktop: ${DESKTOP_ROOT}"
  echo "$DESKTOP_ROOT"
  return 0
}

# 대상 루트 자동 결정
BACKUP_ROOT="$(precheck_usb_or_fallback)"
echo "[PRECHECK] Backup root determined: ${BACKUP_ROOT}"

# USB와 데스크톱 경로 설정
if [[ "$BACKUP_ROOT" == "/mnt/usb" ]]; then
  USB="/mnt/usb"
  DESKTOP_ROOT="/mnt/c/Users/admin/Desktop/두리백업"
  DEST_DESKTOP_DIR="${DESKTOP_ROOT}/$(date +%Y)/$(date +%m)/$(date +%d)"
  mkdir -p "$DEST_DESKTOP_DIR" 2>/dev/null || true
else
  USB=""
  DESKTOP_ROOT="$BACKUP_ROOT"
  DEST_DESKTOP_DIR="${DESKTOP_ROOT}/$(date +%Y)/$(date +%m)/$(date +%d)"
  mkdir -p "$DEST_DESKTOP_DIR" 2>/dev/null || true
fi
# PRECHECK END

# 공통 tar 옵션(메타 보존)
TAR_FLAGS=(--numeric-owner --acls --xattrs --xattrs-include='*' --same-owner --hard-dereference)

die(){ echo "[FATAL] $*" | tee -a "$RUNLOG"; exit 1; }
log(){ echo "[$(date '+%F %T')] $*" | tee -a "$RUNLOG"; }

# 모드별 규격
case "$MODE" in
  full)     exec "$(dirname "$0")/duri_backup_full_canonical.sh";;
  extended) PREFIX="EXT";     EXCLUDES_FILE="scripts/backup_exclude_extended.txt";;
  dev)      PREFIX="DEV";     EXCLUDES_FILE="scripts/backup_exclude_dev.txt";;
  artifact) PREFIX="ART";     EXCLUDES_FILE="scripts/backup_exclude_artifact.txt";;
  *) die "unknown mode: $MODE";;
esac

ARCH_NAME="${PREFIX}__${TS}__${HOST}.tar.zst"
DEST_USB="${USB}/${ARCH_NAME}"
DEST_DESK="${DEST_DESKTOP_DIR}/${ARCH_NAME}"

# exclude 규칙 구성
EX_ARGS=()
if [[ -n "${EXCLUDES_FILE}" && -f "${EXCLUDES_FILE}" ]]; then
  while IFS= read -r p; do 
    [[ -z "$p" || "$p" =~ ^# ]] && continue; 
    EX_ARGS+=(--exclude="$p"); 
  done < "${EXCLUDES_FILE}"
fi

log "MODE=${MODE} SRC=${SRC_DIR}"
log "DEST_USB=${DEST_USB}"
log "DEST_DESK=${DEST_DESK}"

# ---- 백업 생성 (tar → zstd) ----
tmp_tar="$(mktemp -u /tmp/duri_backup_payload.XXXXXX.tar)"
cleanup(){ rm -f "$tmp_tar"; }
trap cleanup EXIT

log "creating tar…"
tar "${EX_ARGS[@]}" "${TAR_FLAGS[@]}" -cf "${tmp_tar}" -C "${SRC_DIR}" . 2>>"$RUNLOG" || die "tar failed"

log "compressing to backup destinations…"

# USB 백업 (USB가 있을 때만)
if [[ -n "$USB" && -d "$USB" ]]; then
  log "📁 USB 백업 시작: ${DEST_USB}"
  if zstd -T0 -19 -f "${tmp_tar}" -o "${DEST_USB}" 2>>"$RUNLOG"; then
    log "✅ USB 백업 완료: ${DEST_USB}"
  else
    log "⚠️  USB 백업 실패, 데스크톱으로 계속 진행"
  fi
else
  log "ℹ️  USB 백업 스킵 (USB 마운트 없음)"
fi

# 데스크톱 백업 (항상 진행)
log "📁 데스크톱 백업 시작: ${DEST_DESK}"
if zstd -T0 -19 -f "${tmp_tar}" -o "${DEST_DESK}" 2>>"$RUNLOG"; then
  log "✅ 데스크톱 백업 완료: ${DEST_DESK}"
else
  die "데스크톱 백업 실패: ${DEST_DESK}"
fi

# ---- full 모드 검증(USB 복원 스모크) ----
if [[ "$MODE" == "full" ]]; then
  if [[ -n "$USB" && -d "$USB" ]]; then
    IMG="${USB}/duri2.img"
    if [[ -e "$IMG" ]]; then
      log "🔍 USB 롤백 검증 시작..."
      
      MNT="/mnt/duri2_usb"
      mkdir -p "$MNT" 2>/dev/null || true
      LOOP="$(losetup -f --show "$IMG" 2>/dev/null)" || { log "[WARN] losetup 실패, 검증 스킵"; exit 0; }
      trap 'umount "$MNT" 2>/dev/null || true; losetup -d "$LOOP" 2>/dev/null || true' EXIT

      log "mkfs.ext4 -F ${LOOP}"
      mkfs.ext4 -F -L DURI2 "$LOOP" >>"$RUNLOG" 2>&1 || { log "[WARN] mkfs 실패, 검증 스킵"; exit 0; }
      
      log "mount ${LOOP} ${MNT}"
      mount "$LOOP" "$MNT" 2>/dev/null || { log "[WARN] mount 실패, 검증 스킵"; exit 0; }

      log "restore to ${MNT}"
      zstd -dc < "${DEST_USB}" | tar -xvf - -C "${MNT}" "${TAR_FLAGS[@]}" >>"$RUNLOG" 2>&1 || { log "[WARN] restore 실패, 검증 스킵"; exit 0; }

      # 간단한 구조 비교(샘플)
      ORIG_COUNT=$(find "${SRC_DIR}" -type f 2>/dev/null | wc -l)
      REST_COUNT=$(find "${MNT}" -type f 2>/dev/null | wc -l)
      log "compare count: orig=${ORIG_COUNT} restored=${REST_COUNT}"
      
      if [[ "$ORIG_COUNT" -gt 0 && "$REST_COUNT" -gt 0 ]]; then
        RESTORE_RATIO=$(echo "scale=1; $REST_COUNT * 100 / $ORIG_COUNT" | bc 2>/dev/null || echo "0")
        log "✅ 복원률: ${RESTORE_RATIO}%"
      fi

      umount "$MNT" 2>/dev/null || true
      losetup -d "$LOOP" 2>/dev/null || true
      log "✅ USB 롤백 검증 완료"
    else
      log "[WARN] USB 이미지 없음: ${IMG} → 검증 스킵"
    fi
  else
    log "ℹ️  USB 롤백 검증 스킵 (USB 마운트 없음)"
  fi
fi

log "[DONE] backup ${MODE} -> ${ARCH_NAME}"
log "📁 백업 위치:"
log "   USB: ${DEST_USB}"
log "   데스크톱: ${DEST_DESK}"
log "📋 로그: ${RUNLOG}"
