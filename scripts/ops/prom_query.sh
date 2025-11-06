#!/usr/bin/env bash
# Prometheus Query Helper
# Purpose: Unified interface for Prometheus queries (instant and range)
# Usage: bash scripts/ops/prom_query.sh <query> [timestamp] [mode] [start] [end] [step]

set -euo pipefail

BASE_URL="${PROM_BASE_URL:-}"
AUTH="${PROM_AUTH_HEADER:-}"
QUERY="${1:?query required}"
TIMESTAMP="${2:-$(date +%s)}"    # Unix timestamp or RFC3339
MODE="${3:-instant}"              # instant|range
START_TS="${4:-}"                 # For range queries
END_TS="${5:-}"                   # For range queries
STEP="${6:-30s}"                  # Step for range queries

log() {
  echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $*" >&2
}

die() {
  log "[FATAL] $*"
  exit 1
}

# Validate BASE_URL
if [ -z "$BASE_URL" ]; then
  die "PROM_BASE_URL not set"
fi

# Build auth header array
AUTH_HEADERS=()
if [ -n "$AUTH" ]; then
  AUTH_HEADERS=(-H "Authorization: $AUTH")
fi

# Ensure URL ends with /api/v1
if [[ ! "$BASE_URL" =~ /api/v1$ ]]; then
  if [[ "$BASE_URL" =~ /api$ ]]; then
    BASE_URL="${BASE_URL}/v1"
  else
    BASE_URL="${BASE_URL}/api/v1"
  fi
fi

# Retry logic with exponential backoff and jitter
retry_with_backoff() {
  local max_retries=5
  local retry=1
  local base_delay=2
  
  while [ $retry -le $max_retries ]; do
    local delay=$((base_delay * (2 ** (retry - 1))))
    # Add jitter (±20%)
    local jitter=$((delay * 20 / 100))
    local random_jitter=$((RANDOM % (jitter * 2 + 1) - jitter))
    delay=$((delay + random_jitter))
    
    # Clamp delay for 429/502/503 (slightly longer delays)
    if [ "$retry" -gt 2 ]; then
      delay=$((delay + retry))
    fi
    
    if [ "$MODE" = "instant" ]; then
      RESPONSE=$(curl -fsSL "${AUTH_HEADERS[@]}" \
        --get "${BASE_URL}/query" \
        --data-urlencode "query=${QUERY}" \
        --data-urlencode "time=${TIMESTAMP}" \
        --max-time 30 \
        --write-out "\n%{http_code}" 2>&1)
    else
      if [ -z "$START_TS" ] || [ -z "$END_TS" ]; then
        die "START_TS and END_TS required for range queries"
      fi
      RESPONSE=$(curl -fsSL "${AUTH_HEADERS[@]}" \
        --get "${BASE_URL}/query_range" \
        --data-urlencode "query=${QUERY}" \
        --data-urlencode "start=${START_TS}" \
        --data-urlencode "end=${END_TS}" \
        --data-urlencode "step=${STEP}" \
        --max-time 60 \
        --write-out "\n%{http_code}" 2>&1)
    fi
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    # Check for rate limit
    if [ "$HTTP_CODE" = "429" ]; then
      RETRY_AFTER=$(echo "$RESPONSE" | grep -i "retry-after" | head -1 | sed 's/.*retry-after: *\([0-9]*\).*/\1/i' || echo "$delay")
      log "Rate limit hit, waiting ${RETRY_AFTER}s before retry (attempt $retry/$max_retries)..."
      sleep "$RETRY_AFTER"
      retry=$((retry + 1))
      continue
    fi
    
    # Check for server errors
    if [ "$HTTP_CODE" = "502" ] || [ "$HTTP_CODE" = "503" ]; then
      log "Server error ($HTTP_CODE), retrying in ${delay}s (attempt $retry/$max_retries)..."
      sleep $delay
      retry=$((retry + 1))
      continue
    fi
    
    # Success
    if [ "$HTTP_CODE" = "200" ]; then
      echo "$BODY"
      return 0
    fi
    
    # Other errors
    log "HTTP $HTTP_CODE error, retrying in ${delay}s (attempt $retry/$max_retries)..."
    sleep $delay
    retry=$((retry + 1))
  done
  
  die "API call failed after $max_retries retries (last HTTP: $HTTP_CODE)"
}

# Execute query with retry
retry_with_backoff

