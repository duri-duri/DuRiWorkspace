#!/usr/bin/env bash
set -Eeuo pipefail

# 동시 실행 방지 (lock 파일)
exec 9>/tmp/duri_backup_phase1.lock
flock -n 9 || { echo "[skip] another run active"; exit 0; }

# 권한 및 에러 방지
umask 027
set -euo pipefail
trap 'echo "[ERR] line $LINENO rc=$?"; exit 1' ERR

# 실행 전 용량·목표지 유효성 체크 (하드 가드)
REQUIRED_GB=20
FREE_GB=$(df -BG /mnt/c | awk 'NR==2{gsub("G","");print $4}')
[ "$FREE_GB" -lt "$REQUIRED_GB" ] && { echo "[ABORT] low disk: ${FREE_GB}GB"; exit 1; }

# 목적지 존재/쓰기 테스트
DST="/mnt/c/Users/admin/Desktop/두리백업"
mkdir -p "$DST/.probe" && echo test > "$DST/.probe/w" || { echo "[ABORT] dst not writable"; exit 1; }
rm -rf "$DST/.probe"

# 로그 전략 (일자 단위 + 핵심 지표)
LOG_DIR="${HOME}/backup_logs"
LOG="${LOG_DIR}/phase1.$(date +%F).log"
mkdir -p "$LOG_DIR"
log(){ printf '%s %s\n' "$(date +'%F %T')" "$*" | tee -a "$LOG"; }

# 작업 종료 후 요약
summary(){
  SRC="${HOME}/DuRiWorkspace"
  CNT=$(find "$SRC" -type f | wc -l)
  SIZE=$(du -sh "$SRC" | awk '{print $1}')
  log "[SUMMARY] files=$CNT size=$SIZE last_run=$(date +%F_%T)"
}

TS(){ date '+%F %T'; }
# log(){ echo "[$(TS)] $*"; }

# --- 기본 설정 ---
MODE="${1:-incr}"                     # incr | full | retention | status
SRC="${SRC:-/home/duri/DuRiWorkspace}"
HOST="$(hostname -s)"
TODAY="$(date +%Y/%m/%d)"
STAMP="$(date +%F__%H%M)"
DESK_ROOT="/mnt/c/Users/admin/Desktop/두리백업"
USB_ROOT="/mnt/usb/두리백업"
DESK_DIR="${DESK_ROOT}/${TODAY}"
USB_DIR="${USB_ROOT}/${TODAY}"
LOG_DIR="${LOG_DIR:-/var/log/duri2-backup}"
STATE_DIR="${STATE_DIR:-$HOME/.local/state/duri2-backup}"
SNAP_DIR="${SNAP_DIR:-${STATE_DIR}/snapshots}"
SNAP_FILE="${SNAP_DIR}/${HOST}_workspace.snar"   # tar 증분 스냅샷

# 디렉토리 생성
mkdir -p "$DESK_DIR" "$LOG_DIR" "$SNAP_DIR"

# 원자적 쓰기 보조
make_sha() {
  ( cd "$(dirname "$1")" && sha256sum "$(basename "$1")" > "SHA256SUMS.$(basename "$1").txt" );
}

# USB 미러링 함수
mirror_to_usb() {
  local src="$1" base dest tmp sha_d sha_u
  base="$(basename "$src")"
  dest="${USB_DIR}/${base}"
  tmp="${dest}.part"
  mkdir -p "$USB_DIR" || true

  if [ -d "$USB_ROOT/.." ] && [ -w "${USB_ROOT%/*}" ] && [ -w "$USB_DIR" ]; then
    if command -v rsync >/dev/null 2>&1; then
      rsync --inplace --partial "$src" "$tmp" || return 1
    else
      cp -f "$src" "$tmp" || return 1
    fi
    sync "$tmp" || true
    mv -f "$tmp" "$dest"
    sha_d="$(sha256sum "$src"  | awk '{print $1}')"
    sha_u="$(sha256sum "$dest" | awk '{print $1}')"
    if [ "$sha_d" = "$sha_u" ]; then
      ( cd "$USB_DIR" && echo "$sha_u  $base" > "SHA256SUMS.$base.txt" )
      log "✅ USB mirror verified: $dest"
      return 0
    else
      log "[WARN] USB checksum mismatch: $dest"
      return 1
    fi
  else
    log "[INFO] USB not mounted/writable — skip mirror"
    return 1
  fi
}

# --- 작업 함수들 ---

# 풀백업 실행
do_full() {
  log "Starting FULL backup using canonical script..."
  # 검증된 풀백업 파이프라인 재사용 (데스크톱 생성 → USB 미러)
  "$(dirname "$0")/duri_backup_full_canonical.sh"
}

# 증분 백업 실행
do_incr() {
  local base="INCR__${STAMP}__host-${HOST}.tar.zst"
  local art="${DESK_DIR}/${base}"
  local tmp="${art}.part"

  log "Creating INCREMENTAL backup on Desktop..."

  # 증분: GNU tar --listed-incremental 스냅샷 사용 (권한/ACL/XATTR 보존)
  if tar --numeric-owner --acls --xattrs \
         --listed-incremental="$SNAP_FILE" \
         -C "$SRC" -cpf - . \
    | zstd -T0 -19 -q -o "$tmp"; then
    sync "$tmp" || true
    mv -f "$tmp" "$art"
    make_sha "$art"
    log "✅ Desktop INCR ready: $art"
  else
    rm -f "$tmp"
    log "[FATAL] Desktop incremental creation failed"; exit 1
  fi

  # USB 미러링 시도
  if mirror_to_usb "$art"; then
    log "SUMMARY: Desktop=OK, USB=OK → success"
  else
    echo "$(date -Iseconds) PENDING_USB $(basename "$art")" >> "${DESK_DIR}/.pending_usb_mirror"
    log "SUMMARY: Desktop=OK, USB=MISS → success (보완 필요)"
  fi
}

# 보관 정책 실행
do_retention() {
  local keep="${KEEP_DAYS:-30}"
  log "Retention: delete *.tar.zst older than ${keep} days"

  for root in "$DESK_ROOT" "$USB_ROOT"; do
    [ -d "$root" ] || continue
    # 오래된 백업 파일 삭제
    find "$root" -type f -name '*.tar.zst' -mtime +"$keep" -print -delete || true
    # 같이 만든 SHA 파일도 정리
    find "$root" -type f -name 'SHA256SUMS.*.txt' -mtime +"$keep" -print -delete || true
    # 빈 날짜 폴더 정리
    find "$root" -type d -empty -delete || true
  done
  log "Retention cleanup completed."
}

# 상태 확인
do_status() {
  echo "=== Desktop latest ==="
  ls -lh "$DESK_DIR" | tail -n +1 || echo "(no files)"
  echo
  echo "=== USB latest ==="
  ls -lh "$USB_DIR"  | tail -n +1 || echo "(no files)"
  echo
  echo "=== Pending USB mirror markers ==="
  grep -h 'PENDING_USB' "$DESK_ROOT"/**/.pending_usb_mirror 2>/dev/null || echo "(none)"
  echo
  echo "=== Recent logs ==="
  tail -n 20 "${LOG_DIR}/phase1_backup.log" 2>/dev/null || echo "(no logs)"
}

# --- 메인 실행 ---
# 로그 파일에 적재
exec >>"${LOG_DIR}/phase1_backup.log" 2>&1

log "START mode=${MODE} SRC=${SRC}"

case "$MODE" in
  full)      do_full ;;
  incr)      do_incr ;;
  retention) do_retention ;;
  status)    do_status ;;
  *)         echo "Usage: $0 {full|incr|retention|status}"; exit 2 ;;
esac

log "END mode=${MODE}"
summary
