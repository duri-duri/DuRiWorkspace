#!/usr/bin/env bash
set -Eeuo pipefail
LC_ALL=C
TS(){ date "+%F %T"; }; log(){ echo "[$(TS)] $*" | tee -a "$LOG_FILE"; }

DESK_ROOT="${DESK_ROOT:-/mnt/c/Users/admin/Desktop/두리백업}"
ARCHIVE="${ARCHIVE:-}"
KEEP_CHECK="${KEEP_CHECK:-3}"
HEAD_N="${HEAD_N:-50}"
LOG_FILE="${LOG_FILE:-var/logs/hdd_verify.log}"
FAILS=0

mkdir -p "$(dirname "$LOG_FILE")"
log "HDD verify start (root=$DESK_ROOT, check=$KEEP_CHECK, head=$HEAD_N)"

# 최신 FULL N개 선정
mapfile -t FULLS < <(find "$DESK_ROOT" -type f -name "FULL__*.tar.*" -printf "%T@ %p
" 2>/dev/null | sort -nr | head -n "$KEEP_CHECK" | awk '{$1=""; sub(/^ /,""); print}')
if ((${#FULLS[@]}==0)); then
  log "no FULL archives found"; exit 0
fi

[ -n "$ARCHIVE" ] && FULLS=("$ARCHIVE")

for A in "${FULLS[@]}"; do
  log "verify: $A"
  # 1) 압축 무결성
  if zstd -tq -- "$A"; then
    log "zstd test: OK"
  else
    log "zstd test: CORRUPT ❌"; FAILS=$((FAILS+1)); continue
    continue
  fi

  # 2) 샘플 목록(빠른 헤더 접근)
  if ( set +o pipefail; zstd -dc -- "$A" | tar -tf - 2>/dev/null | head -n "$HEAD_N" >/dev/null ); then
    log "list sample: OK (head ${HEAD_N})"
  else
    log "list sample: FAIL ⚠️"; FAILS=$((FAILS+1))
  fi
done

[ "$FAILS" -gt 0 ] && { log "HDD verify done with FAILS=$FAILS"; exit 1; } || log "HDD verify done (all OK)"
