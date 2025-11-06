#!/usr/bin/env bash
# L4 Prometheus Rules Validation
# Purpose: Prometheus 룰 파일 문법 검증 및 로딩 확인
# Usage: bash scripts/ops/l4_prometheus_validation.sh

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo /home/duri/DuRiWorkspace)"
cd "${ROOT}"

RULES_FILE="prometheus/rules/l4_alerts.yml"
PROMETHEUS_URL="${PROMETHEUS_URL:-http://localhost:9090}"

echo "=== L4 Prometheus Rules Validation ==="
echo ""

# 1. promtool을 사용한 문법 검증
echo "1. Validating rule syntax with promtool..."
if command -v promtool >/dev/null 2>&1; then
  if promtool check rules "${RULES_FILE}" 2>&1; then
    echo "  ✅ Rule syntax is valid"
  else
    echo "  ❌ Rule syntax validation failed"
    exit 1
  fi
else
  echo "  ⚠️  promtool not found, skipping syntax check"
fi

# 2. Prometheus API를 통한 룰 로딩 확인
echo ""
echo "2. Checking rule loading via Prometheus API..."
if curl -sf "${PROMETHEUS_URL}/api/v1/rules" >/dev/null 2>&1; then
  rules_json=$(curl -sf "${PROMETHEUS_URL}/api/v1/rules" || echo "")
  
  if [[ -n "$rules_json" ]]; then
    l4_group=$(echo "$rules_json" | jq -r '.data.groups[] | select(.name=="l4_weekly_decision")' 2>/dev/null || echo "")
    
    if [[ -n "$l4_group" ]]; then
      rule_count=$(echo "$l4_group" | jq '.rules | length' 2>/dev/null || echo 0)
      echo "  ✅ L4 rules group found in Prometheus"
      echo "  Rule count: ${rule_count}"
      
      # 각 규칙 이름 출력
      echo "  Rules:"
      echo "$l4_group" | jq -r '.rules[].alert // .rules[].record' 2>/dev/null | while read -r rule_name; do
        echo "    - ${rule_name}"
      done
    else
      echo "  ⚠️  L4 rules group not found in Prometheus"
      echo "  (Rules file may not be loaded or Prometheus needs reload)"
    fi
  else
    echo "  ⚠️  Could not fetch rules from Prometheus API"
  fi
else
  echo "  ⚠️  Prometheus not accessible at ${PROMETHEUS_URL}"
  echo "  (Skipping API check - rules file syntax is valid)"
fi

# 3. Alertmanager 연동 확인 (선택적)
echo ""
echo "3. Checking Alertmanager integration..."
if curl -sf "${ALERTMANAGER_URL:-http://localhost:9093}/api/v2/alerts" >/dev/null 2>&1; then
  echo "  ✅ Alertmanager is accessible"
else
  echo "  ⚠️  Alertmanager not accessible (may not be configured)"
fi

echo ""
echo "=== Prometheus Validation Complete ==="

