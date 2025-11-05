#!/usr/bin/env bash
# L4 Daily Runner (with lock and logging)
# Purpose: Wrapper for l4_daily_observation.sh with flock lock and logging
# Usage: Called by systemd timer

set -euo pipefail

cd /home/duri/DuRiWorkspace

mkdir -p var/audit/logs

exec 9>var/audit/.l4_daily.lock
flock -n 9 || { echo "[skip] already running"; exit 0; }

ts=$(date +%Y%m%d_%H%M%S)

bash scripts/ops/l4_daily_observation.sh 2>&1 | tee "var/audit/logs/daily_${ts}.log"

exit 0

