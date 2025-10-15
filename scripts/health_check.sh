#!/bin/bash
set -euo pipefail

retry_check() {
  local port="$1" tries="${2:-20}" sleep_s="${3:-1}"
  for ((i=1;i<=tries;i++)); do
    # 기본 HEAD, 405/빈 응답이면 GET 폴백 (타임아웃 추가)
    code="$(curl --connect-timeout 1 --max-time 2 -sI -o /dev/null -w '%{http_code}' "http://localhost:$port/health" || true)"
    if [ "$code" = "405" ] || [ -z "$code" ]; then
      code="$(curl --connect-timeout 1 --max-time 2 -s -o /dev/null -w '%{http_code}' "http://localhost:$port/health" || true)"
    fi
    if [ "$code" = "200" ] || [ "$code" = "204" ]; then
      body="$(curl --connect-timeout 1 --max-time 2 -s "http://localhost:$port/health" || true)"
      if echo "$body" | grep -q '"status":"ok"'; then
        echo ":$port OK ($code) -> $(echo "$body" | head -c 80)"
      else
        echo ":$port OK ($code)"
      fi; return 0
    fi; sleep "$sleep_s"
  done; echo "❌ :$port health FAIL"; return 1
}

echo "🔍 헬스체크 시작..."
retry_check 8080
retry_check 8081
retry_check 8082
retry_check 8083
echo "✅ all health checks passed"
exit 0
