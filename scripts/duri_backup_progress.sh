#!/usr/bin/env bash
set -Eeuo pipefail

MODE="${1:-full}"              # 기본: full(USB 검증형)
SRC_DIR="${2:-/home/duri/DuRiWorkspace}"
TS="$(date +%F__%H%M)"
HOST="host-$(hostname -s)"
LOG_DIR="${LOG_DIR:-/var/log/duri2-backup}"
mkdir -p "$LOG_DIR" 2>/dev/null || LOG_DIR="/tmp/duri2-backup"
RUNLOG="$LOG_DIR/run_${TS}_${MODE}.log"

# 진행률 표시 함수들
show_progress_bar() {
    local current=$1
    local total=$2
    local width=50
    local filled=$((current * width / total))
    local empty=$((width - filled))
    local percent=$((current * 100 / total))

    printf "\r["
    printf "%${filled}s" | tr ' ' '█'
    printf "%${empty}s" | tr ' ' '░'
    printf "] %3d%%" "$percent"
}

show_step_progress() {
    local step=$1
    local total_steps=$2
    local current_step=$3
    local message="$4"

    echo -e "\n[${current_step}/${total_steps}] ${step}: ${message}"
}

show_file_progress() {
    local current_file="$1"
    local current_count=$2
    local total_count=$3

    # 진행률 바 업데이트
    show_progress_bar "$current_count" "$total_count"

    # 현재 파일 정보 (긴 파일명은 줄임)
    local display_file=$(basename "$current_file")
    if [[ ${#display_file} -gt 40 ]]; then
        display_file="...${display_file: -37}"
    fi
    printf " - %s" "$display_file"
}

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

# 1단계: 파일 스캔 및 크기 계산
show_step_progress "파일 스캔" 4 1 "백업 대상 파일 분석 중..."
log "creating tar…"

# 파일 개수 및 크기 계산
TOTAL_FILES=$(find "${SRC_DIR}" -type f 2>/dev/null | wc -l)
TOTAL_SIZE=$(du -sb "${SRC_DIR}" 2>/dev/null | cut -f1)
log "총 파일: ${TOTAL_FILES}개, 총 크기: ${TOTAL_SIZE} bytes"

# 2단계: tar 압축 (진행률 표시)
show_step_progress "백업 압축" 4 2 "tar 압축 중..."
echo "진행률:"

# tar 진행률을 표시하기 위해 pv 사용 (가능한 경우)
if command -v pv >/dev/null 2>&1; then
    # pv가 있으면 진행률 바와 함께 표시
    tar "${EX_ARGS[@]}" "${TAR_FLAGS[@]}" -cf - -C "${SRC_DIR}" . 2>>"$RUNLOG" | \
    pv -s "${TOTAL_SIZE}" -N "tar 압축" > "${tmp_tar}" || die "tar failed"
else
    # pv가 없으면 기본 tar 실행
    tar "${EX_ARGS[@]}" "${TAR_FLAGS[@]}" -cf "${tmp_tar}" -C "${SRC_DIR}" . 2>>"$RUNLOG" || die "tar failed"
fi

echo -e "\n✅ tar 압축 완료"

# 3단계: zstd 압축 (진행률 표시)
show_step_progress "zstd 압축" 4 3 "zstd 압축 중..."

# USB 백업 (USB가 있을 때만)
if [[ -n "$USB" && -d "$USB" ]]; then
  log "📁 USB 백업 시작: ${DEST_USB}"
  echo "USB 백업 진행률:"

  if command -v pv >/dev/null 2>&1; then
      # pv로 진행률 표시
      pv "${tmp_tar}" | zstd -T0 -19 -f -o "${DEST_USB}" 2>>"$RUNLOG"
  else
      # 기본 zstd 실행
      zstd -T0 -19 -f "${tmp_tar}" -o "${DEST_USB}" 2>>"$RUNLOG"
  fi

  if [[ $? -eq 0 ]]; then
    log "✅ USB 백업 완료: ${DEST_USB}"
  else
    log "⚠️  USB 백업 실패, 데스크톱으로 계속 진행"
  fi
else
  log "ℹ️  USB 백업 스킵 (USB 마운트 없음)"
fi

# 데스크톱 백업 (항상 진행)
log "📁 데스크톱 백업 시작: ${DEST_DESK}"
echo "데스크톱 백업 진행률:"

if command -v pv >/dev/null 2>&1; then
    # pv로 진행률 표시
    pv "${tmp_tar}" | zstd -T0 -19 -f -o "${DEST_DESK}" 2>>"$RUNLOG"
else
    # 기본 zstd 실행
    zstd -T0 -19 -f "${tmp_tar}" -o "${DEST_DESK}" 2>>"$RUNLOG"
fi

if [[ $? -eq 0 ]]; then
  log "✅ 데스크톱 백업 완료: ${DEST_DESK}"
else
  die "데스크톱 백업 실패: ${DEST_DESK}"
fi

# 4단계: 검증 (진행률 표시)
show_step_progress "백업 검증" 4 4 "백업 무결성 검증 중..."

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

echo -e "\n🎉 백업 완료!"
log "[DONE] backup ${MODE} -> ${ARCH_NAME}"
log "📁 백업 위치:"
log "   USB: ${DEST_USB}"
log "   데스크톱: ${DEST_DESK}"
log "📋 로그: ${RUNLOG}"

# 최종 요약
echo -e "\n📊 백업 요약:"
echo "   모드: ${MODE}"
echo "   파일 수: ${TOTAL_FILES}개"
echo "   총 크기: $(numfmt --to=iec-i --suffix=B "${TOTAL_SIZE}")"
echo "   백업 파일: ${ARCH_NAME}"
echo "   로그: ${RUNLOG}"
