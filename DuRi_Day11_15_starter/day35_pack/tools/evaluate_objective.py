#!/usr/bin/env python3
import argparse, json, math, sys, pathlib, re, statistics as stats
import yaml

def to01(v):
    # Accept 0..1 or 0..100
    if v is None:
        return None
    v = float(v)
    if v > 1.000001:  # treat as percentage
        return max(0.0, min(1.0, v/100.0))
    return max(0.0, min(1.0, v))

def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))

def util_latency(ms, cfg):
    target = float(cfg['target_ms'])
    k = float(cfg['k_ms'])
    return max(0.0, min(1.0, 1.0 - sigmoid((ms - target)/k)))

def util_failure(rate, cfg):
    target = float(cfg['target_rate'])
    k = float(cfg['k_rate'])
    return max(0.0, min(1.0, 1.0 - sigmoid((rate - target)/k)))

def util_linear_minmax(x, mn, mx):
    if mx <= mn:
        return 0.0
    return max(0.0, min(1.0, (x - mn) / (mx - mn)))

def enforce_constraints(m, acc):
    ok = True
    reasons = []
    if 'max_p95_latency_ms' in acc and m['latency_ms'] > acc['max_p95_latency_ms']:
        ok = False; reasons.append(f"latency_ms>{acc['max_p95_latency_ms']}")
    if 'min_accuracy' in acc and m['accuracy'] < acc['min_accuracy']:
        ok = False; reasons.append(f"accuracy<{acc['min_accuracy']}")
    if 'min_explainability' in acc and m['explainability'] < acc['min_explainability']:
        ok = False; reasons.append(f"explainability<{acc['min_explainability']}")
    if 'max_failure_rate' in acc and m['failure_rate'] > acc['max_failure_rate']:
        ok = False; reasons.append(f"failure_rate>{acc['max_failure_rate']}")
    return ok, reasons

def load_metrics(path):
    with open(path, "r", encoding="utf-8") as f:
        m = json.load(f)
    # normalize
    m2 = {
        "latency_ms": float(m.get("latency_ms") or m.get("p95_latency_ms") or m.get("latency")),
        "accuracy": to01(m.get("accuracy")),
        "explainability": to01(m.get("explainability")),
        "failure_rate": float(m.get("failure_rate"))
    }
    if any(v is None for v in m2.values()):
        raise ValueError("metrics must include latency_ms, accuracy, explainability, failure_rate")
    return m2

def main():
    ap = argparse.ArgumentParser(description="Compute J given metrics and objective config")
    ap.add_argument("--metrics", required=True, help="JSON file with latency_ms, accuracy, explainability, failure_rate")
    ap.add_argument("--config", required=True, help="YAML file objective_params.yaml")
    ap.add_argument("--weight_preset", default="balanced", help="weights key in YAML (balanced/speed/quality/safety_first)")
    args = ap.parse_args()

    m = load_metrics(args.metrics)
    cfg = yaml.safe_load(open(args.config, "r", encoding="utf-8"))
    w = cfg["weights"].get(args.weight_preset)
    if not w:
        raise SystemExit(f"weight preset '{args.weight_preset}' not found")
    t = cfg["objective"]["transforms"]

    # utilities 0..1
    u_lat = util_latency(m["latency_ms"], t["latency"])
    u_acc = util_linear_minmax(m["accuracy"], t["accuracy"]["min"], t["accuracy"]["max"])
    u_exp = util_linear_minmax(m["explainability"], t["explainability"]["min"], t["explainability"]["max"])
    u_fail = util_failure(m["failure_rate"], t["failure"])

    # sanity
    ok, reasons = enforce_constraints(m, cfg.get("acceptance_criteria", {}))

    # weighted sum
    J = (
        w["latency"] * u_lat
        + w["accuracy"] * u_acc
        + w["explainability"] * u_exp
        + w["failure"] * u_fail
    )

    out = {
        "metrics": m,
        "utilities": {
            "latency": u_lat,
            "accuracy": u_acc,
            "explainability": u_exp,
            "failure": u_fail
        },
        "weights": w,
        "J": J,
        "constraints_ok": ok,
        "violations": reasons
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
