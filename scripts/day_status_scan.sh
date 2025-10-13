#!/usr/bin/env bash
set -euo pipefail
rng_start=${1:-40}; rng_end=${2:-60}
out=".reports/day_status_${rng_start}_${rng_end}.tsv"
mkdir -p .reports

echo -e "day\tgit_tag\tgit_branch\tcompletion_report\tverify_jsons" > "$out"
for d in $(seq "$rng_start" "$rng_end"); do
  tag_ok=$(git tag | grep -E "^day${d}\b|v0\.1.*-day${d}\b" || true)
  br_ok=$(git branch -a | grep -E "day${d}\b" || true)
  rep_ok=$(ls DuRi_Day11_15_starter/DAY${d}_COMPLETION_REPORT.md 2>/dev/null || true)
  ver_ok=$(ls DuRi_Day11_15_starter/verify_out/day_${d}.json 2>/dev/null || true)
  echo -e "${d}\t${tag_ok:+yes}\t${br_ok:+yes}\t${rep_ok:+yes}\t${ver_ok:+yes}" >> "$out"
done
echo "Wrote $out"
