#!/bin/bash
# scripts/push_deploy_event.sh (코어 호출 부분만 분리 권장)
set -euo pipefail

# 환경변수 설정
DORA_PUSH_TOKEN="${DORA_PUSH_TOKEN:-duri-secret-token-2024}"
DORA_URL="${DORA_URL:-http://localhost:8000}"

push_core() {
  # 기존 POST 수행(파이썬 urllib)
  python3 -c "
import urllib.request
import urllib.parse
import sys
import json

# 파라미터 설정
params = {
    'env': '${ENV:-staging}',
    'service': '${SERVICE:-duri_control}',
    'source': '${SOURCE:-manual}',
    'commit': '${COMMIT:-unknown}',
    'id': '${ID:-$(date +%s)}'
}

# URL 구성
url = '${DORA_URL}/push/deployment?' + urllib.parse.urlencode(params)

# 요청 생성
req = urllib.request.Request(url, method='POST')
req.add_header('Authorization', 'Bearer ${DORA_PUSH_TOKEN}')

try:
    with urllib.request.urlopen(req, timeout=10) as response:
        result = response.read().decode()
        print(f'✅ 배포 이벤트 전송 성공: {result}')
        sys.exit(0)
except urllib.error.HTTPError as e:
    if e.code == 429:
        print(f'❌ Rate limited: {e.code}')
        sys.exit(1)
    elif e.code == 400:
        print(f'❌ Bad request: {e.code} - {e.read().decode()}')
        sys.exit(1)
    else:
        print(f'❌ HTTP Error: {e.code}')
        sys.exit(1)
except Exception as e:
    print(f'❌ Network Error: {e}')
    sys.exit(1)
"
}

push_with_backoff() {
  if push_core; then return 0; fi
  for s in 0.5 1 2; do
    echo "⏳ 재시도 대기: ${s}초..."
    sleep "$s"
    if push_core; then return 0; fi
  done
  echo "❌ 모든 재시도 실패"
  return 1
}

# 메인 실행
echo "🚀 배포 이벤트 전송 시작..."
push_with_backoff