#!/usr/bin/env bash
set -Eeuo pipefail
# 가장 기본적인 검증: Prometheus 엔드포인트 응답 확인
if command -v curl >/dev/null 2>&1; then
  curl -sf http://localhost:9090/metrics >/dev/null || { echo "MISS prometheus_metrics"; exit 1; }
else
  echo "MISS curl_command"; exit 1;
fi
echo "METRICS-ABI OK"
