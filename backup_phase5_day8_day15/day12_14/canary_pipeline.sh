#!/usr/bin/env bash
set -euo pipefail

# DuRi Canary Pipeline
# - 배포 실행(선택) → Grafana 주석 → 웜업 → 통계 가드 → (실패 시 롤백+주석)
#
# 사용 예:
#   GRAFANA_URL=http://localhost:3000 \
#   GRAFANA_TOKEN=XXXX \
#   PROM_URL=http://localhost:9090 \
#   DASH_UID=duri-phase-lat \
#   P95_SLO_MS=350 P99_SLO_MS=500 WINDOW=10m STEP=15s WARMUP_SECS=60 \
#   tools/canary_pipeline.sh --deploy "./deploy_canary.sh" --rollback "./rollback_canary.sh"
#
# 필수 도구: python3, jq, curl

PROM_URL="${PROM_URL:-http://localhost:9090}"
GRAFANA_URL="${GRAFANA_URL:-http://localhost:3000}"
DASH_UID="${DASH_UID:-duri-phase-lat}"
ANN_TAGS="${ANN_TAGS:-canary,duri}"

P95_SLO_MS="${P95_SLO_MS:-350}"
P99_SLO_MS="${P99_SLO_MS:-500}"
WINDOW="${WINDOW:-10m}"
STEP="${STEP:-15s}"
WARMUP_SECS="${WARMUP_SECS:-60}"

DEPLOY_CMD=""
ROLLBACK_CMD=""
SKIP_BASELINE="${SKIP_BASELINE:-0}"

usage() {
  cat <<'USAGE'
Usage: canary_pipeline.sh [--deploy "<cmd>"] [--rollback "<cmd>"] [--skip-baseline]
Env:
  PROM_URL (default: http://localhost:9090)
  GRAFANA_URL (default: http://localhost:3000)
  GRAFANA_TOKEN (optional, set to enable annotations)
  DASH_UID (default: duri-phase-lat)
  ANN_TAGS (default: canary,duri)
  P95_SLO_MS (default: 350), P99_SLO_MS (default: 500)
  WINDOW (default: 10m), STEP (default: 15s), WARMUP_SECS (default: 60)
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --deploy)   DEPLOY_CMD="$2"; shift 2 ;;
    --rollback) ROLLBACK_CMD="$2"; shift 2 ;;
    --skip-baseline) SKIP_BASELINE=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1"; usage; exit 2 ;;
  esac
done

need() { command -v "$1" >/dev/null 2>&1 || { echo "ERROR: '$1' not found"; exit 2; }; }
need curl; need jq; need python3

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GUARD="$ROOT_DIR/tools/canary_guard.py"
ANNOT="$ROOT_DIR/tools/annotate_grafana.sh"
[ -f "$GUARD" ] || { echo "ERROR: missing $GUARD"; exit 2; }
[ -f "$ANNOT" ] || { echo "ERROR: missing $ANNOT"; exit 2; }

annotate() {
  local text="$1"
  if [[ -n "${GRAFANA_TOKEN:-}" ]]; then
    "$ANNOT" -t "$text" -g "$ANN_TAGS" -d "$DASH_UID" || true
  else
    echo "ℹ️  GRAFANA_TOKEN not set → skip annotation: $text"
  fi
}

run_guard() {
  python3 "$GUARD" \
    --prom-url "$PROM_URL" \
    --window "$WINDOW" --step "$STEP" \
    --p95-slo-ms "$P95_SLO_MS" --p99-slo-ms "$P99_SLO_MS" \
    --min-exceed-ratio 0.2 --confidence 0.95
}

echo "▶️  Canary pipeline start (PROM_URL=$PROM_URL, DASH_UID=$DASH_UID, WINDOW=$WINDOW, STEP=$STEP)"

if [[ "$SKIP_BASELINE" != "1" ]]; then
  echo "🔎 Baseline health check…"
  if ! run_guard; then
    annotate "❌ Canary baseline FAIL"
    echo "Baseline failed. Stop."; exit 3
  fi
  echo "✅ Baseline OK"
fi

annotate "🚀 Canary start"

if [[ -n "$DEPLOY_CMD" ]]; then
  echo "📦 Deploy: $DEPLOY_CMD"
  bash -lc "$DEPLOY_CMD"
else
  echo "ℹ️  No --deploy command provided (skipping deploy step)"
fi

echo "⏳ Warmup ${WARMUP_SECS}s…"; sleep "$WARMUP_SECS"

set +e
run_guard
rc=$?
set -e

if [[ $rc -eq 0 ]]; then
  annotate "✅ Canary PASS"
  echo "✅ Canary PASS"; exit 0
else
  annotate "❌ Canary FAIL"
  echo "❌ Canary FAIL (rc=$rc)"
  if [[ -n "$ROLLBACK_CMD" ]]; then
    echo "↩️  Rollback: $ROLLBACK_CMD"
    bash -lc "$ROLLBACK_CMD" || true
    annotate "↩️  Canary rollback executed"
  fi
  exit 2
fi
