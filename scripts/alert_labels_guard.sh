#!/usr/bin/env bash
set -euo pipefail
fail=0
for f in prometheus/rules/*.y*ml; do
  awk -v F="$f" '
    BEGIN { in_alert=0; sev=team=rb=0; bad=0 }
    /^\s*-\s*alert:\s*/ {
      if (in_alert && !(sev && team && rb)) { printf "MISSING labels in %s\n", F; bad=1 }
      in_alert=1; sev=team=rb=0; next
    }
    in_alert && /[[:space:]]severity:[[:space:]]/   { sev=1 }
    in_alert && /[[:space:]]team:[[:space:]]/       { team=1 }
    in_alert && /[[:space:]]runbook_url:[[:space:]]/ { rb=1 }
    END {
      if (in_alert && !(sev && team && rb)) { printf "MISSING labels in %s\n", F; bad=1 }
      if (bad) exit 2
    }
  ' "$f" || fail=1
done
exit $fail
