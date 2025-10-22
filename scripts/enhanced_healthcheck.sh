#!/usr/bin/env bash
set -euo pipefail

# Enhanced Healthcheck Script for DuRi Core
# This script performs comprehensive health checks including API endpoints

RED='\033[0;31m'; GREEN='\033[0;32m'; YEL='\033[1;33m'; NC='\033[0m'
pass(){ echo -e "${GREEN}✔ $*${NC}"; }
fail(){ echo -e "${RED}✘ $*${NC}"; exit 1; }
note(){ echo -e "${YEL}➜ $*${NC}"; }

BASE="http://localhost:8080"

# 1) Basic health check
note "Basic health check"
code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/health")
[[ "$code" == "200" ]] && pass "Health endpoint OK" || fail "Health endpoint failed: $code"

# 2) Metrics endpoint check
note "Metrics endpoint check"
code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/metrics")
[[ "$code" == "200" ]] && pass "Metrics endpoint OK" || fail "Metrics endpoint failed: $code"

# 3) API emotion endpoint check (happy path)
note "API emotion endpoint check (happy path)"
HAPPY_RESP=$(curl -s -X POST "$BASE/api/emotion" -H "Content-Type: application/json" -d @- <<EOF
{"emotion":"happy","timestamp":"$(date -Iseconds)","data":{"text":"healthcheck","source":"healthcheck"},"intensity":0.5}
EOF
)

echo "$HAPPY_RESP" | jq -e 'select(.status=="completed")' > /dev/null \
  && pass "Happy emotion API OK" \
  || fail "Happy emotion API failed: $HAPPY_RESP"

# 4) API emotion endpoint check (alias path)
note "API emotion endpoint check (alias path)"
JOY_RESP=$(curl -s -X POST "$BASE/api/emotion" -H "Content-Type: application/json" -d @- <<EOF
{"emotion":"joy","timestamp":"$(date -Iseconds)","data":{"text":"healthcheck","source":"healthcheck"},"intensity":0.5}
EOF
)

echo "$JOY_RESP" | jq -e 'select(.status=="completed")' > /dev/null \
  && pass "Joy alias API OK" \
  || fail "Joy alias API failed: $JOY_RESP"

# 5) Invalid emotion handling check
note "Invalid emotion handling check"
BAD_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/api/emotion" -H "Content-Type: application/json" -d @- <<EOF
{"emotion":"invalid_emotion","timestamp":"$(date -Iseconds)","data":{"text":"healthcheck"},"intensity":0.5}
EOF
)
[[ "$BAD_CODE" == "400" ]] && pass "Invalid emotion handling OK" || fail "Invalid emotion handling failed: $BAD_CODE"

# 6) Check for Unknown emotion in responses (should not appear)
note "Check for Unknown emotion in responses"
echo "$JOY_RESP" | grep -q 'Unknown emotion' \
  && fail "Joy alias not working (Unknown emotion found)" \
  || pass "Joy alias working (Unknown emotion not found)"

echo
pass "ENHANCED HEALTHCHECK ALL GREEN ✅"
