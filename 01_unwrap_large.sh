#!/usr/bin/env bash
set -Eeuo pipefail
ARCH="/mnt/h/ARCHIVE"
WRK="$ARCH/.UNWRAP"; OUT="$WRK/extracted/FIRST"
LOG="$WRK/logs/unwrap_large_$(date +%Y-%m-%d_%H%M%S).log"
MIN="+1G" ; mkdir -p "$OUT" "$WRK/logs"

echo "[START] unwrap >=1GB" | tee -a "$LOG"

# 작업/격리 영역은 제외
find "$ARCH" -type d \( -path "$WRK" -o -path "$ARCH/.TRASH" -o -path "$ARCH/.QUAR_FAIL" \) -prune -false -o \
     -type f -size "$MIN" -regextype posix-extended \
     -iregex '.*\.(tar\.zst|tar\.gz|tgz|tar|zip|7z)$' -print0 |
while IFS= read -r -d '' F; do
  base="$(basename "$F")"; name="${base%.*}"
  dst="$OUT/$name"; ok="$dst/.ok"; tmp="$dst.tmp.$$"
  [[ -f "$ok" ]] && { echo "[SKIP] $F"; continue; }
  mkdir -p "$tmp"
  trap 'rm -rf "$tmp"' ERR
  case "$F" in
    *.tar.zst) tar -I zstd -xf "$F" -C "$tmp" ;;
    *.tar.gz|*.tgz) tar -xzf "$F" -C "$tmp" ;;
    *.tar) tar -xf "$F" -C "$tmp" ;;
    *.zip)  7z x -y -o"$tmp" "$F" >/dev/null ;;
    *.7z)   7z x -y -o"$tmp" "$F" >/dev/null ;;
    *) echo "[WARN] unsupported: $F" | tee -a "$LOG"; rm -rf "$tmp"; continue ;;
  esac
  mv "$tmp" "$dst" && touch "$ok"
  echo "[UNWRAP] $F -> $dst" | tee -a "$LOG"
done

echo "[DONE] unwrap >=1GB -> $LOG"
