#!/usr/bin/env bash
# With Lock Helper - 파일 락을 사용한 명령 실행
# Purpose: 파일 락을 사용하여 동시 실행 방지
# Usage: with_lock <lock_file> <cmd...>

set -euo pipefail

lock="$1"
shift

# 락 파일 디렉터리 생성
mkdir -p "$(dirname "$lock")"

# 파일 디스크립터 9로 락 획득
exec 9>"$lock"

# 10초 타임아웃으로 락 획득 시도
if flock -w 10 9; then
  "$@"
  exit_code=$?
  exec 9>&-
  exit $exit_code
else
  echo "[ERROR] Failed to acquire lock: $lock" >&2
  exit 1
fi

