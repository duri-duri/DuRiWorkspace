#!/usr/bin/env bash
set -euo pipefail
fail=0
for f in prometheus/rules/*.y*ml; do
  if grep -q '^- alert:' "$f"; then
    if ! egrep -q "severity:|team:|runbook_url:" "$f"; then
      echo "MISSING labels in $f"
      fail=1
    fi
  fi
done
exit $fail
