#!/usr/bin/env bash
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YEL='\033[1;33m'; NC='\033[0m'
pass(){ echo -e "${GREEN}✔ $*${NC}"; }
fail(){ echo -e "${RED}✘ $*${NC}"; exit 1; }
note(){ echo -e "${YEL}➜ $*${NC}"; }

BASE="http://localhost:8080"

# 0) 컨테이너 상태
note "docker 컨테이너 상태 확인"
docker ps | grep -q "duri-core.*(healthy)" && pass "duri-core healthy" || fail "duri-core not healthy"

# 1) /health
note "헬스 체크"
code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/health")
[[ "$code" == "200" ]] && pass "/health 200" || fail "/health $code"

# 2) SSOT 설정 키 존재 확인 (컨테이너 내부 파이썬으로 검사)
note "SSOT 설정 키 확인"
docker exec duri-core python - <<'PY' || exit 1
from duri_core.app import create_app
app = create_app()
required = ["LOG_FILE","RECEIVE_JSON_LOG","EVOLUTION_LOG_PATH","ACTION_STATS_PATH","BRAIN_URL","EVOLUTION_URL"]
missing = [k for k in required if not app.config.get(k)]
if missing:
    raise SystemExit(f"Missing config keys: {missing}")
print("OK")
PY
pass "필수 설정 키 존재"

# 3) 감정 도메인/별칭: joy -> happy 정상 처리
note "감정 별칭(joy→happy) 및 허용 감정 처리"
JOY_RESP=$(curl -s -X POST "$BASE/api/emotion" -H "Content-Type: application/json" -d @- <<EOF
{"emotion":"joy","timestamp":"$(date -Iseconds)","data":{"text":"probe","source":"smoke","meta":{"request_id":"smoke-joy"}},"intensity":0.5}
EOF
)

# 1) status == completed (jq로 안전하게 파싱)
echo "$JOY_RESP" | jq -e 'select(.status=="completed")' > /dev/null \
  && pass "joy status=completed" \
  || fail "joy status!=completed: $JOY_RESP"

# 2) 별칭 정상화: Unknown emotion이 없어야 함
echo "$JOY_RESP" | grep -q 'Unknown emotion' \
  && fail "joy 별칭 미적용: $JOY_RESP" \
  || pass "joy 별칭 정상(Unknown emotion 미포함)"

# 3) reason이 positive 스펙트럼인지 확인
echo "$JOY_RESP" | jq -r '.decision.reason' | grep -Eq 'positive|happy' \
  && pass "joy 처리 reason OK" \
  || note "joy reason이 정책 문자열과 달라 별도 확인 필요"

HAPPY_RESP=$(curl -s -X POST "$BASE/api/emotion" -H "Content-Type: application/json" -d @- <<EOF
{"emotion":"happy","timestamp":"$(date -Iseconds)","data":{"text":"probe","source":"smoke","meta":{"request_id":"smoke-happy"}},"intensity":0.5}
EOF
)

# happy도 동일하게 검증
echo "$HAPPY_RESP" | jq -e 'select(.status=="completed")' > /dev/null \
  && pass "happy status=completed" \
  || fail "happy status!=completed: $HAPPY_RESP"

# 4) 잘못된 감정은 4xx로 방어되는지(예: "ecstasy")
note "잘못된 감정 4xx 확인"
BAD_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/api/emotion" -H "Content-Type: application/json" -d @- <<EOF
{"emotion":"ecstasy","timestamp":"$(date -Iseconds)","data":{"text":"probe","source":"smoke"},"intensity":0.5}
EOF
)
[[ "$BAD_CODE" == "400" ]] && pass "잘못된 감정에 400 반환" || fail "잘못된 감정에 $BAD_CODE 반환"

# 5) /metrics 노출 및 핵심 메트릭 존재
note "메트릭 엔드포인트 확인"
MET_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/metrics")
[[ "$MET_CODE" == "200" ]] && pass "/metrics 200" || fail "/metrics $MET_CODE"
curl -s "$BASE/metrics" | grep -Eq 'process_cpu_seconds_total|python_info' \
  && pass "기본 프로메테우스 메트릭 노출" \
  || fail "기본 메트릭 미노출"

# 6) 로그 파일 생성 확인 (컨테이너 내부)
note "로그 파일 생성 확인"
docker exec duri-core python - <<'PY' || exit 1
import os, glob
from datetime import datetime
date_str = datetime.now().strftime("%Y-%m-%d")
log_dir = "/tmp/logs"
req = os.path.join(log_dir, f"{date_str}_emotion_requests.json")
res = os.path.join(log_dir, f"{date_str}_emotion_responses.json")
missing = [p for p in [req,res] if not os.path.exists(p)]
if missing:
    raise SystemExit("Missing logs: " + ", ".join(missing))
print("OK")
PY
pass "요청/응답 로그 생성 확인"

echo
pass "SMOKE TEST ALL GREEN ✅"
