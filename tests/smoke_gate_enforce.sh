#!/usr/bin/env bash
set -euo pipefail

echo "🧪 Enforce: 운영 p@3 > 0"
SEARCH=scripts/rag_search_fusion_v1.sh THRESH_P=0.01 bash scripts/rag_gate_day62.sh >/tmp/g1.out
grep -q 'micro precision@3 = 0\.0000' /tmp/g1.out && { echo "❌ p@3==0"; exit 1; }
echo "✅ 운영 p@3 > 0"

echo "🧪 Enforce: 클린 p@3 ≥ 0.45"
SEARCH=scripts/rag_search_fusion.sh THRESH_P=0.45 PRE_K=20 RRF_K=10 \
  bash scripts/rag_gate.sh .reports/day62/ground_truth_clean.tsv >/tmp/g2.out
grep -q 'micro_p@3=0\.4[0-4][0-9]' /tmp/g2.out && { echo "❌ p@3<0.45"; exit 1; }
echo "✅ 클린 p@3 ≥ 0.45"
