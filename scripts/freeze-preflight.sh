#!/usr/bin/env bash
set -euo pipefail
git fetch -q origin main
git diff --name-only origin/main...HEAD \
| grep -Ev -f <(awk 'NF && $0 !~ /^#/' .github/freeze-allow.txt | sed 's/\r$//') \
|| true
