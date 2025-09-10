#!/usr/bin/env bash
# Snapshot current scheduling state (cron & timers) with diff/retention.
# Standalone now; later can be ingested into axis=automation_cron.
# Modes:
#   MODE=snapshot (default) | diff | purge | status
# Vars:
#   ROOT=/mnt/h/ARCHIVE (default)
#   KEEP_DAYS=90          (retention for purge)
#   TAGS="weekday,backup" (free-form labels for later axis mapping)

set -Eeuo pipefail

MODE="${MODE:-snapshot}"
ROOT="${ROOT:-/mnt/h/ARCHIVE}"
KEEP_DAYS="${KEEP_DAYS:-90}"
TAGS="${TAGS:-}"
OPS_DIR="${ROOT}/.OPS/cron_snapshots"
LOCK="${OPS_DIR}/.lock"
TS="$(date '+%Y%m%d_%H%M%S')"
HOST="$(hostname 2>/dev/null || echo unknown)"
TZSTR="$(date +%Z)"
SNAP="${OPS_DIR}/crons_${HOST}_${TS}.txt"
META="${OPS_DIR}/crons_${HOST}_${TS}.meta"
LOG="${OPS_DIR}/cron_snapshots.log"

mkdir -p "${OPS_DIR}"

log(){ echo "[$(date '+%F %T')] $*" | tee -a "$LOG" ; }
with_lock(){
  mkdir -p "$(dirname "$LOCK")"
  if ( set -o noclobber; echo "$$" > "$LOCK") 2>/dev/null; then
    trap 'rm -f "$LOCK"' EXIT INT TERM
  else
    log "[ERR] another run is active: $LOCK"; exit 2
  fi
}

collect(){
  {
    echo "===== SNAPSHOT ${TS} (${TZSTR}) host=${HOST} ====="
    echo "### USER crontab"
    (crontab -l 2>/dev/null || echo "(no user crontab)") | sed 's/^/  /'
    echo
    echo "### SYSTEM /etc/crontab"
    (test -r /etc/crontab && sed 's/^/  /' /etc/crontab) || echo "  (no /etc/crontab)"
    echo
    echo "### /etc/cron.d entries"
    if [ -d /etc/cron.d ]; then
      for f in /etc/cron.d/*; do
        [ -f "$f" ] || continue
        echo "  --- $f ---"
        sed 's/^/    /' "$f"
      done
    else
      echo "  (no /etc/cron.d)"
    fi
    echo
    echo "### systemd timers (if available)"
    if command -v systemctl >/dev/null 2>&1; then
      systemctl list-timers --all 2>/dev/null | sed 's/^/  /' || true
    else
      echo "  (systemd not available)"
    fi
    echo "===== END SNAPSHOT ${TS} ====="
  } > "$SNAP"
}

write_meta(){
  # Leave breadcrumbs for future axis ingestion without enforcing schema now.
  # Minimal manifest-like metadata.
  sha="$(sha256sum "$SNAP" | awk '{print $1}')"
  size="$(stat -c%s "$SNAP" 2>/dev/null || wc -c < "$SNAP")"
  {
    echo "file=${SNAP}"
    echo "sha256=${sha}"
    echo "size=${size}"
    echo "host=${HOST}"
    echo "tz=${TZSTR}"
    echo "tags=${TAGS}"
    echo "axis_hint=automation_cron"
    echo "generated_at=$(date -Iseconds)"
  } > "$META"
}

latest_snapshot(){
  ls -1 ${OPS_DIR}/crons_${HOST}_*.txt 2>/dev/null | sort | tail -n 2
}

diff_last(){
  # Show diff between newest and previous snapshot (if any).
  local arr
  mapfile -t arr < <(latest_snapshot)
  if [ "${#arr[@]}" -lt 2 ]; then
    echo "(no previous snapshot to diff)"
    return 0
  fi
  local prev="${arr[0]}" curr="${arr[1]}"
  echo "=== DIFF (prev=$(basename "$prev"), curr=$(basename "$curr")) ==="
  if command -v diff >/dev/null 2>&1; then
    diff -u "$prev" "$curr" || true
  else
    echo "(diff not available)"
  fi
}

purge_old(){
  find "$OPS_DIR" -type f -name "crons_${HOST}_*.txt" -mtime +"$KEEP_DAYS" -print0 \
    | xargs -0 -r rm -f --
  find "$OPS_DIR" -type f -name "crons_${HOST}_*.meta" -mtime +"$KEEP_DAYS" -print0 \
    | xargs -0 -r rm -f --
}

status(){
  echo "ROOT=$ROOT"
  echo "OPS_DIR=$OPS_DIR"
  echo "KEEP_DAYS=$KEEP_DAYS"
  echo
  echo "Snapshots:"
  ls -lh ${OPS_DIR}/crons_${HOST}_*.txt 2>/dev/null || echo "(none)"
}

# Dispatch
case "$MODE" in
  snapshot)
    with_lock
    log "[INFO] snapshot start host=$HOST tz=$TZSTR"
    collect
    write_meta
    log "[INFO] written: $SNAP"
    ;;

  diff)
    diff_last
    ;;

  purge)
    with_lock
    log "[INFO] purge older than ${KEEP_DAYS} days"
    purge_old
    ;;

  status)
    status
    ;;

  *)
    echo "[ERR] MODE must be snapshot|diff|purge|status" >&2 ; exit 1 ;;
esac




