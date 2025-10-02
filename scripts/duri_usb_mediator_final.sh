#!/usr/bin/env bash
set -Eeuo pipefail
# G:\DuRiSync 의 Dump_*.dump 를 E/F 콜드 저장소로 동기화
# - 미반영분은 다음 실행 시 재시도
# - E/F 양쪽 완료된 오래된 덤프는 USB에서 보존개수(N) 외 정리
set -Eeuo pipefail
export LC_ALL=C

[ -f /etc/duri/backup.env ] && . /etc/duri/backup.env 2>/dev/null || true
USB_ROOT="${USB_ROOT:-/mnt/usb/두리백업}"
E_ROOT="${E_ROOT:-/mnt/e/DuRiSafe_HOSP/DAILY}"
F_ROOT="${F_ROOT:-/mnt/f/DuRiSafe_HOME/DAILY}"
RETAIN_COUNT="${RETAIN_COUNT:-3}"
LOG_DIR="${LOG_DIR:-$HOME/.local/var/log/duri_cold_import}"; mkdir -p "$LOG_DIR" || true
LOCK="/tmp/.duri_usb_mediator.lock"
exec 9>"$LOCK" && flock -n 9 || { echo "[ERR] another run"; exit 99; }

ts(){ date '+%F %T'; }
ok(){ echo "[OK ] $*"; }
ng(){ echo "[ERR] $*"; }
info(){ echo "[.. ] $*"; }
sha_of(){ sha256sum "$1" 2>/dev/null | awk '{print $1}'; }

[ -d "$USB_ROOT" ] || { ng "USB not found: $USB_ROOT"; exit 2; }

TARGETS=()
[ -d "$E_ROOT" ] && TARGETS+=("$E_ROOT|E")
[ -d "$F_ROOT" ] && TARGETS+=("$F_ROOT|F")
[ ${#TARGETS[@]} -gt 0 ] || info "no cold targets mounted (E/F) — will only wait/backlog"

list_dumps(){
  find "$USB_ROOT" -maxdepth 1 -type f -name 'Dump_*.dump' -printf '%T@ %f\n' 2>/dev/null \
    | sort -n | awk '{print $2}'
}
mark_done(){ : > "$USB_ROOT/$1.delivered.$2" 2>/dev/null || true; }
is_done(){ [ -f "$USB_ROOT/$1.delivered.$2" ]; }

copy_verify(){
  local src="$1" dst="$2" ssha="$3" dsha="$4"
  cp -f "$src" "$dst.part" && sync && mv -f "$dst.part" "$dst"
  if [ -f "$ssha" ]; then
    cp -f "$ssha" "$dsha"
    local want have; want="$(awk '{print $1}' "$dsha" 2>/dev/null)"; have="$(sha_of "$dst")"
    [ -n "$want" ] && [ "$want" = "$have" ] || return 10
  else
    sha256sum "$dst" > "$dsha"
  fi
  return 0
}

sync_one_target(){
  local dst_root="$1" tag="$2"; mkdir -p "$dst_root" || true
  local cnt_new=0 cnt_skip=0 cnt_upd=0
  while IFS= read -r F; do
    local src="$USB_ROOT/$F" dst="$dst_root/$F" ssha="$src.sha256" dsha="$dst.sha256"
    if [ -f "$dst" ] && [ -f "$dsha" ]; then
      local want have; want="$(awk '{print $1}' "$dsha" 2>/dev/null)"; have="$(sha_of "$dst")"
      if [ -n "$want" ] && [ "$want" = "$have" ]; then
        is_done "$F" "$tag" || mark_done "$F" "$tag"
        cnt_skip=$((cnt_skip+1)); continue
      fi
    fi
    if copy_verify "$src" "$dst" "$ssha" "$dsha"; then
      if is_done "$F" "$tag"; then cnt_upd=$((cnt_upd+1)); else cnt_new=$((cnt_new+1)); fi
      mark_done "$F" "$tag"
      echo "[$(ts)] import $F -> $dst_root OK ($tag)" >> "$LOG_DIR/$(date +%Y%m%d).log"
    else
      ng "copy/verify failed: $F -> $dst_root"
    fi
  done < <(list_dumps)
  ok "target=$tag new=$cnt_new updated=$cnt_upd skipped=$cnt_skip"
}

prune_usb_when_done(){
  mapfile -t ALL < <(list_dumps | tac) # 최신 -> 오래된
  local kept=0
  for F in "${ALL[@]}"; do
    if [ -f "$USB_ROOT/$F.delivered.E" ] && [ -f "$USB_ROOT/$F.delivered.F" ]; then
      kept=$((kept+1))
      if [ "$kept" -le "$RETAIN_COUNT" ]; then continue; fi
      rm -f "$USB_ROOT/$F" "$USB_ROOT/$F.sha256" \
            "$USB_ROOT/$F.delivered.E" "$USB_ROOT/$F.delivered.F" 2>/dev/null || true
      echo "[$(ts)] prune USB $F" >> "$LOG_DIR/$(date +%Y%m%d).log"
    fi
  done
}

for T in "${TARGETS[@]}"; do IFS="|" read -r ROOT TAG <<<"$T"; sync_one_target "$ROOT" "$TAG"; done
prune_usb_when_done
ok "USB mediator finished"
