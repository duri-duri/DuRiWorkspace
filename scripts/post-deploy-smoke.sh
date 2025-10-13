#!/usr/bin/env bash
set -euo pipefail

echo "=== 배포 직후 10-15분 스모크 체크 ==="

# promtool/jq 버전
echo "1. 도구 버전 확인:"
promtool --version && jq --version

# 런북 URL 샘플 3~5개 200 OK 확인
echo ""
echo "2. 런북 URL 가용성 확인:"
codes=$(xargs -n1 -I{} bash -lc 'curl -sS --max-time 5 --retry 2 --retry-delay 1 -o /dev/null -w "%{http_code}" "{}"; echo' <<EOF
https://docs.example.com/runbooks/mrr-slo
https://docs.example.com/runbooks/metric-delay
https://docs.example.com/runbooks/metric-absent
https://docs.example.com/runbooks/ma7-distortion
EOF
)
echo "$codes" | grep -vq '^200$' && { echo "Runbook URL check FAIL"; exit 1; }
echo "Runbook URL check OK"

# 알람 총량 확인
echo ""
echo "3. 알람 총량 확인:"
curl -sS --max-time 5 'localhost:9090/api/v1/alerts' | jq '.data.alerts | length' || { echo "Prometheus not available"; exit 1; }

# 핵심 패널 확인
echo ""
echo "4. 핵심 패널 확인:"
echo "SLO 패널: slo:core|brain|evolution|control:availability:*"
echo "Burn rate 패널: slo:*:burn_rate:*"
echo "Blackbox p95 패널: duri:blackbox:p95"
echo "Scrape 성공률: up{job=~\"blackbox|node_exporter\"}"

echo ""
echo "✅ 스모크 체크 완료"
