#!/usr/bin/env bash
# 디버그 트레이스 가독성 향상
set -euo pipefail

# 디버깅 시 타임스탬프+PID 포함
export PS4='+ [${EPOCHREALTIME}] $$ ${BASH_SOURCE##*/}:${LINENO}: '
export BASH_XTRACEFD=19
mkdir -p var/logs
exec 19>>var/logs/debug_trace.log
