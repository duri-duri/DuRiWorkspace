#!/usr/bin/env bash
set -Eeuo pipefail
# Alertmanager test API를 통한 알람 드릴
curl -XPOST -H 'Content-Type: application/json' \
  -d '[{"labels":{"alertname":"TEST_BURN","severity":"critical","job":"test"},"annotations":{"summary":"test alert"}}]' \
  http://localhost:9093/api/v2/alerts
sleep 10
# 수신 확인
curl -sf 'http://localhost:9093/api/v2/alerts?active=true' | jq -e '.[].labels.alertname=="TEST_BURN"' >/dev/null && echo "ALERT-DRILL OK"
# 정리
curl -XPOST -H 'Content-Type: application/json' -d '[]' http://localhost:9093/api/v2/alerts

