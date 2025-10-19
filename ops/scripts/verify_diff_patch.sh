#!/usr/bin/env bash
set -euo pipefail
echo "== Check 1. prometheus.yml: rule_files"
grep -qE '/etc/prometheus/rules\.d/\*\.yml' prometheus.yml && echo "OK rule_files" || { echo "NG rule_files"; exit 1; }

echo "== Check 2. no recursive glob"
! grep -R -qE 'rules/\*\*/\*\.yml' prometheus.yml && echo "OK no recursive glob" || { echo "NG recursive glob"; exit 1; }

echo "== Check 3. compose merged: versions & mounts"
docker compose -f docker-compose.yml -f compose.health.overlay.yml -p duriworkspace config > /tmp/dw.merged.yml
grep -q 'prom/prometheus:v2.54.1' /tmp/dw.merged.yml && echo "OK prometheus version" || { echo "NG prometheus version"; exit 1; }
grep -q 'grafana/grafana:10.4.5' /tmp/dw.merged.yml && echo "OK grafana version" || { echo "NG grafana version"; exit 1; }
grep -q '/etc/prometheus/rules.d' /tmp/dw.merged.yml && echo "OK rules.d mount" || { echo "NG rules.d mount"; exit 1; }
! grep -qE '/etc/prometheus/rules/[^:]+\.yml' /tmp/dw.merged.yml && echo "OK no single-file bind" || { echo "NG single-file bind"; exit 1; }

echo "== Check 4. runtime config"
curl -sf http://localhost:9090/-/ready >/dev/null && echo "OK ready" || { echo "NG not ready"; exit 1; }
RG=$(curl -sf http://localhost:9090/api/v1/rules | jq '.data.groups | length')
echo "Rule groups: $RG"
curl -sf http://localhost:9090/api/v1/status/config | jq -r '.data.yaml' | grep -q '/etc/prometheus/rules.d/\*\.yml' && echo "OK runtime rule_files" || { echo "NG runtime rule_files"; exit 1; }

echo "ALL GOOD ✅"
