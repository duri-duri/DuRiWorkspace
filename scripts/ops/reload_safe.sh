#!/usr/bin/env bash
set -euo pipefail

# Prometheus reload with pre-validation guard
# Usage: bash scripts/ops/reload_safe.sh

PROM_URL="${PROM_URL:-http://localhost:9090}"
TEXTFILE_DIR="${TEXTFILE_DIR:-./reports/textfile}"
ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"

cd "$ROOT"

mkdir -p "$TEXTFILE_DIR"

# Rate limiting: minimum gap between reloads (30s)
MIN_GAP="${MIN_GAP:-30}"
STAMP="/tmp/duri_last_reload.ts"
now=$(date +%s)

if [ -f "$STAMP" ]; then
  last=$(cat "$STAMP" 2>/dev/null || echo "0")
  gap=$((now - last))
  if [ "$gap" -lt "$MIN_GAP" ]; then
    echo "[SKIP] reload throttled (last reload ${gap}s ago, min gap ${MIN_GAP}s)"
    exit 0
  fi
fi

# 1) promtool validation
echo "[1/2] promtool validation..."
if docker run --rm --entrypoint /bin/sh \
  -v "$(pwd)/prometheus:/etc/prometheus:ro" prom/prometheus:v2.54.1 -lc \
  'promtool check config /etc/prometheus/prometheus.yml.minimal && promtool check rules /etc/prometheus/rules/*.yml' 2>&1; then
  echo "[OK] promtool passed"
else
  echo "[FAIL] promtool failed"
  echo "reload_ok 0" > "$TEXTFILE_DIR/duri_prometheus_reload.prom"
  exit 1
fi

# 2) Forbidden template function check
echo "[2/2] template function check..."
if grep -r -nE 'humanize[A-Za-z]+' prometheus/rules/ 2>/dev/null; then
  echo "[FAIL] Forbidden template function detected"
  echo "reload_ok 0" > "$TEXTFILE_DIR/duri_prometheus_reload.prom"
  exit 1
fi

# 3) Reload with exponential backoff (max 5 retries)
echo "[RELOAD] POST /-/reload"
MAX_RETRY="${MAX_RETRY:-5}"
BASE_SLEEP="${BASE_SLEEP:-2}"
retry=0
success=0

while [ $retry -lt $MAX_RETRY ]; do
  if curl -sf -XPOST "$PROM_URL/-/reload" >/dev/null 2>&1; then
    success=1
    break
  fi
  retry=$((retry + 1))
  if [ $retry -lt $MAX_RETRY ]; then
    sleep=$((BASE_SLEEP * (1 << (retry - 1))))
    echo "[RETRY] reload attempt $retry/$MAX_RETRY (backoff ${sleep}s)..."
    sleep $sleep
  fi
done

TS="$(date +%s)"
echo "$TS" > "$STAMP" 2>/dev/null || true

TMP="$(mktemp "${TEXTFILE_DIR}/.duri_prometheus_reload.prom.XXXXXX")"
{
  printf 'duri_prom_reload_success %d\n' $success
  printf 'duri_prom_reload_timestamp %d\n' "$TS"
  printf 'duri_prom_reload_retries %d\n' $retry
} > "$TMP"
chmod 644 "$TMP"
mv -f "$TMP" "${TEXTFILE_DIR}/duri_prometheus_reload.prom"

if [ $success -eq 1 ]; then
  echo "[OK] reload successful (attempts: $retry)"
  exit 0
else
  echo "[FAIL] reload failed after $MAX_RETRY attempts"
  exit 1
fi

