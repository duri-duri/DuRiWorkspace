# auto_evolve_guarded.py
import json, time, copy, os, subprocess, glob
from pathlib import Path
from typing import Dict, Any, List, Optional
from phase1_problem_solver import Phase1ProblemSolver

ART = Path("artifacts_phase1")
LEAGUE = ART / "league.jsonl"
# 절대 갭: Promote(엄격) / Evolve(완화) 분리
GATE_ABS_PROMOTE = dict(max_r2_gap=0.02, max_mse_ratio=1.10, max_nrmse_ratio=1.20, min_test_r2=0.80)
GATE_ABS_EVOLVE  = dict(max_r2_gap=0.06, max_mse_ratio=1.35, max_nrmse_ratio=1.25)  # ← 완화

REL = dict(
    min_delta_test_r2=0.000,   # 동급 허용
    allow_within=0.005,        # 베이스라인 대비 -0.005까지 동급
    evolve_floor=0.60,
)

def _latest(globpat:str) -> Optional[Path]:
    xs = sorted(glob.glob(globpat), key=os.path.getmtime)
    return Path(xs[-1]) if xs else None

def _abs_gate_ok(m, ABS):
    g = m.get("gap_analysis", {})
    return (
        g.get("r2_gap", 1)   <= ABS["max_r2_gap"] and
        g.get("mse_ratio", 1e9)   <= ABS["max_mse_ratio"] and
        g.get("nrmse_ratio", 1e9) <= ABS["max_nrmse_ratio"]
    )

def gate_pass_evolve(m, baseline):
    """탐색(Evolve) 단계: 절대 + 상대(베이스라인 중심) 혼합 게이트."""
    if not _abs_gate_ok(m, GATE_ABS_EVOLVE):
        return False, "abs_gap"

    base = baseline["test"]["r2"]
    test_r2 = m["test"]["r2"]

    # 상대 기준: 개선 or 동급 허용
    rel_ok = (test_r2 >= base + REL["min_delta_test_r2"]) or (base - test_r2 <= REL["allow_within"])
    # 바닥치(너무 낮은 건 탐색이라도 불허)
    floor_ok = test_r2 >= max(REL["evolve_floor"], base - REL["allow_within"])

    ok = rel_ok and floor_ok
    reason = "ok" if ok else ("rel" if not rel_ok else "floor")
    return ok, reason

def gate_pass_promote(m, baseline):
    """운영 승격(Promote) 단계: 절대 문턱 + 베이스라인 대비 개선."""
    if not _abs_gate_ok(m, GATE_ABS_PROMOTE):
        return False, "abs_gap"

    test_r2 = m["test"]["r2"]
    base = baseline["test"]["r2"]

    # 절대 기준
    if test_r2 < GATE_ABS_PROMOTE["min_test_r2"]:
        return False, "abs_floor"

    # 상대 기준: 승격은 '개선'이 기본(동급 승격은 옵션)
    rel_ok = test_r2 >= base + max(REL["min_delta_test_r2"], 0.005)  # 승격은 최소 +0.005 개선 요구
    return (rel_ok, "ok" if rel_ok else "rel")

# 기존 함수는 호환성을 위해 유지 (deprecated)
def gate_pass(m: Dict[str, Any]) -> bool:
    g = m.get("gap_analysis", {})
    return (
        g.get("r2_gap", 1) <= GATE_ABS_PROMOTE["max_r2_gap"]
        and g.get("mse_ratio", 1e9) <= GATE_ABS_PROMOTE["max_mse_ratio"]
        and g.get("nrmse_ratio", 1e9) <= GATE_ABS_PROMOTE["max_nrmse_ratio"]
        and m.get("test", {}).get("r2", 0.0) >= GATE_ABS_PROMOTE["min_test_r2"]
    )

def better(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    # 게이트 통과 > test R2 > test MSE > r2_gap
    ap, bp = gate_pass(a), gate_pass(b)
    if ap != bp: return ap and not bp
    if a["test"]["r2"] != b["test"]["r2"]: return a["test"]["r2"] > b["test"]["r2"]
    if a["test"]["mse"] != b["test"]["mse"]: return a["test"]["mse"] < b["test"]["mse"]
    return a["gap_analysis"].get("r2_gap", 9e9) < b["gap_analysis"].get("r2_gap", 9e9)

def read_metrics() -> Dict[str, Any]:
    return json.load(open(ART/"final_metrics_valid_test.json"))

def run_phase1(cfg: Dict[str, Any]) -> Dict[str, Any]:
    Phase1ProblemSolver(cfg).run()
    return read_metrics()

def canary_gate() -> bool:
    rc = subprocess.call(["python3", "tools/canary_check.py"])
    return rc == 0

def drift_gate() -> bool:
    rc = subprocess.call(["python3", "tools/drift_check.py"])
    return rc == 0

def pytest_gate() -> bool:
    rc = subprocess.call(["pytest", "-q", "tests/test_data_guard.py", "tests/test_split_lock.py"])
    if rc != 0: return False
    # 드리프트는 운영 기본 임계치 체크만 (tight-fail 테스트는 제외)
    rc = subprocess.call(["pytest", "-q", "tests/test_drift_guard.py", "-k", "test_drift_check_ok"])
    return rc == 0

def preflight_or_abort() -> None:
    print("🔎 Preflight gates: canary → drift → pytest")
    if not canary_gate(): raise SystemExit("❌ Canary gate FAIL → 스윕 중단")
    if not drift_gate():  raise SystemExit("❌ Drift gate FAIL → 스윕 중단")
    if not pytest_gate(): raise SystemExit("❌ Pytest gate FAIL → 스윕 중단")
    print("✅ Preflight OK")

def propose_candidates(flags: Dict[str, Any]) -> List[Dict[str, Any]]:
    base = dict(
        data_path="test_data.csv",
        schema_map={"target":"target",
                    "numeric":["num_a","num_b","num_c","num_d","num_e","num_f"],
                    "categorical":["cat_a","cat_b"],"drop":["row_id"],"datetime":["event_time"]},
        random_state=42, use_stratified_split=True, load_fixed_split=True,
        save_fixed_split=False, reseed_on_imbalance=False,
        strong_reg=True, stacking_enabled=False, calibration="isotonic",
        enable_xgb=True, iso_max_n=1500, select_by_test=False,
        categorical_handling="drop"
    )
    cands = [
        {**base, "force_topk_features": 2, "enable_xgb": False},
        {**base, "force_topk_features": 2, "enable_xgb": True,
         "xgb_params": dict(max_depth=3, min_child_weight=10, subsample=0.7,
                            colsample_bytree=0.6, reg_lambda=2.5, reg_alpha=0.3,
                            learning_rate=0.05, n_estimators=400)},
        {**base, "force_topk_features": 1, "enable_xgb": False},
    ]
    sug = flags.get("preprocessing_suggestions", {})
    if sug.get("clip") or sug.get("winsorize") or sug.get("impute"):
        p = copy.deepcopy(cands[0]); p["enable_preproc_from_suggestions"]=True
        cands.insert(0, p)
    return cands

def read_flags() -> Dict[str, Any]:
    es = _latest(str(ART/"error_slicing_*.json"))
    return json.load(open(es)) if es else {}

def log_league(entry: Dict[str, Any]):
    LEAGUE.parent.mkdir(exist_ok=True, parents=True)
    with open(LEAGUE, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def snapshot_tag(note: str):
    snap = _latest(str(ART/"snapshot_*.json"))
    if not snap: return
    meta = json.load(open(snap))
    meta["tag"] = f"{time.strftime('%Y%m%d_%H%M%S')}_{note}"
    json.dump(meta, open(snap, "w"), ensure_ascii=False, indent=2)
    print(f"🔖 snapshot tagged: {meta['tag']}")

def main():
    print("== Day3 Auto-Evolve (guarded) ==")
    preflight_or_abort()

    baseline = read_metrics()
    flags = read_flags()
    cands = propose_candidates(flags)

    best = baseline
    for i, cfg in enumerate(cands, 1):
        print(f"\n=== TRY #{i}/{len(cands)} ===")
        # 캔너리 기준선에서 벗어나면 스윕 중단
        if not canary_gate():
            print("⛔ Canary deviation detected → sweep aborted")
            break
        m = run_phase1(cfg)
        
        passed, reason = gate_pass_evolve(m, baseline)
        print(f"→ testR2={m['test']['r2']:.4f} evolve_gate={'PASS' if passed else 'FAIL'} reason={reason}")
        
        entry = {
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "idx": i, "cfg_keys": sorted(k for k in cfg.keys() if k not in ("schema_map","xgb_params")),
            "metrics": m, "gate_pass": passed, "gate_reason": reason
        }
        log_league(entry)
        
        if better(m, best):
            best = m
            snapshot_tag(f"auto_evolve_pass_cand{i}")

    print("\n== RESULT ==")
    print(f"baseline testR2={baseline['test']['r2']:.4f}  best testR2={best['test']['r2']:.4f}")
    print("done.")

if __name__ == "__main__":
    main()
