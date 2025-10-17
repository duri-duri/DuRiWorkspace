#!/usr/bin/env bash
set -euo pipefail
LOG=/var/log/duri/cron.log
MAX=$((50*1024*1024))   # 50MB
[ -f "$LOG" ] || exit 0
SZ=$(stat -c%s "$LOG" 2>/dev/null || echo 0)
if [ "$SZ" -ge "$MAX" ]; then
  ts=$(date +%F_%H%M%S)
  mv "$LOG" "/var/log/duri/cron.$ts.log"
  gzip -f "/var/log/duri/cron.$ts.log" || true
fi
find /var/log/duri -name "cron.*.log.gz" -mtime +14 -delete 2>/dev/null || true
