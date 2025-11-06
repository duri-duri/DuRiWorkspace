#!/usr/bin/env bash
# Atomic Write Helper - 원자적 파일 쓰기
# Purpose: 파일 쓰기를 원자적으로 수행 (tmp -> rename)
# Usage: atomic_write <dst_file> < content

set -euo pipefail

dst="$1"
tmp="${dst}.tmp"

# stdin을 임시 파일에 쓰기
cat > "$tmp"

# 원자적 이동
mv -f "$tmp" "$dst"

# 디렉터리 fsync (rename 내구성 보장)
if [[ -f "${WORK}/scripts/ops/inc/_fsync_dir.py" ]]; then
  python3 "${WORK}/scripts/ops/inc/_fsync_dir.py" "$(dirname "$dst")" 2>/dev/null || true
fi

exit 0

