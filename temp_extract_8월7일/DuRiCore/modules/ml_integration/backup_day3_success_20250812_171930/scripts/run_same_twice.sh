#!/usr/bin/env bash
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"/ml_integration

one_run () {
python3 - <<'PY'
from phase1_problem_solver import Phase1ProblemSolver
cfg=dict(
  data_path="test_data.csv",
  schema_map={"target":"target","numeric":["num_a","num_b","num_c","num_d","num_e","num_f"],
              "categorical":["cat_a","cat_b"],"drop":["row_id"],"datetime":["event_time"]},
  random_state=42, use_stratified_split=True,
  load_fixed_split=True, save_fixed_split=False,
  reseed_on_imbalance=False, strong_reg=True,
  stacking_enabled=False, enable_xgb=True,
  calibration="isotonic", iso_max_n=1500, select_by_test=False,
  categorical_handling="drop"
)
Phase1ProblemSolver(cfg).run()
PY
}

echo "[A] run #1"; one_run
cp artifacts_phase1/final_metrics_valid_test.json /tmp/metrics_run1.json

echo "[B] run #2"; one_run
cp artifacts_phase1/final_metrics_valid_test.json /tmp/metrics_run2.json

python3 - <<'PY'
import json
m1=json.load(open("/tmp/metrics_run1.json"))
m2=json.load(open("/tmp/metrics_run2.json"))
def r2(m): return m["test"]["r2"]
print("run1 test R2:", r2(m1), "run2 test R2:", r2(m2), "Δ:", abs(r2(m1)-r2(m2)))
PY
