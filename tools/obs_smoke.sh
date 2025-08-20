#!/usr/bin/env bash
set -euo pipefail

export OTEL_EXPORTER_OTLP_ENDPOINT="${OTEL_EXPORTER_OTLP_ENDPOINT:-http://localhost:4318/v1/traces}"
export PROM_PORT="${PROM_PORT:-9108}"

echo "[1/3] Starting metrics endpoint on port ${PROM_PORT} (if integrated in process)"
# If your service is long-running, ensure maybe_expose_metrics_port() is called at boot.
# For one-shot scripts, skip. This is a placeholder for services.

echo "[2/3] Running one gate check to emit spans/metrics..."
GATE_SET="${GATE_SET:-tight}" bash tools/day9_gate_check.sh >/tmp/gate_run.log 2>&1 || true

echo "[3/3] Quick checks"
grep -E '"trace_id":"[0-9a-f]{32}"' -q /tmp/gate_run.log && echo "✓ trace_id present in logs" || echo "! trace_id not found (check logger wiring)"
grep -E 'latency_seconds_bucket\{phase=' -q /tmp/gate_run.log || echo "i metrics emitted by process; scrape via /metrics if service exposes"
echo "Done."



