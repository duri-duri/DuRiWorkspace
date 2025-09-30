#!/usr/bin/env bash
set -Eeuo pipefail
svc=${1:-duri_core_container}
# 컨테이너가 실행 중인지 확인
if docker ps --format "{{.Names}}" | grep -q "^${svc}$"; then
  echo "LOG-ABI OK"
else
  echo "LOG-ABI FAIL: Container not running"
  exit 1
fi
