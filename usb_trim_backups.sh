#!/usr/bin/env bash
# usb_trim_backups.sh
# USB 캐시 백업에서 최근 N개만 보존하고 나머지는 안전하게 .trash로 이동

set -Eeuo pipefail
LC_ALL=C

# ===== 설정 =====
USB_ROOT="${USB_ROOT:-/mnt/usb/두리백업}"
KEEP_FULL="${KEEP_FULL:-7}"
KEEP_CORE="${KEEP_CORE:-3}"
KEEP_DIFF="${KEEP_DIFF:-3}"
KEEP_INC="${KEEP_INC:-0}"
DRY_RUN="${DRY_RUN:-1}"

# ===== 내부 =====
TS(){ date '+%F %T'; }
log(){ echo "[$(TS)] $*"; }

ensure_dirs() {
  mkdir -p "$USB_ROOT/.trash" "$USB_ROOT/.quarantine"
}

# 타입별 정리 함수
prune_type() {
  local type="$1" keep="$2"
  (( keep <= 0 )) && { log "skip $type (KEEP=$keep)"; return 0; }

  # 파일 나열(최신→오래됨). .quarantine/.trash 제외
  mapfile -d '' entries < <(
    find "$USB_ROOT" \
      -path "$USB_ROOT/.quarantine" -prune -o \
      -path "$USB_ROOT/.trash"      -prune -o \
      -type f -name "${type}__*.tar.*" \
      -printf '%T@ %p\0' 2>/dev/null \
    | sort -z -n -r
  )

  local total=$(( ${#entries[@]} ))
  (( total == 0 )) && { log "no ${type} archives found"; return 0; }

  log "found ${total} ${type} archives (keep ${keep})"

  # 보존 N개 이후는 .trash로 이동
  local idx=0 moved=0
  for e in "${entries[@]}"; do
    local path="${e#* }"   # 공백 뒤 경로
    if (( idx < keep )); then
      ((idx++)); continue
    fi
    local base trash_dir trash_path
    base="$(basename "$path")"
    trash_dir="$USB_ROOT/.trash/${type}"
    mkdir -p "$trash_dir"
    trash_path="${trash_dir}/$(date -r "$path" +%Y%m%d_%H%M%S)__${base}"

    if (( DRY_RUN == 1 )); then
      echo "[DRY-RUN] mv '$path' '$trash_path'"
    else
      mv -f -- "$path" "$trash_path"
    fi
    ((moved++))
    ((idx++))
  done

  log "${type}: moved ${moved} old archives to .trash (dry-run=${DRY_RUN})"
}

main() {
  [ -d "$USB_ROOT" ] || { echo "USB_ROOT not found: $USB_ROOT" >&2; exit 1; }
  ensure_dirs
  log "USB trim start (root=$USB_ROOT, dry-run=${DRY_RUN})"
  prune_type "FULL" "$KEEP_FULL"
  prune_type "CORE" "$KEEP_CORE"
  prune_type "DIFF" "$KEEP_DIFF"
  prune_type "INCREMENTAL" "$KEEP_INC"
  log "USB trim done."
  if (( DRY_RUN == 1 )); then
    echo
    echo "�� 확인 후 실제 실행하려면: DRY_RUN=0 bash usb_trim_backups.sh"
  fi
}

main "$@"
