#!/usr/bin/env bash
# 하드닝 #1: find -newermt 인용 문제 해결 (함수로 고정)
set -euo pipefail

win="${1:-2 hours}"

find var/evolution -type f -name 'ab_eval.prom' -newermt "-${win}" \
  ! -path '*-SYN*/ab_eval.prom' -print0 \
| xargs -0 awk '/^duri_ab_p_value{/{print $NF}' \
| sort -u | wc -l

