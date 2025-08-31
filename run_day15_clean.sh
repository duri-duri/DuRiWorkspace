#!/usr/bin/env bash
set -euo pipefail

export ROOT="$HOME/DuRiWorkspace"
export POLICY="$ROOT/policies/auto_code_loop/gate_policy.yaml"

# Git/쉘 환경을 안전하게 고정
export GIT_TERMINAL_PROMPT=0
export GIT_OPTIONAL_LOCKS=0
export PS1="$ "
export PS4="+ "

# shim을 PATH 최우선에 둠
PATH="/tmp/gitshim:$PATH"

# 완전한 청정 셸에서 실행 + 디버그 로그 남기기
env -i HOME="$HOME" PATH="$PATH" TERM="$TERM" \
  bash --noprofile --norc -c '
    set -euo pipefail
    cd "$HOME/DuRiWorkspace"
    bash -x tools/auto_code_loop_beta.sh
  ' |& tee -a "$ROOT/logs/auto_code_loop_beta/$(date +%F)/run.debug"
