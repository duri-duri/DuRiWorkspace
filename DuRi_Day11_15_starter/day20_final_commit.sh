#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1) SWEEP_DIR 안전 획득
if [[ -f "$ROOT/.last_sweep.json" ]]; then
  SWEEP_DIR="$(jq -r '.sweep_dir' "$ROOT/.last_sweep.json")"
fi
if [[ -z "${SWEEP_DIR:-}" || ! -d "$SWEEP_DIR" ]]; then
  # 최신 스위프 디렉토리 탐색 폴백
  SWEEP_DIR="$(ls -1dt "$ROOT/trace_v2_perf_tuned/sweeps"/sweep_* 2>/dev/null | head -n1 || true)"
fi
if [[ -z "${SWEEP_DIR:-}" || ! -d "$SWEEP_DIR" ]]; then
  echo "[ERR] sweep dir not found. run sweep first." >&2
  exit 2
fi

# 2) 최적 구성 추출
jq -r '.best | {sampling_rate,serialization,compression}' "$SWEEP_DIR/summary.json" \
  > "$ROOT/configs/trace_v2_selected.json"

echo "=== Day 20 실벤치 기반 검증 완료 ==="
echo "최적 구성:"
cat "$ROOT/configs/trace_v2_selected.json"

echo ""
echo "=== 환경변수 설정 예시 ==="
echo "export TRACE_SAMPLING=$(jq -r '.sampling_rate' "$ROOT/configs/trace_v2_selected.json")"
echo "export TRACE_SER=$(jq -r '.serialization' "$ROOT/configs/trace_v2_selected.json")"
echo "export TRACE_COMP=$(jq -r '.compression' "$ROOT/configs/trace_v2_selected.json")"

echo ""
echo "=== 최종 커밋 ==="
git add "$ROOT/configs/trace_v2_selected.json" "$SWEEP_DIR"/{report.md,summary.json,res_*.json}
git commit -m "perf(day20): real-bench verified; freeze best trace config"
