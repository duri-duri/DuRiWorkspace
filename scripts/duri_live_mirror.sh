#!/usr/bin/env bash
# DuRi 워크트리 → USB 최신화(+manifest + handoff)
set -Eeuo pipefail
shopt -s nullglob

# ===== defaults =====
SRC="${SRC:-/home/duri/DuRiWorkspace}"
USB_ROOT="${USB_ROOT:-/mnt/g/두리백업}"
USB_DIR="${USB_DIR:-$USB_ROOT/latest}"
MANIROOT="${MANIROOT:-$USB_ROOT/.manifest}"
LOG_DIR="${LOG_DIR:-/var/log/duri2-backup}"
LOCK_FILE="${LOCK_FILE:-/var/lock/duri_live.lock}"
EXCLUDES="${EXCLUDES:-.git/ .github/ ARCHIVE/ *.tar.zst}"
MODIFY_WINDOW="${MODIFY_WINDOW:-2}"     # NTFS/WSL 권장
LOG_LEVEL="${LOG_LEVEL:-INFO}"          # DEBUG|INFO|WARN|ERROR
DRYRUN=0
DEBUG=0
DESK_DIR="${DESK_DIR:-}"                # 필요 시만 사용

usage(){ cat <<USAGE
Usage: $0 [--dry-run] [--debug] [--desk] [--src DIR] [--usb-root DIR]
USAGE
}
while (( $# )); do
  case "$1" in
    --dry-run) DRYRUN=1 ;;
    --debug) DEBUG=1; LOG_LEVEL=DEBUG; set -x ;;
    --desk) [[ -z "$DESK_DIR" ]] && DESK_DIR="/mnt/c/Users/admin/Desktop/두리백업/latest" ;;
    --src) SRC="$2"; shift ;;
    --usb-root) USB_ROOT="$2"; USB_DIR="$USB_ROOT/latest"; MANIROOT="$USB_ROOT/.manifest"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown arg: $1"; usage; exit 2;;
  esac; shift
done

mkdir -p "$LOG_DIR" "$USB_DIR" "$MANIROOT"
LOG_FILE="$LOG_DIR/live_mirror.$(date +%Y%m%d_%H%M%S).log"
TS(){ date -Iseconds; }
jlog(){ local lvl="$1"; shift; local msg="$1"; shift||true
  case "$LOG_LEVEL:$lvl" in DEBUG:DEBUG|INFO:DEBUG|INFO:INFO|WARN:DEBUG|WARN:INFO|WARN:WARN|ERROR:*);;*) return 0;; esac
  local kv=""; for x in "$@"; do kv="$kv,\"${x%%=*}\":\"${x#*=}\""; done
  printf '{"ts":"%s","level":"%s","msg":"%s"%s}\n' "$(TS)" "$lvl" "$msg" "${kv#*,}" | tee -a "$LOG_FILE"; }

exec 9>"$LOCK_FILE"; flock -n 9 || { echo "[skip] duri_live running"; exit 0; }

# manifest(dry-run) — 항상 **상대경로**로 기록
ts="$(date +%Y%m%d_%H%M%S)"
MANI="$MANIROOT/$ts.files"
rsync -ai --delete --out-format='%i|%n' --modify-window="$MODIFY_WINDOW" \
  --exclude='.git/' --exclude='.github/' --exclude='ARCHIVE/' --exclude='*.tar.zst' \
  --dry-run "$SRC/" "$USB_DIR/" \
| sed -E 's#^[.]/##; s#^/##' > "$MANI"

# 실제 동기(USB 최신 상태만 유지)
rsflags=(-a --delete --mkpath --modify-window="$MODIFY_WINDOW")
[[ $DRYRUN -eq 1 ]] && rsflags+=(-n)
for ex in $EXCLUDES; do rsflags+=(--exclude="$ex"); done
rsync "${rsflags[@]}" "$SRC/" "$USB_DIR/"

# (옵션) 데스크톱도 최신화 원하면 --desk
if [[ -n "$DESK_DIR" ]]; then
  mkdir -p "$DESK_DIR"
  rsync "${rsflags[@]}" "$SRC/" "$DESK_DIR/"
fi

# handoff
SEQF="$USB_ROOT/.handoff.seq"
SEQ=$(( $(cat "$SEQF" 2>/dev/null || echo 0) + 1 ))
echo "$SEQ" > "$SEQF"
: > "$USB_ROOT/.handoff_READY"
jlog INFO "handoff" seq="$SEQ" manifest="$MANI"
