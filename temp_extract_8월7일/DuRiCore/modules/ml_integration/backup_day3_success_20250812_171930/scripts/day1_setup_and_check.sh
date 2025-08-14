#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"   # scripts/.. = ml_integration
cd "$ROOT"

ART="artifacts_phase1"
mkdir -p "$ART" tools

echo "==[1/4] 기준선 스냅샷 태깅(있으면 유지)=="
if ls $ART/snapshot_*.json >/dev/null 2>&1; then
  SNAP=$(ls -t $ART/snapshot_*.json | head -1)
  TS=$(date +%Y%m%d_%H%M%S)
  python3 - <<PY
import json,sys
p="$SNAP"
meta=json.load(open(p))
meta["tag"]=meta.get("tag", f"{'$TS'}_realdata_baseline_rf_top2")
json.dump(meta, open(p,"w"), ensure_ascii=False, indent=2)
print("tagged:", p, meta["tag"])
PY
else
  echo "WARN: snapshot not found yet. Run Phase1ProblemSolver once first."
fi

echo "==[2/4] split 고정 설정으로 1회 재실행=="
python3 - <<'PY'
from phase1_problem_solver import Phase1ProblemSolver
cfg=dict(
  data_path="test_data.csv",
  schema_map={"target":"target","numeric":["num_a","num_b","num_c","num_d","num_e","num_f"],
              "categorical":["cat_a","cat_b"],"drop":["row_id"],"datetime":["event_time"]},
  random_state=42, use_stratified_split=True,
  load_fixed_split=True,   # 재현성 락
  save_fixed_split=False,  # 이미 저장되어 있다면 불필요
  reseed_on_imbalance=False,
  strong_reg=True, stacking_enabled=False, enable_xgb=True,
  calibration="isotonic", iso_max_n=1500, select_by_test=False,
  categorical_handling="drop"
)
Phase1ProblemSolver(cfg).run()
PY

echo "==[3/4] 스키마 기준선 고정(없으면 생성)=="
if [ ! -f "$ART/schema_expectations_baseline.json" ]; then
  D1=$(ls -t $ART/error_slicing_*.json | head -1)
  python3 - <<PY
import json,sys
d1="$D1"
out="$ART/schema_expectations_baseline.json"
obj=json.load(open(d1))
exp=obj.get("schema_expectations", {})
json.dump(exp, open(out,"w"), ensure_ascii=False, indent=2)
print("schema baseline saved:", out)
PY
else
  echo "schema baseline already present: $ART/schema_expectations_baseline.json"
fi

echo "==[4/4] 드리프트 체크 실행=="
python3 tools/drift_check.py || {
  echo "DRIFT WARN → 오늘의 자동 스윕/진화는 SKIP 권장"
  exit 2
}

echo "DONE: Day1 baseline lock + drift guard OK"
