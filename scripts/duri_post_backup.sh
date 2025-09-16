#!/usr/bin/env bash
set -Eeuo pipefail
export LC_ALL=C

LOCK="/tmp/.duri_post_backup.lock"
exec 9>"$LOCK" && flock -n 9 || { echo "[ERR] another run"; exit 99; }

ts(){ date '+%F %T'; }
ok(){ echo "[OK ] $*"; }
ng(){ echo "[ERR] $*"; }
info(){ echo "[.. ] $*"; }

DUMP="${1:-}"
pick_latest_dump(){
  for base in /mnt/d/backup/DAILY /mnt/c/backup/DAILY; do
    [ -d "$base" ] || continue
    timeout 3s bash -c "ls -1t \"$base\"/Dump_*.dump 2>/dev/null | head -1" | tail -n1 && return 0
  done; return 1
}
if [ -z "$DUMP" ]; then DUMP="$(pick_latest_dump || true)"; fi
[ -n "$DUMP" ] && [ -f "$DUMP" ] || { ng "dump not found"; exit 2; }
F="$(basename "$DUMP")"

# 날짜 파싱
if [[ "$F" =~ Dump_([0-9]{8})([0-9]{6})\.dump ]]; then
  Y="${BASH_REMATCH[1]:0:4}"; M="${BASH_REMATCH[1]:4:2}"; D="${BASH_REMATCH[1]:6:2}"
else
  Y="$(date -d "@$(stat -c %Y "$DUMP")" +%Y)"; M="$(date -d "@$(stat -c %Y "$DUMP")" +%m)"; D="$(date -d "@$(stat -c %Y "$DUMP")" +%d)"
fi

# --- 데스크탑 미러 ---
DESK_DIR="/mnt/c/Users/admin/Desktop/두리백업/$Y/$M/$D"; mkdir -p "$DESK_DIR" || true
if [ -f "${DUMP}.sha256" ]; then cp -n "${DUMP}.sha256" "$DESK_DIR/${F}.sha256" || true
else sha256sum "$DUMP" > "$DESK_DIR/${F}.sha256"; fi

to_win_path(){ if [[ "$1" =~ ^/mnt/([a-z])/(.*)$ ]]; then echo "${BASH_REMATCH[1]^^}:\\"${BASH_REMATCH[2]//\//\\}; else echo "$1"; fi; }
WIN_TARGET="$(to_win_path "$DUMP")"; WIN_LNK_DIR="$(to_win_path "$DESK_DIR")"; WIN_LNK_PATH="${WIN_LNK_DIR}\\${F}.lnk"
make_lnk(){ /mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile -NonInteractive -Command "\$ws=New-Object -ComObject WScript.Shell; \$s=\$ws.CreateShortcut('$WIN_LNK_PATH'); \$s.TargetPath='$WIN_TARGET'; \$s.Save()" >/dev/null 2>&1; }
if ! make_lnk; then ln -sf "$DUMP" "$DESK_DIR/$F" || true; fi
LOG_MD="$DESK_DIR/backup_log_${Y}${M}${D}_final.md"
{ echo "# Backup Log $(ts)"; echo "- dump: $F"; echo "- dump_path: $WIN_TARGET"; echo "- sha256: $(awk '{print $1}' "$DESK_DIR/${F}.sha256" 2>/dev/null || echo N/A)"; } > "$LOG_MD"
ok "desktop mirror -> $DESK_DIR"

# --- USB export: 오직 G만 ---
USB_RC=2
sudo mkdir -p /mnt/g >/dev/null 2>&1 || true
mountpoint -q /mnt/g || sudo mount -t drvfs G: /mnt/g >/dev/null 2>&1 || true
if [ -d /mnt/g/DuRiSync ] && [ -x /mnt/c/Users/admin/Desktop/usb_incremental_sync.sh ]; then
  if /mnt/c/Users/admin/Desktop/usb_incremental_sync.sh export >/dev/null 2>&1; then ok "USB_EXPORT_OK (/mnt/g/DuRiSync)"; USB_RC=0; else ng "USB_EXPORT_FAIL"; USB_RC=1; fi
else
  info "USB(G) not present → skip"; USB_RC=2
fi

RET=0; [ -f "$LOG_MD" ] || RET=$((RET|1)); [ "$USB_RC" -eq 0 ] || RET=$((RET|2))
echo "[RET] $RET (1:mirror fail, 2:usb fail)"; exit "$RET"