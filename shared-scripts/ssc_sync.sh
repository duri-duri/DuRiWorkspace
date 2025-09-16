#!/usr/bin/env bash
# ssc_sync.sh — HDD의 최신 산출물을 SSD 캐시에 자동 동기화(점진/안전)
# 사용: ./ssc_sync.sh [--dry-run] [--once|--loop] [--src DIR] [--dst DIR]
set -Eeo pipefail

SRC="${SRC:-/mnt/hdd/ARCHIVE/FULL}"          # 원본(HDD)
DST="${DST:-/mnt/i/DURISSD/FAST_RESTORE}"    # 캐시(SSD)  ※ 환경에 맞게 조정
LOGDIR="${LOGDIR:-/var/log/duri/ssc_sync}"
LOCKFILE="${LOCKFILE:-/var/lock/ssc_sync.lock}"
INTERVAL="${INTERVAL:-600}"                  # 루프 모드 간격(초)
RSYNC_OPTS="-aH --delete --info=stats2 --human-readable"

mkdir -p "$LOGDIR" "$DST" || true
LOGFILE="${LOGDIR}/ssc_sync_$(date +%Y%m%d_%H%M%S).log"

log(){ printf "[%s] %s\n" "$(date '+%F %T')" "$*" | tee -a "$LOGFILE" >&2; }

health_check(){
  [[ -d "$SRC" && -r "$SRC" ]] || { log "SRC 접근 불가: $SRC"; return 1; }
  mkdir -p "$DST" && [[ -w "$DST" ]] || { log "DST 쓰기 불가: $DST"; return 1; }
  return 0
}

do_sync(){
  log "SSC 동기화 시작 → SRC: $SRC  DST: $DST"
  health_check
  # I/O 친화도 ↓
  ionice -c2 -n7 nice -n 10 rsync $RSYNC_OPTS $DRYRUN --delete-excluded \
    --exclude '.~tmp~*' \
    --exclude '*.partial' \
    --exclude 'lost+found' \
    "$SRC"/ "$DST"/ | tee -a "$LOGFILE"
  log "SSC 동기화 종료"
}

mode="once"; DRYRUN=""
for a in "$@"; do
  case "$a" in
    --dry-run) DRYRUN="--dry-run" ;;
    --once) mode="once" ;;
    --loop) mode="loop" ;;
    --src) shift; SRC="$1" ;;
    --dst) shift; DST="$1" ;;
  esac
done

# 중복 실행 방지
exec 9>"$LOCKFILE" || true
if ! flock -n 9; then
  log "이미 실행 중 → 종료"; exit 0
fi

if [[ "$mode" == "loop" ]]; then
  while :; do do_sync || true; sleep "$INTERVAL"; done
else
  do_sync
fi
