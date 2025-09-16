#!/usr/bin/env bash
set -Eeuo pipefail

# 설정
ARCH="/mnt/h/ARCHIVE"
WRK="/mnt/h/ARCHIVE/.UNWRAP/STAGE1"
LOG="$WRK/unwrap_$(date +%Y%m%d_%H%M%S).log"

mkdir -p "$WRK" "$WRK/logs"

log(){ echo "[$(date +%F_%T)] $*" | tee -a "$LOG"; }

log "=== STAGE1: 1GB+ 모든 압축 파일 언랩 시작 ==="

# 1GB 이상 압축 파일들 찾기
find "$ARCH" -type f -size +1G \( -name "*.tar.zst" -o -name "*.tar.gz" -o -name "*.tgz" -o -name "*.tar" -o -name "*.zip" -o -name "*.7z" \) \
  -not -path "$ARCH/.UNWRAP/*" -not -path "$ARCH/.TRASH/*" \
  -print0 | while IFS= read -r -d '' file; do
  
  # 파일 정보 추출
  size=$(stat -c %s "$file")
  mtime=$(stat -c %Y "$file")
  date_str=$(date -d "@$mtime" +%Y%m%d_%H%M%S)
  name=$(basename "$file")
  
  # 날짜별 디렉토리 생성
  date_dir="$WRK/$date_str"
  mkdir -p "$date_dir"
  
  # 언랩
  case "$file" in
    *.tar.zst) 
      tar -I zstd -xf "$file" -C "$date_dir" 
      log "[UNWRAP] $name -> $date_dir (${size} bytes)"
      ;;
    *.tar.gz|*.tgz) 
      tar -xzf "$file" -C "$date_dir"
      log "[UNWRAP] $name -> $date_dir (${size} bytes)"
      ;;
    *.tar) 
      tar -xf "$file" -C "$date_dir"
      log "[UNWRAP] $name -> $date_dir (${size} bytes)"
      ;;
    *.zip) 
      7z x -y -o"$date_dir" "$file" >/dev/null
      log "[UNWRAP] $name -> $date_dir (${size} bytes)"
      ;;
    *.7z) 
      7z x -y -o"$date_dir" "$file" >/dev/null
      log "[UNWRAP] $name -> $date_dir (${size} bytes)"
      ;;
  esac
  
  # 원본 파일 정보 기록
  echo "$file|$size|$mtime|$date_str" >> "$WRK/original_files.txt"
done

log "=== STAGE1 언랩 완료 ==="
log "결과 디렉토리: $WRK"
log "로그 파일: $LOG"











