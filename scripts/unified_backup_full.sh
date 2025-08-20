#!/usr/bin/env bash
# 호환성 래퍼: 기존 unified_backup_full.sh → 새로운 duri_backup.sh full
exec "$(dirname "$0")/duri_backup.sh" full "$@"















