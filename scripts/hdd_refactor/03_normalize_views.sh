#!/usr/bin/env bash
set -Eeuo pipefail
CANON="/mnt/h/ARCHIVE"
IDX="$CANON/META/sha256_index.tsv"
mkdir -p "$CANON/FULL" "$CANON/INCR" "$CANON/CORE"

awk -F'\t' '{print $3}' "$IDX" \
| while read -r path; do
  base=$(basename "$path")
  case "$base" in
    FULL__*.tar.*) dest="$CANON/FULL/$base" ;;
    INCR__*.tar.*) dest="$CANON/INCR/$base" ;;
    CORE__*.tar.*) dest="$CANON/CORE/$base" ;;
    *) continue ;;
  esac
  mkdir -p "$(dirname "$dest")"
  dev_src=$(df -P "$path" | tail -1 | awk '{print $1}')
  dev_dst=$(df -P "$(dirname "$dest")" | tail -1 | awk '{print $1}')
  if [[ "$dev_src" == "$dev_dst" ]]; then ln -f "$path" "$dest"; else ln -sfn "$path" "$dest"; fi
done
