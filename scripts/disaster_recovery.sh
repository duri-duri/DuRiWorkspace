#!/usr/bin/env bash
set -Eeuo pipefail
TS(){ date "+%F %T"; }; log(){ echo "[$(TS)] $*"; }

# 1) 스탬프/토폴로지 우선
PRIMARY_DIR="/mnt/hdd/ARCHIVE/FULL"
[ -f "$PRIMARY_DIR/.topology.json" ] && \
  PRIMARY_DIR="$(jq -r '.chosen // empty' "$PRIMARY_DIR/.topology.json" 2>/dev/null || echo "$PRIMARY_DIR")"

STAMP_FILE="$PRIMARY_DIR/.last_full_backup.txt"
STAMP_NAME=""
if [ -f "$STAMP_FILE" ]; then
  # "YYYY-mm-dd ... FULL__...tar.zst"에서 마지막 필드가 파일명
  STAMP_NAME="$(awk '{print $NF}' "$STAMP_FILE")"
fi

pick_from_stamp() {
  [ -z "$STAMP_NAME" ] && return 1
  local candidate
  # 1순위: PRIMARY 안에서 직방 매칭
  candidate="$PRIMARY_DIR/$STAMP_NAME"
  if [ -f "$candidate" ] && zstd -t "$candidate" >/dev/null 2>&1; then
    echo "$candidate"; return 0
  fi
  # 2순위: 전체 후보에서 이름 매칭
  for d in "$PRIMARY_DIR" "/mnt/usb/두리백업" "/mnt/c/Users/admin/Desktop/두리백업"; do
    candidate="$(find "$d" -type f -name "$STAMP_NAME" -print -quit 2>/dev/null || true)"
    if [ -n "$candidate" ] && zstd -t "$candidate" >/dev/null 2>&1; then
      echo "$candidate"; return 0
    fi
  done
  return 1
}

# 최신 FULL 백업 찾기 (스탬프 우선, mtime 폴백)
file="$(pick_from_stamp || true)"
if [ -z "$file" ]; then
  # 3순위: 종전처럼 mtime 최신으로
  file="$(find /mnt/hdd/ARCHIVE/FULL /mnt/usb/두리백업 /mnt/c/Users/admin/Desktop/두리백업 \
           -type f -name 'FULL__*.tar.zst' -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -1 | cut -d' ' -f2-)"
fi

[ -z "$file" ] && { log "FATAL: no backup found"; exit 1; }

log "Using backup: $file"

# 무결성 검증
if command -v unzstd >/dev/null 2>&1; then
  unzstd -t "$file" && log "DR integrity test OK"
else
  zstd -t -q "$file" && log "DR integrity test OK"
fi

# 백업 정보 출력
log "Backup details:"
log "  File: $file"
log "  Size: $(du -h "$file" | cut -f1)"
log "  Date: $(stat -c %y "$file")"

echo "✅ Disaster recovery check completed successfully"
