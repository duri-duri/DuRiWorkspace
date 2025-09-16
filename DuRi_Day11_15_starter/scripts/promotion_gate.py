from __future__ import annotations
import json, sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

__all__ = ["evaluate", "load_policy", "as_decimal", "eval_rule"]

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
    """일반화된 정책 평가: 모든 정책 규칙을 자동으로 평가"""
    
    def ci_width_val(r: Dict[str, Any]):
        """CI 폭 계산"""
        lo, hi = r.get("ci_low"), r.get("ci_high")
        if lo is None or hi is None:
            return None
        try:
            return Decimal(str(hi)) - Decimal(str(lo))
        except Exception:
            return None

    # 특별한 getter들 (계산형 파생지표)
    getters = {
        "delta":    lambda r: r.get("objective_delta"),
        "p_value":  lambda r: r.get("p_value"),
        "ci_width": ci_width_val,
        "mes":      lambda r: abs(float(r.get("objective_delta", 0))) if r.get("objective_delta") is not None else None,
    }

    checks: List[Tuple[bool, str]] = []
    
    # 정책에 정의된 모든 키를 평가 (메타데이터 제외)
    for name, rule in (policy or {}).items():
        # 메타데이터 필드들은 평가에서 제외
        if name in ["policy_version"] or not isinstance(rule, dict):
            continue
            
        # 정의된 getter가 있으면 사용, 없으면 동명이의 결과 필드 사용
        value = getters.get(name, lambda r: r.get(name))(results)
        ok, msg = eval_rule(name, value, rule)
        checks.append((ok, msg))

    ok_all = all(ok for ok, _ in checks) if checks else True
    reasons = [msg for _, msg in checks] if checks else ["no_policy_rules"]
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
