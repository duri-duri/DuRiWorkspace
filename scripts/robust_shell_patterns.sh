#!/usr/bin/env bash
set -euo pipefail

# Robust Shell Script Patterns for DuRi Core
# This script demonstrates safe patterns for shell scripting

RED='\033[0;31m'; GREEN='\033[0;32m'; YEL='\033[1;33m'; NC='\033[0m'
pass(){ echo -e "${GREEN}✔ $*${NC}"; }
fail(){ echo -e "${RED}✘ $*${NC}"; exit 1; }
note(){ echo -e "${YEL}➜ $*${NC}"; }

BASE="http://localhost:8080"

# Pattern 1: Safe Python execution with HEREDOC
note "Safe Python execution with HEREDOC"
docker exec duri-core python - <<'PY'
from duri_common.config.emotion_labels import normalize_emotion
print('joy ->', normalize_emotion('joy'))
print('happiness ->', normalize_emotion('happiness'))
print('anger ->', normalize_emotion('anger'))
PY

# Pattern 2: Safe JSON with jq construction
note "Safe JSON construction with jq"
TIMESTAMP=$(date -Iseconds)
JSON_DATA=$(jq -n \
  --arg emotion "joy" \
  --arg timestamp "$TIMESTAMP" \
  --arg text "test" \
  --arg source "robust_test" \
  --argjson intensity 0.5 \
  '{
    emotion: $emotion,
    timestamp: $timestamp,
    data: {
      text: $text,
      source: $source
    },
    intensity: $intensity
  }')

echo "Constructed JSON: $JSON_DATA"

# Pattern 3: Safe API calls with proper error handling
note "Safe API calls with error handling"
RESPONSE=$(curl -s -X POST "$BASE/api/emotion" \
  -H "Content-Type: application/json" \
  -d "$JSON_DATA" \
  --fail-with-body \
  --max-time 10 \
  --retry 3 \
  --retry-delay 1)

if [ $? -eq 0 ]; then
    pass "API call successful"

    # Safe JSON parsing with jq
    STATUS=$(echo "$RESPONSE" | jq -r '.status')
    REASON=$(echo "$RESPONSE" | jq -r '.decision.reason')

    if [ "$STATUS" = "completed" ]; then
        pass "Status: $STATUS, Reason: $REASON"
    else
        fail "Unexpected status: $STATUS"
    fi
else
    fail "API call failed"
fi

# Pattern 4: Safe file operations
note "Safe file operations"
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

echo "$RESPONSE" > "$TEMP_DIR/response.json"
if [ -f "$TEMP_DIR/response.json" ]; then
    pass "File operations successful"
else
    fail "File operations failed"
fi

# Pattern 5: Safe variable handling
note "Safe variable handling"
set +u  # Temporarily disable unbound variable check
if [ -n "${OPTIONAL_VAR:-}" ]; then
    echo "Optional variable is set: $OPTIONAL_VAR"
else
    echo "Optional variable is not set"
fi
set -u  # Re-enable unbound variable check

echo
pass "ROBUST SHELL PATTERNS ALL GREEN ✅"
