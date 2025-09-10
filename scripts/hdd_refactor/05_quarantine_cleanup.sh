#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="/mnt/h/ARCHIVE"
TRASH="$ROOT/.TRASH"

# 1) 삭제 대신 격리로 옮겼던 파일 중 30일 경과 항목 삭제
find "$TRASH" -type f -mtime +30 -print -delete
find "$TRASH" -type d -empty -delete
