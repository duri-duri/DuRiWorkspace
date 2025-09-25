#!/usr/bin/env bash
set -euo pipefail
PROM="${PROMETHEUS_URL:-http://prometheus:9090}"
fail() { echo "::error::$1"; exit 1; }

# 최근 10분 핵심 지표 체크
evidence_low=$(curl -s "$PROM/api/v1/query" \
  --data-urlencode 'query=(sum(rate(rag_evidence_attach_total{status="miss"}[10m])) / sum(rate(rag_evidence_attach_total[10m]))) > 0.05' \
  | jq -r '.data.result | length')

conflict_spike=$(curl -s "$PROM/api/v1/query" \
  --data-urlencode 'query=rate(core_rag_conflict_total[10m]) > 0.01' \
  | jq -r '.data.result | length')

repro_drop=$(curl -s "$PROM/api/v1/query" \
  --data-urlencode 'query=(1 - reproducible_capsule_rate) > 0.001' \
  | jq -r '.data.result | length')

if [[ "$evidence_low" != "0" || "$conflict_spike" != "0" || "$repro_drop" != "0" ]]; then
  fail "Health gates failed → rollback to previous milestone"
fi

echo "Health gates passed"


