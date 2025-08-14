#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==[1/5] 캔너리셋 생성/고정=="
python3 scripts/make_canary_split.py

echo "==[2/5] 재현성 잠금 설정으로 1회 실행=="
python3 - <<'PY'
from phase1_problem_solver import Phase1ProblemSolver
cfg=dict(
  data_path="test_data.csv",
  schema_map={"target":"target","numeric":["num_a","num_b","num_c","num_d","num_e","num_f"],
              "categorical":["cat_a","cat_b"],"drop":["row_id"],"datetime":["event_time"]},
  random_state=42, use_stratified_split=True,
  load_fixed_split=True, save_fixed_split=True,   # split 파일을 명시적으로 보존
  reseed_on_imbalance=False, strong_reg=True,
  stacking_enabled=False, enable_xgb=True,
  calibration="isotonic", iso_max_n=1500, select_by_test=False,
  categorical_handling="drop"
)
Phase1ProblemSolver(cfg).run()
PY

# 모델 존재성/정합성 빠른 체크
if ! ls artifacts_phase1/*model*.pkl >/dev/null 2>&1; then
  echo "❌ 모델 피클 없음 → stop"
  exit 2
fi

echo "==[3/5] 캔너리 성능 게이트=="
python3 tools/canary_check.py

echo "==[4/5] 드리프트 가드(기본 임계치) 사전 체크=="
python3 tools/drift_check.py

echo "==[5/5] pytest 3종 실행=="
pytest -q tests/test_data_guard.py
pytest -q tests/test_split_lock.py
pytest -q tests/test_drift_guard.py

echo "DONE: Day2 canary+tests OK"
