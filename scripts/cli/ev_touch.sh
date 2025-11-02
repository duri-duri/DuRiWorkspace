#!/usr/bin/env bash
set -euo pipefail
base="var/evolution"
mkdir -p "$base"
ts=$(date +%s)
dir=$(find "$base" -maxdepth 1 -type d -name 'EV-*' -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -1 | awk '{print $2}')
if [ -z "$dir" ]; then
  dir="$base/EV-${ts}-01"
  mkdir -p "$dir"
fi
touch "$dir"
# LATEST 심볼릭 링크 갱신(있으면 최신을 가리키게)
ln -sfn "$(basename "$dir")" "$base/LATEST"
echo "[OK] EV touch: $dir"
