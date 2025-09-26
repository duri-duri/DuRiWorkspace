#!/usr/bin/env bash
set -Eeuo pipefail
bash scripts/duri_backup.sh --mode full --verify-only
docker compose down
docker compose up -d
bash tools/smoke.sh
echo "BACKUP/RESTORE OK"
