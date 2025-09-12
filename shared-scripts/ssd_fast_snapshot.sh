#!/usr/bin/env bash
set -euo pipefail
SNAP=${1:-"DuRi_$(date +%F_%H%M)"}
tar -cf - -C ~ DuRiWorkspace | zstd -9 -T0 -o /mnt/i/DURISSD/FAST_RESTORE/$SNAP.tar.zst
echo "[OK] FAST_RESTORE => $SNAP"
