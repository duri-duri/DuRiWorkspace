#!/usr/bin/env bash
# 스모크 테스트: /emotion 엔드포인트가 202 + job_id를 반환하는지 검증
set -euo pipefail

DURI_CORE_URL="${DURI_CORE_URL:-http://localhost:8080}"
RESP_FILE="/tmp/_resp.json"

# 1) POST 요청 + 상태코드 확인
CODE=$(curl -sS -o "$RESP_FILE" -w '%{http_code}' -X POST "${DURI_CORE_URL}/emotion" \
  -H 'Content-Type: application/json' -d '{"emotion":"happy"}')

# 2) job_id 존재 확인
if ! python3 -c "
import json, sys
try:
    d = json.load(open('$RESP_FILE'))
    job_id = d.get('job_id', '')
    if not job_id or not isinstance(job_id, str):
        sys.exit(1)
    print('job_id:', job_id)
except Exception as e:
    print('JSON parse error:', e, file=sys.stderr)
    sys.exit(1)
" 2>/dev/null; then
    echo "[FAIL] job_id 없음 또는 JSON 파싱 실패"
    cat "$RESP_FILE" 2>/dev/null || true
    exit 1
fi

# 3) HTTP 상태코드 확인
if [ "$CODE" != "202" ]; then
    echo "[FAIL] HTTP 상태코드=$CODE (202 기대)"
    exit 1
fi

echo "[OK] 202 + job_id 확인"
exit 0

