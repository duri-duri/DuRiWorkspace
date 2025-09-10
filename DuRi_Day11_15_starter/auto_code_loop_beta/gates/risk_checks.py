import argparse, json, pathlib
import yaml

SEVERITY = {"Validation": 2, "Transient": 1, "System": 3, "Spec": 2}

def _load_json(p: pathlib.Path):
    if not p.exists(): 
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None

def _load_policy(path):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}

def _find_freeze_flag(start: pathlib.Path):
    # 상위 3단계까지 FREEZE.FLAG 탐색
    cur = start
    for _ in range(4):
        f = cur / "FREEZE.FLAG"
        if f.exists():
            return True
        cur = cur.parent
    return False

def main(inp, outp):
    base = pathlib.Path(__file__).resolve().parent   # .../auto_code_loop_beta/gates
    project_root = base.parent.parent               # .../DuRi_Day11_15_starter
    
    # 정책 로드
    policy = _load_policy((base.parent / "policy.yaml"))
    guards = (policy.get("risk_guards") or {})
    
    # 임계치 설정 (외부화)
    thr_dp95   = float(guards.get("delta_p95_le", 0.05))
    thr_p99mul = float(guards.get("p99_le_slo_multiplier", 1.05))
    thr_canary = float(guards.get("canary_pct_lt", 25))
    thr_pass   = float(guards.get("pass_rate_ge", 0.80))
    req_freeze = bool(guards.get("require_no_freeze", True))
    
    logs_json = _load_json(pathlib.Path(inp)) or {}
    failures = logs_json.get("failures", [])
    pass_rate = logs_json.get("pass_rate", None)

    # 운영 지표(선택): p95/p99/SLO/카나리 비율
    metrics_path = project_root / "slo_sla_dashboard_v1" / "metrics.json"
    metrics = _load_json(metrics_path) or {}
    p95 = metrics.get("p95_ms")
    p99 = metrics.get("p99_ms")
    base_p95 = metrics.get("baseline_p95_ms") or metrics.get("p95_baseline_ms")
    slo_p99 = metrics.get("slo_p99_ms")
    canary_pct = metrics.get("canary_traffic_pct") or metrics.get("canary_pct")

    # 기본 고위험 판정
    high = [f for f in failures if SEVERITY.get(f.get("type"),2) >= 3]

    # --- 단건 System timeout 완화 조건 검사 (외부화된 임계치 사용) ---
    system_timeouts = [
        f for f in failures
        if (f.get("type") == "System") and ("timeout" in (f.get("msg","")+f.get("reason","")).lower())
    ]
    cond_single_timeout = (len(system_timeouts) == 1)
    cond_pass_rate = (pass_rate is not None and float(pass_rate) >= thr_pass)
    cond_delta_p95 = False
    if isinstance(p95,(int,float)) and isinstance(base_p95,(int,float)) and base_p95 > 0:
        cond_delta_p95 = ((p95 - base_p95) / base_p95) <= thr_dp95
    cond_p99 = False
    if isinstance(p99,(int,float)) and isinstance(slo_p99,(int,float)) and slo_p99 > 0:
        cond_p99 = p99 <= (slo_p99 * thr_p99mul)
    cond_canary = (isinstance(canary_pct,(int,float)) and canary_pct < thr_canary)
    freeze_on = _find_freeze_flag(base) if req_freeze else False

    # 모든 가드 충족 시: 단건 timeout을 고위험 목록에서 제외(경고로 다운그레이드)
    if cond_single_timeout and cond_pass_rate and cond_delta_p95 and cond_p99 and cond_canary and not freeze_on:
        high = [f for f in high if f not in system_timeouts]
        note = f"downgraded: single System timeout (p95Δ≤{thr_dp95*100:.0f}%, p99≤SLO*{thr_p99mul}, canary<{thr_canary:.0f}%, no FREEZE)"
        auto_human_ack = True
    else:
        note = "auto-ack when no high severity"
        auto_human_ack = False

    out = {
        "new_risks": len(high),
        "high_severity_count": len(high),
        "human_ack": True if len(high) == 0 else auto_human_ack,
        "guards": {
            "single_timeout": cond_single_timeout,
            "pass_rate_ge_0.80": cond_pass_rate,
            "delta_p95_le_5pct": cond_delta_p95,
            "p99_le_slo105": cond_p99,
            "canary_lt_25pct": cond_canary,
            "freeze_flag": freeze_on
        },
        "policy_thresholds": {
            "delta_p95_le": thr_dp95,
            "p99_le_slo_multiplier": thr_p99mul,
            "canary_pct_lt": thr_canary,
            "pass_rate_ge": thr_pass,
            "require_no_freeze": req_freeze
        },
        "notes": note
    }
    pathlib.Path(outp).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="outp", required=True)
    args = ap.parse_args()
    main(args.inp, args.outp)
