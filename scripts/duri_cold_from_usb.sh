#!/usr/bin/env bash
# USB → Cold(HOSP/HOME) 증가분 동기(매니페스트 while-read 파서)
set -Eeuo pipefail
shopt -s nullglob

MODE="${1:-hosp}"                              # hosp|home
USB_ROOT="${USB_ROOT:-/mnt/usb/두리백업}"
USB_DIR="${USB_DIR:-$USB_ROOT/latest}"
HOSP_DIR="${HOSP_DIR:-/mnt/e/DuRiSafe_HOSP/latest}"
HOME_DIR="${HOME_DIR:-/mnt/f/DuRiSafe_HOME/latest}"
MANIROOT="${MANIROOT:-$USB_ROOT/.manifest}"
LOG_DIR="${LOG_DIR:-/var/log/duri2-backup}"
LOCK_FILE="${LOCK_FILE:-/var/lock/duri_cold.lock}"
LOG_LEVEL="${LOG_LEVEL:-INFO}"
DRYRUN=0
DEBUG=0
FULL=0

usage(){ echo "Usage: $0 [hosp|home] [--dry-run] [--debug] [--full]"; }
while (( $# )); do
  case "$1" in
    hosp|home) MODE="$1" ;;
    --dry-run) DRYRUN=1 ;;
    --debug) DEBUG=1; LOG_LEVEL=DEBUG; set -x ;;
    --full) FULL=1 ;;
    -h|--help) usage; exit 0 ;;
  esac; shift || true
done

mkdir -p "$LOG_DIR"; LOG_FILE="$LOG_DIR/cold_sync.$(date +%Y%m%d_%H%M%S).log"
TS(){ date -Iseconds; }
jlog(){ local lvl="$1"; shift; local msg="$1"; shift||true
  case "$LOG_LEVEL:$lvl" in DEBUG:DEBUG|INFO:DEBUG|INFO:INFO|WARN:DEBUG|WARN:INFO|WARN:WARN|ERROR:*);;*) return 0;; esac
  local kv=""; for x in "$@"; do kv="$kv,\"${x%%=*}\":\"${x#*=}\""; done
  printf '{"ts":"%s","level":"%s","msg":"%s"%s}\n' "$(TS)" "$lvl" "$msg" "${kv#*,}" | tee -a "$LOG_FILE"; }

exec 9>"$LOCK_FILE"; flock -n 9 || { echo "[skip] cold running"; exit 0; }

DEST="$HOSP_DIR"; [[ "$MODE" == "home" ]] && DEST="$HOME_DIR"
mkdir -p "$DEST"

# 전체 비교 우회 스위치
rsflags=(-a --mkpath --modify-window=2)
[[ $DRYRUN -eq 1 ]] && rsflags+=(-n)
if [[ $FULL -eq 1 ]]; then
  rsync "${rsflags[@]}" --delete "$USB_DIR/" "$DEST/"
  jlog INFO "cold_done_full" mode="$MODE"
  exit 0
fi

# 최신 매니페스트
mani="$(ls -1t "$MANIROOT"/*.files 2>/dev/null | head -n1 || true)"
jlog INFO "cold_start" mode="$MODE" usb="$USB_DIR" dest="$DEST" mani="${mani##*/}" dry="$DRYRUN"
if [[ -z "$mani" || ! -f "$mani" ]]; then
  rsync "${rsflags[@]}" --delete "$USB_DIR/" "$DEST/"
  jlog INFO "cold_done_full_no_manifest" mode="$MODE"
  exit 0
fi

# --- 추가/변경 목록 파싱 (while-read, 상대경로 정규화) ---
paths_file="$(mktemp)"
while IFS='|' read -r tag rawpath; do
  # rsync -i tag: 파일/디렉(>, c, h, d 등)만, 삭제/제거 라인은 제외
  case "$tag" in (\**|*deleting*) continue;; esac
  p="${rawpath#./}"; p="${p#/}"
  # 다양한 프리픽스 제거(절대·다른 루트 방어)
  p="${p#*DuRiWorkspace/}"
  p="${p#*두리백업/latest/}"
  p="${p#*DuRiSafe_HOSP/latest/}"
  p="${p#*DuRiSafe_HOME/latest/}"
  # USB 기준 실제 존재하는 것만
  if [ -e "$USB_DIR/$p" ] || [ -d "$USB_DIR/$p" ]; then
    printf '%s\n' "$p" >> "$paths_file"
  fi
done < "$mani"

if [[ -s "$paths_file" ]]; then
  rsync "${rsflags[@]}" --files-from="$paths_file" "$USB_DIR/" "$DEST/"
fi
rm -f "$paths_file"

# --- 삭제 반영 ---
deletes_file="$(mktemp)"
while IFS='|' read -r tag rawpath; do
  case "$tag" in (\**|*deleting*))
    p="${rawpath#./}"; p="${p#/}"
    p="${p#*DuRiWorkspace/}"
    p="${p#*두리백업/latest/}"
    p="${p#*DuRiSafe_HOSP/latest/}"
    p="${p#*DuRiSafe_HOME/latest/}"
    printf '%s\n' "$p" >> "$deletes_file"
  ;; esac
done < "$mani"

if [[ -s "$deletes_file" ]]; then
  while IFS= read -r p; do
    [ -e "$DEST/$p" ] && rm -rf -- "$DEST/$p"
  done < "$deletes_file"
fi
rm -f "$deletes_file"

jlog INFO "cold_done" mode="$MODE"