#!/usr/bin/env bash
set -euo pipefail

# Prometheus reload with pre-validation guard
# Usage: bash scripts/ops/reload_safe.sh

PROM_URL="${PROM_URL:-http://localhost:9090}"
TEXTFILE_DIR="${TEXTFILE_DIR:-./reports/textfile}"
ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"

cd "$ROOT"

mkdir -p "$TEXTFILE_DIR"

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

# 3) Reload
echo "[RELOAD] POST /-/reload"
if curl -sf -XPOST "$PROM_URL/-/reload" >/dev/null 2>&1; then
  TS="$(date +%s)"
  TMP="$(mktemp "${TEXTFILE_DIR}/.duri_prometheus_reload.prom.XXXXXX")"
  {
    printf 'duri_prom_reload_success %d\n' 1
    printf 'duri_prom_reload_timestamp %d\n' "$TS"
  } > "$TMP"
  chmod 644 "$TMP"
  mv -f "$TMP" "${TEXTFILE_DIR}/duri_prometheus_reload.prom"
  echo "[OK] reload successful"
  exit 0
else
  echo "[FAIL] reload failed"
  TS="$(date +%s)"
  TMP="$(mktemp "${TEXTFILE_DIR}/.duri_prometheus_reload.prom.XXXXXX")"
  {
    printf 'duri_prom_reload_success %d\n' 0
    printf 'duri_prom_reload_timestamp %d\n' "$TS"
  } > "$TMP"
  chmod 644 "$TMP"
  mv -f "$TMP" "${TEXTFILE_DIR}/duri_prometheus_reload.prom"
  exit 1
fi

