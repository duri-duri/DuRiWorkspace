#!/usr/bin/env bash
# HDD 덤프 완료 직후: Desktop 미러(.lnk+sha+log) + USB(DuRiSync) 스테이징
set -Eeuo pipefail
export LC_ALL=C

LOCK="/tmp/.duri_post_backup.lock"
exec 9>"$LOCK" && flock -n 9 || { echo "[ERR] another run"; exit 99; }

# ---- 설정 로드 ----
[ -f /etc/duri/backup.env ] && . /etc/duri/backup.env || true
USB_ROOT="${USB_ROOT:-/mnt/g/DuRiSync}"
DESKTOP_ROOT="${DESKTOP_ROOT:-/mnt/c/Users/admin/Desktop/두리백업}"

ts(){ date '+%F %T'; }
ok(){ echo "[OK ] $*"; }
ng(){ echo "[ERR] $*"; }
info(){ echo "[.. ] $*"; }
sha_of(){ sha256sum "$1" 2>/dev/null | awk '{print $1}'; }

# ---- 덤프 선택 ----
DUMP="${1:-}"
pick_latest_dump(){
  for base in /mnt/d/backup/DAILY /mnt/c/backup/DAILY; do
    [ -d "$base" ] || continue
    timeout 3s bash -c "find '$base' -maxdepth 1 -type f -name 'Dump_*.dump' -printf '%T@ %p\n' 2>/dev/null" \
      | sort -nr | head -1 | awk '{ $1=""; sub(/^ /,""); print }' && return 0
  done; return 1
}
if [ -z "$DUMP" ]; then DUMP="$(pick_latest_dump || true)"; fi
[ -n "$DUMP" ] && [ -f "$DUMP" ] || { ng "dump not found"; exit 2; }
F="$(basename "$DUMP")"

# ---- 날짜 파싱(파일명 우선, 실패시 mtime) ----
if [[ "$F" =~ Dump_([0-9]{8})([0-9]{6})\.dump ]]; then
  Y="${BASH_REMATCH[1]:0:4}"; M="${BASH_REMATCH[1]:4:2}"; D="${BASH_REMATCH[1]:6:2}"
else
  Y="$(date -d "@$(stat -c %Y "$DUMP")" +%Y)"
  M="$(date -d "@$(stat -c %Y "$DUMP")" +%m)"
  D="$(date -d "@$(stat -c %Y "$DUMP")" +%d)"
fi

# ---- Desktop 미러(.lnk + sha256 + log) ----
DESK_DIR="$DESKTOP_ROOT/$Y/$M/$D"; mkdir -p "$DESK_DIR" || true

# sha256: 원본 옆에 이미 있으면 재사용, 없으면 Desktop에 생성
if [ -f "${DUMP}.sha256" ]; then
  cp -n "${DUMP}.sha256" "$DESK_DIR/${F}.sha256" 2>/dev/null || true
else
  sha256sum "$DUMP" > "$DESK_DIR/${F}.sha256"
fi

to_win_path(){ # /mnt/d/foo -> D:\foo
  local p="$1"
  if [[ "$p" =~ ^/mnt/([a-z])/(.*)$ ]]; then
    local drive="${BASH_REMATCH[1]^^}" rest="${BASH_REMATCH[2]//\//\\}"
    printf "%s\n" "${drive}:\\${rest}"
  else printf "%s\n" "$p"; fi
}
WIN_TARGET="$(to_win_path "$DUMP")"
WIN_LNK_DIR="$(to_win_path "$DESK_DIR")"
WIN_LNK_PATH="${WIN_LNK_DIR}\\${F}.lnk"

make_lnk(){ # PowerShell 변수 확장 충돌 방지: env로 넘기기
  local ps='
$target = $env:TARGET
$link   = $env:LINK
$ws = New-Object -ComObject WScript.Shell
$s  = $ws.CreateShortcut($link)
$s.TargetPath = $target
$s.Save()
'
  TARGET="$WIN_TARGET" LINK="$WIN_LNK_PATH" \
  /mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe \
    -NoProfile -NonInteractive -Command "$ps" >/dev/null 2>&1
}

# .lnk 생성 실패 시 심볼릭 링크 폴백
if ! make_lnk; then ln -sf "$DUMP" "$DESK_DIR/$F" 2>/dev/null || true; fi

LOG_MD="$DESK_DIR/backup_log_${Y}${M}${D}_final.md"
{
  echo "# Backup Log ($(ts))"
  echo "- dump: $F"
  echo "- dump_path: $WIN_TARGET"
  echo "- sha256: $(awk '{print $1}' "$DESK_DIR/${F}.sha256" 2>/dev/null || echo 'N/A')"
} > "$LOG_MD"

# ---- USB 스테이징(있으면) ----
copy_verify(){
  local src="$1" dst="$2" ssha="$3" dsha="$4"
  cp -f "$src" "$dst.part" && sync && mv -f "$dst.part" "$dst"
  if [ -f "$ssha" ]; then
    cp -f "$ssha" "$dsha"
    local want have; want="$(awk '{print $1}' "$dsha" 2>/dev/null)"; have="$(sha_of "$dst")"
    [ -n "$want" ] && [ "$want" = "$have" ]
  else
    sha256sum "$dst" > "$dsha"
  fi
}
USB_RC=2
if [ -d "$USB_ROOT" ]; then
  mkdir -p "$USB_ROOT" || true
  SRC="$DUMP"; DST="$USB_ROOT/$F"
  if [ -f "$DST" ]; then
    # 이미 있으면 해시 확인(다르면 갱신)
    want="$( [ -f "$USB_ROOT/${F}.sha256" ] && awk '{print $1}' "$USB_ROOT/${F}.sha256" )"
    have="$(sha_of "$DST")"
    if [ -n "$want" ] && [ "$want" = "$have" ]; then
      USB_RC=0
    else
      copy_verify "$SRC" "$DST" "${SRC}.sha256" "$USB_ROOT/${F}.sha256" && USB_RC=0 || USB_RC=1
    fi
  else
    copy_verify "$SRC" "$DST" "${SRC}.sha256" "$USB_ROOT/${F}.sha256" && USB_RC=0 || USB_RC=1
  fi
fi

RET=0
[ -f "$LOG_MD" ] || RET=$((RET|1))
[ "$USB_RC" -eq 0 ] || RET=$((RET|2))
echo "[RET] $RET (1:mirror fail, 2:usb stage fail)"
exit "$RET"
