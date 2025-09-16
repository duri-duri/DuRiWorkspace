#!/usr/bin/env bash
set -Eeuo pipefail
TS(){ date "+%F %T"; }; log(){ echo "[$(TS)] $*"; }

# SSOT에서 목적지 읽기
_read_topology() {
  local cfg="configs/backup_topology.yml"
  [ -f "$cfg" ] || { printf '%s\n' "/mnt/hdd/ARCHIVE/FULL" "/mnt/usb/두리백업" "/mnt/c/Users/admin/Desktop/두리백업"; return; }
  awk '/primary:/{print $2} /secondary:/{print $2} /tertiary:/{print $2}' "$cfg"
}

# 실제 쓰기 가능한 첫 번째 목적지 찾기
_first_writable(){
  for d in "$@"; do
    mkdir -p "$d" 2>/dev/null || true
    t="$d/.w.$$"
    ( : >"$t" && rm -f "$t" ) 2>/dev/null && { printf '%s\n' "$d"; return 0; }
  done
  return 1
}

# 목적지 선택 (stdout 누출 방지)
choose_dest(){
  mapfile -t cand < <(_read_topology)
  DEST="$(_first_writable "${cand[@]}")" || { log "FATAL: no writable destination"; exit 1; }
  echo "$DEST" > /tmp/backup.dest.$$; printf '%s\n' "${cand[@]}" > /tmp/backup.cand.$$
  echo "$DEST"
}

# 목적지 스탬프 생성 (원자적 쓰기)
stamp_dest(){
  local d="$1" name="$2" t="$(date '+%F %T')"
  
  # .last_full_backup.txt 원자적 쓰기
  printf '%s %s %s %s\n' "$t" "$(hostname)" "$(whoami)" "$name" > "$d/.last_full_backup.txt.tmp" \
    && mv "$d/.last_full_backup.txt.tmp" "$d/.last_full_backup.txt" \
    || { log "[WARN] .last_full_backup.txt 쓰기 실패"; return 1; }
  
  # .topology.json 원자적 쓰기
  if command -v jq >/dev/null 2>&1; then
    jq -n --arg chosen "$d" \
          --argjson cands "$(printf '%s\n' "${cand[@]}" | jq -R . | jq -s .)" \
          --arg reason "writable" \
          '{chosen:$chosen,candidates:$cands,reason:$reason,ts:now}' \
      > "$d/.topology.json.tmp" 2>/dev/null \
      && mv "$d/.topology.json.tmp" "$d/.topology.json" \
      || { log "[WARN] jq JSON 생성 실패, 폴백 사용"; 
           echo '{"chosen":"'"$d"'","reason":"writable","ts":"'"$t"'"}'> "$d/.topology.json.tmp" \
           && mv "$d/.topology.json.tmp" "$d/.topology.json"; }
  else
    echo '{"chosen":"'"$d"'","reason":"writable","ts":"'"$t"'"}'> "$d/.topology.json.tmp" \
      && mv "$d/.topology.json.tmp" "$d/.topology.json" \
      || { log "[WARN] .topology.json 쓰기 실패"; return 1; }
  fi
  
  log "✅ 스탬프 생성 완료: $d"
  return 0
}
