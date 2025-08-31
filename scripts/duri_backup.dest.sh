#!/usr/bin/env bash
set -Eeuo pipefail
TS(){ date "+%F %T"; }; log(){ echo "[$(TS)] $*"; }

# SSOT에서 목적지 읽기
_read_topology() {
  local cfg="configs/backup_topology.yml"
  [ -f "$cfg" ] || { echo "/mnt/usb/두리백업 /mnt/c/Users/admin/Desktop/두리백업"; return; }
  awk '/primary:/{print $2} /secondary:/{print $2} /tertiary:/{print $2}' "$cfg"
}

# 실제 쓰기 가능한 첫 번째 목적지 찾기
_first_writable(){ 
  for d in "$@"; do 
    mkdir -p "$d" 2>/dev/null || true
    t="$d/.w.$$"
    ( : >"$t" && rm -f "$t" ) 2>/dev/null && { echo "$d"; return 0; }
  done
  return 1
}

# 목적지 선택
choose_dest(){
  mapfile -t cand < <(_read_topology)
  DEST="$(_first_writable "${cand[@]}")" || { log "FATAL: no writable destination"; exit 1; }
  echo "$DEST"
}

# 목적지 스탬프 생성
stamp_dest(){
  local dest="$1" name="$2"
  echo "$(TS) $HOSTNAME $USER $name" >> "$dest/.last_full_backup.txt"
  printf '{ "chosen":"%s","candidates":[%s],"reason":"writable"}\n' "$dest" "$(printf '"%s",' "${cand[@]}" | sed 's/,$//')" > "$dest/.topology.json"
}
