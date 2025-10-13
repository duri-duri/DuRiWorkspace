#!/usr/bin/env bash
set -euo pipefail
fail=0
for d in $(seq 1 30); do
  f="DuRi_Day11_15_starter/verify_out/day_${d}.json"
  if [[ ! -f "$f" ]] || [[ "$(jq -r '.status' "$f")" != "ok" ]]; then
    echo "Phase1 guard FAIL: Day $d not ok"
    fail=1
  fi
done
exit $fail
