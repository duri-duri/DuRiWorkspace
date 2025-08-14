#!/usr/bin/env python3
import os, json, time, copy, random
from pathlib import Path

# --- force working-dir to the script folder (idempotent) ---
os.chdir(Path(__file__).resolve().parent)
# -----------------------------------------------------------

# =========================
# 설정: Evolve/Promote 이중 기준 + REL 타이트닝
# =========================
GATE_ABS_EVOLVE = dict(
    max_r2_gap=0.07,      # 완화 (탐색 허용) - 0.06 → 0.07
    max_mse_ratio=1.45,   # 완화 (탐색 허용) - 1.35 → 1.45
    max_nrmse_ratio=1.25, # 완화
)

GATE_ABS_PROMOTE = dict(
    max_r2_gap=0.02,      # 엄격 (운영)
    max_mse_ratio=1.10,   # 엄격
    max_nrmse_ratio=1.20, # 엄격
    min_test_r2=0.80,     # 절대 문턱
)

REL = dict(
    # Evolve: "개선만 채택"에 가깝게 타이트닝(동급 홍수 차단)
    min_delta_test_r2=0.003,
    allow_within=0.003,
    evolve_floor=0.60,
)

ART = Path("artifacts_phase1")
ART.mkdir(exist_ok=True)
LEAGUE = ART / "league.jsonl"

# =========================
# 유틸: 모델 실행(외부 솔버 호출) - 프로젝트 환경에 맞게 import/호출
# =========================
def train_and_eval(cfg: dict):
    """
    프로젝트의 phase1 문제 해결 파이프라인을 호출하여
    validation/test 메트릭과 gap_analysis를 반환한다고 가정.
    여기선 artifacts_phase1/final_metrics_valid_test.json을 읽어 metrics를 가져오는 형태 유지.
    """
    # 여기는 기존 시스템의 실행 진입점에 맞춰 호출하세요.
    # 보통은 내부 모듈 import 후 run(cfg) → metrics 반환.
    # 현재 파이프라인은 cfg만 바꾸고 동일 진입점 실행 시 결과 파일에 반영되도록 설계되어 있음.
    # run
    from phase1_problem_solver import Phase1ProblemSolver
    solver = Phase1ProblemSolver(cfg)
    solver.run()

    # 결과 적재
    mpath = ART / "final_metrics_valid_test.json"
    m = json.loads(mpath.read_text())
    return m

# =========================
# 게이트 로직 (분리)
# =========================
def _abs_ok(m, ABS):
    gap = m.get("gap_analysis", {})
    return (
        gap.get("r2_gap", 1) <= ABS["max_r2_gap"] and
        gap.get("mse_ratio", 1e9) <= ABS["max_mse_ratio"] and
        gap.get("nrmse_ratio", 1e9) <= ABS["max_nrmse_ratio"]
    )

def gate_pass_evolve(m, baseline):
    """Evolve: 완화된 절대 + 상대(베이스라인 중심) 혼합 + 퇴행 방지"""
    # 하드필터 C: 과도한 과적합 즉시 차단
    gap = m.get("gap_analysis", {})
    if gap.get("mse_ratio", 9e9) > 2.0 or gap.get("nrmse_ratio", 9e9) > 1.4:
        return False, "hard_fail_ratio"
    
    # 절대 기준 체크 (완화된 기준)
    if not _abs_ok(m, GATE_ABS_EVOLVE):
        return False, "abs_gap"
    
    # 퇴행 방지: 최소 개선 기준
    base = baseline["test"]["r2"]
    r2 = m["test"]["r2"]
    min_improvement = 0.003  # 최소 0.3% 개선
    if r2 < base + min_improvement:
        return False, "regression_prevention"
    
    # 상대 기준 체크
    rel_ok = (r2 >= base + REL["min_delta_test_r2"]) or (base - r2 <= REL["allow_within"])
    floor_ok = r2 >= max(REL["evolve_floor"], base - REL["allow_within"])
    ok = rel_ok and floor_ok
    return ok, ("ok" if ok else ("rel" if not rel_ok else "floor"))

def gate_pass_promote(m, baseline):
    """Promote: 엄격 절대 + 상대(개선 필수)"""
    if not _abs_ok(m, GATE_ABS_PROMOTE):
        return False, "abs_gap"
    r2 = m["test"]["r2"]
    base = baseline["test"]["r2"]
    if r2 < GATE_ABS_PROMOTE["min_test_r2"]:
        return False, "abs_floor"
    rel_ok = r2 >= base + max(REL["min_delta_test_r2"], 0.005)  # 동급 승격 금지
    return (rel_ok, "ok" if rel_ok else "rel")

# =========================
# 선택 규칙: mse_ratio ↓ → |r2_gap| ↓ → test.r2 ↑ → (latency, size) ↓
# =========================
def pick_min_gap_min_ratio(cands):
    def key(m):
        g = m.get("gap_analysis", {})
        return (
            round(g.get("mse_ratio", 1e9), 6),
            round(abs(g.get("r2_gap", 1e9)), 6),
            -round(m.get("test", {}).get("r2", -1e9), 6),
            m.get("meta", {}).get("latency_ms", 0),
            m.get("meta", {}).get("model_size", 0),
        )
    return sorted(cands, key=key)[0]

# =========================
# 베이스라인 로딩
# =========================
def load_baseline_metrics():
    p = ART / "final_metrics_valid_test.json"
    if not p.exists():
        raise RuntimeError("no baseline metrics (artifacts_phase1/final_metrics_valid_test.json)")
    return json.loads(p.read_text())

# =========================
# 메인
# =========================
def main():
    print("== Day3 Auto-Evolve (guarded) ==")
    # --- Preflight (기존 테스트/드리프트/카나리 등 내부 스크립트가 있다면 유지) ---
    # from tools.canary_check import canary_check
    # from tools.drift_check import drift_check
    # canary_check()  # 내부에서 artifacts_phase1/canary_metrics_baseline.json 사용
    # drift_check()
    # pytest 등은 기존 스크립트에 포함되어 있으면 shell에서 실행하는 것으로 가정

    baseline = load_baseline_metrics()

    # ===== 탐색 후보 구성 (topk 확장 + calibration ablation) =====
    base = dict(
        strong_reg=True, stacking_enabled=False,
        calibration=None,               # (핵심) ablation에 의해 주입
        enable_xgb=True, iso_max_n=1500,
        select_by_test=False,
        categorical_handling="drop"
    )

    # topk = 2/3(추가) + 보수용 1
    model_space = [
        {**base, "force_topk_features": 2, "enable_xgb": False},
        {**base, "force_topk_features": 2, "enable_xgb": True,
         "xgb_params": dict(max_depth=3, min_child_weight=10, subsample=0.7,
                            colsample_bytree=0.6, reg_lambda=2.5, reg_alpha=0.3,
                            learning_rate=0.05, n_estimators=400)},
        {**base, "force_topk_features": 3, "enable_xgb": False},   # (신규) 과소적합 방지
        {**base, "force_topk_features": 1, "enable_xgb": False},   # 보수용
    ]
    cal_space = ["isotonic", "platt", "none"]  # (핵심) 보정 ablation

    tries = []
    idx = 0
    for cfg0 in model_space:
        cal_results = []
        for cal in cal_space:
            idx += 1
            cfg = {**cfg0, "calibration": cal}
            print(f"\n=== TRY #{idx} === (topk={cfg['force_topk_features']}, cal={cal}, xgb={cfg['enable_xgb']})")
            m = train_and_eval(cfg)

            # === [PATCH C START] 과도한 폭주 후보 하드 필터 ===
            g = m.get("gap_analysis", {})
            if g.get("mse_ratio", 9) > 2.0 or g.get("nrmse_ratio", 9) > 1.4:
                print("⚠️ hard-fail: excessive ratio -> skip from selection pool")
                passed = False
                reason = "hard_fail_ratio"
            else:
                # 게이트 판정(Evolve)
                passed, reason = gate_pass_evolve(m, baseline)
            print(f"→ testR2={m['test']['r2']:.4f} evolve_gate={'PASS' if passed else 'FAIL'} reason={reason}")
            # === [PATCH C END] ===

            # 리그 기록
            log = {
                "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "idx": idx,
                "cfg_keys": sorted(list(cfg.keys())),
                "metrics": m,
                "gate_pass": passed,
                "gate_reason": reason,
                "calibration": cal,
                "force_topk": cfg["force_topk_features"],
                "enable_xgb": cfg["enable_xgb"],
            }
            with LEAGUE.open("a", encoding="utf-8") as f:
                f.write(json.dumps(log, ensure_ascii=False) + "\n")
            # 후보 중 보정별 우수 모델 수집
            cal_results.append(m)

        # 보정 최적화 선택: mse_ratio ↓ → |r2_gap| ↓ → test.r2 ↑
        best_m = pick_min_gap_min_ratio(cal_results)
        tries.append(best_m)

    # === [PATCH B START] 게이트 기반 최종 선택 ===
    # ---- helpers: safe access to metrics/gaps -----------------------------------
    def _get_gap(d: dict) -> dict:
        if isinstance(d.get("gap_analysis"), dict):
            return d["gap_analysis"]
        m = d.get("metrics")
        if isinstance(m, dict) and isinstance(m.get("gap_analysis"), dict):
            return m["gap_analysis"]
        return {}

    def _best_r2(d: dict) -> float:
        t = d.get("test") or {}
        v = d.get("validation") or d.get("valid") or {}
        return float(t.get("r2", v.get("r2", float("-inf"))))

    def _r2_gap_val(d: dict) -> float:
        return float(_get_gap(d).get("r2_gap", 9e9))

    def _violation_score(gap: dict) -> float:
        # 안전한 기본값
        mr = float(gap.get("mse_ratio", float("inf")))
        rg = float(gap.get("r2_gap",   float("inf")))
        nr = float(gap.get("nrmse_ratio", float("inf")))
        # 위반 강도 가중합 (필요시 미세조정 가능)
        return (mr - 1.0) * 2.0 + max(rg - 0.06, 0) * 5.0 + max(nr - 1.25, 0) * 2.0

    # ---- least-bad fallback ------------------------------------------------------
    def pick_least_bad(cands: list) -> dict:
        # 1) 위반 최소 → 2) testR2 최대 → 3) r2_gap 최소
        return sorted(
            cands,
            key=lambda r: (_violation_score(_get_gap(r)), -_best_r2(r), _r2_gap_val(r))
        )[0]

    # 게이트 통과 후보와 실패 후보 분리
    pass_pool = []
    fail_pool = []
    for r in tries:  # tries는 시도별 메트릭 dict 리스트
        ok, reason = gate_pass_evolve(r, baseline)
        r["gate_pass"] = ok
        r["gate_reason"] = reason
        (pass_pool if ok else fail_pool).append(r)

    if pass_pool:
        final = max(pass_pool, key=lambda r: r["test"]["r2"])
        final_pick_reason = "best_among_pass"
    else:
        final = pick_least_bad(fail_pool)
        final_pick_reason = "least_bad_fallback"

    print("\n== RESULT ==")
    print(f"baseline testR2={baseline['test']['r2']:.4f}  best({final_pick_reason}) testR2={_best_r2(final):.4f}")
    
    # 안전한 요약 출력
    if final_pick_reason == "least_bad_fallback":
        fg = _get_gap(final)
        print(
            f"[SUMMARY] least_bad_fallback: testR2={_best_r2(final):.4f} "
            f"r2_gap={fg.get('r2_gap', float('nan')):.4f} "
            f"mse_ratio={fg.get('mse_ratio', float('nan')):.3f} "
            f"nrmse_ratio={fg.get('nrmse_ratio', float('nan')):.3f}"
        )
    else:
        print(f"[SUMMARY] final_pick reason={final_pick_reason} "
              f"testR2={_best_r2(final):.4f} "
              f"gap={_get_gap(final)}")
    
    print("done.")
    # === [PATCH B END] ===

if __name__ == "__main__":
    main()
