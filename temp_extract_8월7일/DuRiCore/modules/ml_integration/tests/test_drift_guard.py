import os, json, tempfile, subprocess
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
ART  = ROOT / "artifacts_phase1"

@pytest.mark.parametrize("na_delta,out_delta,iqr_ratio,expect_rc", [
    ("0.02","0.10","1.15", 0),  # Day1 상태: OK
])
def test_drift_check_ok(na_delta, out_delta, iqr_ratio, expect_rc):
    env = os.environ.copy()
    env["DRIFT_NA_DELTA"] = na_delta
    env["DRIFT_OUTLIER_DELTA"] = out_delta
    env["DRIFT_TARGET_IQR_RATIO"] = iqr_ratio
    rc = subprocess.call(["python3", "tools/drift_check.py"], cwd=str(ROOT), env=env)
    assert rc == expect_rc

def _make_tweaked_current(tmpdir: Path):
    # baseline 읽기
    base = json.load(open(ART / "schema_expectations_baseline.json"))
    cur  = json.loads(json.dumps(base))  # deep copy

    # 타겟 IQR을 아주 살짝 키워서 임계 초과 유도
    if "target_summary" in cur and "iqr" in cur["target_summary"]:
        cur["target_summary"]["iqr"] *= 1.02  # +2%

    # 또는 어떤 numeric 컬럼의 outlier_rate_iqr을 살짝 증가
    ns = cur.get("numeric_summary", {})
    for col, s in ns.items():
        if "outlier_rate_iqr" in s:
            s["outlier_rate_iqr"] = s.get("outlier_rate_iqr", 0.0) + 0.02  # +2%p
            break

    out = tmpdir / "schema_expectations_current.json"
    json.dump(cur, open(out, "w"), ensure_ascii=False, indent=2)
    return out

def test_drift_check_fail_when_tight_thresholds(tmp_path):
    cur_file = _make_tweaked_current(tmp_path)

    env = os.environ.copy()
    env["DRIFT_TARGET_IQR_RATIO"] = "1.01"     # 1%만 늘어나도 FAIL
    env["DRIFT_OUTLIER_DELTA"]    = "0.01"     # 1%p만 늘어나도 FAIL
    env["DRIFT_NA_DELTA"]         = "0.00"     # 동일 아니면 FAIL
    env["DRIFT_CURRENT_FILE"]     = str(cur_file)  # ← 주입!

    rc = subprocess.call(["python3", "tools/drift_check.py"], cwd=str(ROOT), env=env)
    assert rc == 2  # 의도적 FAIL
