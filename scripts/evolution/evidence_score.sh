#!/usr/bin/env bash
set -euo pipefail
ev_dir=$(find var/evolution -maxdepth 1 -type d -name 'EV-*' -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -1 | awk '{print $2}')
[ -n "${ev_dir:-}" ] || { echo "[ERR] bundle dir not found"; exit 1; }
mkdir -p "${ev_dir}/metrics"
summary="${ev_dir}/summary.txt"; : > "$summary"
missing=(); for f in STATE.SHA256SUMS.snapshot SHA256SUMS; do [ -f "${ev_dir}/${f}" ] || missing+=("${f}"); done
anchor_state="PRESENT"; [ -f "${ev_dir}/ANCHOR.SHA256SUMS" ] || anchor_state="MISSING"
echo "anchor_state=${anchor_state}" >> "$summary"
AB_SRC=""; for cand in "${ev_dir}/ab_eval.prom" "var/metrics/ab_eval.prom"; do [ -f "$cand" ] && AB_SRC="$cand" && break; done
if [ -z "$AB_SRC" ]; then echo "[WARN] ab_eval.prom missing" >&2; echo "score_decision=DEFERRED" >> "$summary"; exit 0; fi
# scientific notation support, choose first numeric <=1e3
pval=$(awk '{for(i=1;i<=NF;i++){ if ($i ~ /^-?[0-9]+(\.[0-9]+)?([eE][+-]?[0-9]+)?$/){ if (($i+0)<=1000){ print $i; exit } } }}' "$AB_SRC")
if [ -z "${pval:-}" ]; then echo "[WARN] parse failed" >&2; echo "score_decision=DEFERRED" >> "$summary"; exit 0; fi
echo "ab_p_value=${pval}" > "${ev_dir}/metrics/ab_eval.txt"
[ "${#missing[@]}" -gt 0 ] && echo "invariants_missing=${missing[*]}" >> "$summary"
if [ "$anchor_state" = "MISSING" ]; then echo "score_decision=RECORDED_NOANCHOR" >> "$summary"; else echo "score_decision=RECORDED" >> "$summary"; fi
echo "[OK] score: ${ev_dir} (p=${pval}, anchor=${anchor_state})"
