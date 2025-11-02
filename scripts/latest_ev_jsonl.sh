#!/usr/bin/env bash
set -euo pipefail
EV=$(find var/evolution -maxdepth 1 -type d -name "EV-*" -printf "%T@ %p\n" 2>/dev/null | sort -nr | head -1 | awk '{print $2}')
[ -z "$EV" ] && { echo "[INFO] EV 없음"; exit 0; }
echo "LATEST_EV=$EV"
find "$EV" -maxdepth 1 -name "evolution.*.jsonl" -exec ls -lt {} \; 2>/dev/null | head -1 || echo "[INFO] JSONL 파일 없음"
