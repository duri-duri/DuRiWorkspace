#!/usr/bin/env bash
set -Eeuo pipefail

# 로케일 방어 (소수점/정렬 안전)
export LC_ALL=C.UTF-8 LANG=C.UTF-8

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
K="${1:-${METRIC_K:-3}}"
PRED_ARG="${2:-${RUN_PATH:-}}"

# 1) 입력 자동해결
PRED="$(bash "$ROOT/scripts/metrics/resolve_input.sh" "${PRED_ARG:-}")"

mkdir -p "$ROOT/.reports/metrics" "$ROOT/var/metrics"

echo "[metrics] hygiene..."
bash "$ROOT/scripts/metrics/data_hygiene.sh" "$PRED"

# hygiene FAIL 즉시 중단
if grep -q $'\tFAIL\t' "$ROOT/.reports/metrics/day66_hygiene.tsv"; then
  echo "[err] hygiene failed; see $ROOT/.reports/metrics/day66_hygiene.tsv" >&2
  exit 2
fi

echo "[metrics] compute..."
python3 "$ROOT/scripts/metrics/compute_metrics.py" --k "$K" --in "$PRED" --out "$ROOT/.reports/metrics/day66_metrics.tsv"

# 임계값 로드 (있으면)
TH_ENV_PATH="${TH_ENV:-$ROOT/.reports/metrics/day66_thresholds.env}"
[[ -f "$TH_ENV_PATH" ]] && set -a && source "$TH_ENV_PATH" && set +a || true

echo "[metrics] guard..."
bash "$ROOT/scripts/alerts/threshold_guard.sh" "$ROOT/.reports/metrics/day66_metrics.tsv" "$K"

# 프로메테우스 export 훅(있을 때만)
if [[ -x "$ROOT/scripts/metrics/export_prom.sh" ]]; then
  mkdir -p "$ROOT/var/metrics"
  bash "$ROOT/scripts/metrics/export_prom.sh" "$ROOT/.reports/metrics/day66_metrics.tsv" > "$ROOT/var/metrics/duri.prom"
fi

echo "[metrics] done → $ROOT/.reports/metrics/day66_metrics.tsv"
