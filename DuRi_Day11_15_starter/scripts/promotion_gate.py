from __future__ import annotations
import json, sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

OPS = {
    "gt":  lambda a,b: a >  b,
    "ge":  lambda a,b: a >= b,
    "lt":  lambda a,b: a <  b,
    "le":  lambda a,b: a <= b,
    "eq":  lambda a,b: a == b,
    "ne":  lambda a,b: a != b,
}

def as_decimal(x: Any) -> Optional[Decimal]:
    if x is None: return None
    try: return Decimal(str(x))
    except (InvalidOperation, TypeError, ValueError): return None

def load_policy(path: Optional[Path]) -> Dict[str, Any]:
    if not path: return {}
    if not path.exists(): return {}
    import yaml
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

def eval_rule(name: str, value: Any, rule: Dict[str, Any]) -> Tuple[bool, str]:
    # 정수형 min/max 규칙 지원
    if "min" in rule or "max" in rule:
        ok = True; msgs = []
        if "min" in rule:
            ok_min = value is not None and int(value) >= int(rule["min"])
            ok &= ok_min
            if not ok_min: msgs.append(f"{name}<{rule['min']}")
        if "max" in rule:
            ok_max = value is not None and int(value) <= int(rule["max"])
            ok &= ok_max
            if not ok_max: msgs.append(f"{name}>{rule['max']}")
        return ok, (f"{name} ok" if ok else f"{name} fail: {', '.join(msgs)}")

    # 비교 연산 규칙 (Decimal)
    op = rule.get("op")
    thr = as_decimal(rule.get("value"))
    val = as_decimal(value)
    if op not in OPS or thr is None or val is None:
        return False, f"{name} invalid: op={op}, thr={thr}, val={val}"
    ok = OPS[op](val, thr)
    return ok, (f"{name} ok" if ok else f"{name} fail: {val} !{op} {thr}")

def evaluate(results: Dict[str, Any], policy: Dict[str, Any]) -> Tuple[bool, List[str]]:
    reasons: List[str] = []
    checks: List[Tuple[bool, str]] = []

    # results 키 매핑
    keymap = {
        "delta": "objective_delta",
        "p_value": "p_value",
        "t_stat": "t_stat",
        "n_A": "n_A",
        "n_B": "n_B",
    }
    for pol_key, res_key in keymap.items():
        if pol_key in policy:
            checks.append(eval_rule(pol_key, results.get(res_key), policy[pol_key]))

    # 최소 효과크기(|delta|)
    if "mes" in policy:
        delta_val = as_decimal(results.get("objective_delta"))
        thr = as_decimal(policy["mes"].get("value"))
        op = policy["mes"].get("op", "ge")
        if delta_val is None or thr is None or op not in OPS:
            checks.append((False, f"mes invalid"))
        else:
            ok = OPS[op](abs(delta_val), thr)
            checks.append((ok, "mes ok" if ok else f"mes fail: |{delta_val}| !{op} {thr}"))

    # CI 폭(ci_high - ci_low)
    if "ci_width" in policy:
        hi = as_decimal(results.get("ci_high"))
        lo = as_decimal(results.get("ci_low"))
        width = (hi - lo) if (hi is not None and lo is not None) else None
        checks.append(eval_rule("ci_width", width, policy["ci_width"]))

    ok_all = True
    for ok, msg in checks:
        reasons.append(msg)
        ok_all &= ok
    return ok_all, reasons

def cli(argv: List[str]) -> int:
    if len(argv) < 2:
        print("usage: python scripts/promotion_gate.py <results.json> [policy.yaml]")
        return 2
    results_p = Path(argv[1])
    policy_p = Path(argv[2]) if len(argv) >= 3 else None

    results = json.loads(results_p.read_text(encoding="utf-8"))
    policy = load_policy(policy_p)
    if not policy:
        policy = {"delta":{"op":"gt","value":0},"p_value":{"op":"le","value":0.05}}

    ok, reasons = evaluate(results, policy)
    status = "PROMOTION=PASS" if ok else "PROMOTION=FAIL"
    print(f"{status} | " + " ; ".join(reasons))
    return 0 if ok else 1

def main():
    sys.exit(cli(sys.argv))

if __name__ == "__main__":
    main()
