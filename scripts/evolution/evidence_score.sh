#!/usr/bin/env bash
set -euo pipefail
ev_dir=$(find var/evolution -maxdepth 1 -type d -name 'EV-*' -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -1 | awk '{print $2}')
[ -n "${ev_dir:-}" ] || { echo "[ERR] bundle dir not found"; exit 1; }
core_missing=()
for f in ANCHOR.SHA256SUMS STATE.SHA256SUMS.snapshot SHA256SUMS; do
  [ -f "${ev_dir}/${f}" ] || core_missing+=("${f}")
done
comp_json=$(ls "${ev_dir}"/evolution.*.jsonl 2>/dev/null | head -1 || true)
[ -n "${comp_json}" ] || core_missing+=("evolution.*.jsonl")
if [ ${#core_missing[@]} -gt 0 ]; then echo "[ERR] core invariants missing: ${core_missing[*]}"; exit 1; fi
AB_SRC=""; for cand in "${ev_dir}/ab_eval.prom" "var/metrics/ab_eval.prom"; do [ -f "$cand" ] && AB_SRC="$cand" && break; done
mkdir -p "${ev_dir}/metrics"
if [ -z "$AB_SRC" ]; then echo "[WARN] ab_eval.prom missing (score DEFERRED)"; echo "score_decision=DEFERRED" >> "${ev_dir}/summary.txt"; exit 0; fi
pval=$(awk '{for(i=1;i<=NF;i++) if ($i ~ /^[0-9]*\.?[0-9]+$/){print $i; exit}}' "$AB_SRC")
if [ -z "${pval:-}" ]; then echo "[WARN] parse failed (score DEFERRED)"; echo "score_decision=DEFERRED" >> "${ev_dir}/summary.txt"; exit 0; fi
echo "ab_p_value=${pval}" > "${ev_dir}/metrics/ab_eval.txt"
echo "score_decision=RECORDED" >> "${ev_dir}/summary.txt"
echo "[OK] score: ${ev_dir} (p=${pval})"
