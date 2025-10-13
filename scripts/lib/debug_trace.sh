#!/usr/bin/env bash
# 디버그 트레이스 가독성 향상
set -euo pipefail

# 디버깅 시 타임스탬프+PID 포함
export PS4='+ [${EPOCHREALTIME}] $$ ${BASH_SOURCE##*/}:${LINENO}: '

# BASH_XTRACEFD 안전 가드
if [[ -n "${BASH_XTRACEFD:-}" && "${BASH_XTRACEFD:-}" =~ ^[0-9]+$ ]]; then
  : # 유효하면 그대로 사용
else
  # 자체 fd 열기 (repo_root 함수 사용 가능한 경우만)
  if command -v repo_root >/dev/null 2>&1; then
    LOG_DIR="$(repo_root)/var/logs"
  else
    LOG_DIR="var/logs"
  fi
  mkdir -p "$LOG_DIR"
  exec {__tracefd}>>"$LOG_DIR/trace.log"
  export BASH_XTRACEFD=$__tracefd
fi
