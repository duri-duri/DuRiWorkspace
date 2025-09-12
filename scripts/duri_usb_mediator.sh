#!/usr/bin/env bash
# G:\DuRiSync 의 Dump_*.dump 를 E/F 콜드 저장소로 동기화
# - 미반영분은 다음 실행 시 계속 재시도
# - E/F 양쪽 완료된 오래된 덤프는 USB에서 보존개수(N) 외 정리
set -Eeuo pipefail
export LC_ALL=C

# ==== 설정 ====
USB_ROOT="/mnt/g/DuRiSync"
E_ROOT="/mnt/e/DuRiSafe_HOSP/DAILY"
F_ROOT="/mnt/f/DuRiSafe_HOME/DAILY"
LOG_DIR="/var/log/duri_cold_import"
RETAIN_COUNT="${RETAIN_COUNT:-3}"   # USB에 완료된 덤프 보존 개수
LOCK="/tmp/.duri_usb_mediator.lock"

# ==== 공용 ====
exec 9>"$LOCK" && flock -n 9 || { echo "[ERR] another run"; exit 99; }
ts(){ date '+%F %T'; }
ok(){ echo "[OK ] $*"; }
ng(){ echo "[ERR] $*"; }
info(){ echo "[.. ] $*"; }
sha_of(){ sha256sum "$1" 2>/dev/null | awk '{print $1}'; }
mkdir -p "$LOG_DIR"

require_usb(){ [ -d "$USB_ROOT" ] || { ng "USB not found: $USB_ROOT"; exit 2; }; }

targets_present(){
  TARGETS=()
  mountpoint -q /mnt/e && [ -d "$E_ROOT" ] && TARGETS+=("$E_ROOT|E")
  mountpoint -q /mnt/f && [ -d "$F_ROOT" ] && TARGETS+=("$F_ROOT|F")
  [ ${#TARGETS[@]} -gt 0 ] || info "no cold targets mounted (E/F) — will only mark backlog and exit"
}

list_dumps(){
  # 오래된 것부터 처리(백로그 먼저 해소)
  find "$USB_ROOT" -maxdepth 1 -type f -name 'Dump_*.dump' -printf '%T@ %f\n' 2>/dev/null \
    | sort -n | awk '{print $2}'
}

mark_done(){ touch "$USB_ROOT/$1.delivered.$2" 2>/dev/null || true; }
is_done(){ [ -f "$USB_ROOT/$1.delivered.$2" ]; }

copy_verify(){
  local src="$1" dst="$2" sha_src="$3" sha_dst="$4"
  cp -f "$src" "$dst.part"
  sync
  mv -f "$dst.part" "$dst"
  if [ -f "$sha_src" ]; then
    cp -f "$sha_src" "$sha_dst"
    local want have; want="$(awk '{print $1}' "$sha_dst" 2>/dev/null)"; have="$(sha_of "$dst")"
    [ -n "$want" ] && [ "$want" = "$have" ] || { ng "sha mismatch: $(basename "$dst")"; return 10; }
  else
    sha256sum "$dst" > "$sha_dst"
  fi
  return 0
}

sync_one_target(){
  local dst_root="$1" tag="$2"
  mkdir -p "$dst_root"
  local cnt_new=0 cnt_skip=0 cnt_upd=0

  while IFS= read -r F; do
    local src="$USB_ROOT/$F"
    local dst="$dst_root/$F"
    local ssha="$src.sha256"
    local dsha="$dst.sha256"

    # 이미 타깃에 있고 해시가 일치하면 바로 완료마크 후 스킵
    if [ -f "$dst" ] && [ -f "$dsha" ]; then
      local want have; want="$(awk '{print $1}' "$dsha" 2>/dev/null)"; have="$(sha_of "$dst")"
      if [ -n "$want" ] && [ "$want" = "$have" ]; then
        is_done "$F" "$tag" || mark_done "$F" "$tag"
        cnt_skip=$((cnt_skip+1)); continue
      fi
    fi

    # USB에 있는 덤프를 타깃으로 복사/검증
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
  # 둘 다 완료(delivered.E && delivered.F)인 파일들 중,
  # 최신 RETAIN_COUNT개만 남기고 더 오래된 것 제거
  mapfile -t ALL < <(list_dumps | tac) # 최신 -> 오래된
  local kept=0
  for F in "${ALL[@]}"; do
    if [ -f "$USB_ROOT/$F.delivered.E" ] && [ -f "$USB_ROOT/$F.delivered.F" ]; then
      kept=$((kept+1))
      if [ "$kept" -le "$RETAIN_COUNT" ]; then continue; fi
      # 제거 후보(덤프+sha+마커)
      rm -f "$USB_ROOT/$F" "$USB_ROOT/$F.sha256" \
            "$USB_ROOT/$F.delivered.E" "$USB_ROOT/$F.delivered.F" 2>/dev/null || true
      echo "[$(ts)] prune USB $F" >> "$LOG_DIR/$(date +%Y%m%d).log"
    fi
  done
}

main(){
  require_usb
  targets_present

  # 1) 마운트되어 있는 모든 타깃(E/F)에 대해 미반영분부터 반영
  for T in "${TARGETS[@]}"; do
    IFS="|" read -r ROOT TAG <<<"$T"
    sync_one_target "$ROOT" "$TAG"
  done

  # 2) 보존 정책: E/F 모두 완료된 것만 정리(최신 RETAIN_COUNT 개 유지)
  prune_usb_when_done

  ok "USB mediator finished"
}

main "$@"
