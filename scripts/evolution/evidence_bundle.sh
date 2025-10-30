#!/usr/bin/env bash
set -euo pipefail
ts="$(date -u +%Y%m%d-%H%M%S)"
# add 2-digit random suffix to avoid ID collisions within the same second
rnd=$(awk 'BEGIN{srand(); printf "%02d", int(rand()*100)}')
ev_dir="var/evolution/EV-${ts}-${rnd}"
mkdir -p "$ev_dir"
[ -f var/ANCHOR/SHA256SUMS ] && cp -a var/ANCHOR/SHA256SUMS "$ev_dir/ANCHOR.SHA256SUMS" || true
[ -f var/STATE.SHA256SUMS.snapshot ] && cp -a var/STATE.SHA256SUMS.snapshot "$ev_dir/STATE.SHA256SUMS.snapshot" || true
mkdir -p var/events; [ -f var/events/evolution.jsonl ] || touch var/events/evolution.jsonl
if command -v jq >/dev/null 2>&1; then
  echo '{}' | jq -c --arg ts "$(date -Iseconds -u)" --arg cyc "EV-${ts}" '{ts:$ts,cycle_id:$cyc}' >> var/events/evolution.jsonl
else
  echo "{\"ts\":\"$(date -Iseconds -u)\",\"cycle_id\":\"EV-${ts}\"}" >> var/events/evolution.jsonl
fi
tail -n 50 var/events/evolution.jsonl > "$ev_dir/evolution.EV-${ts}.jsonl"
[ -f var/metrics/ab_eval.prom ] && cp var/metrics/ab_eval.prom "$ev_dir/ab_eval.prom" || true
( cd "$ev_dir" && find . -maxdepth 1 -type f -printf "%P\n" | sort | xargs -r sha256sum > SHA256SUMS )
echo "[OK] bundle: $ev_dir"

# Update latest pointer
ln -sfn "$(realpath --relative-to=var/evolution "$ev_dir")" var/evolution/LATEST || true
