#!/usr/bin/env python3
# Compute Pareto front for candidates using 4 objectives in utility space (higher is better).
import json, argparse, math, glob

def is_dominated(a, b):
    # a, b dict of utilities: latency, accuracy, explainability, failure
    better_or_equal = all(b[k] >= a[k] for k in a.keys())
    strictly_better = any(b[k] > a[k] for k in a.keys())
    return better_or_equal and strictly_better

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", nargs="+", help="JSON files produced by evaluate_objective.py", required=True)
    args = ap.parse_args()

    items = []
    for p in args.inputs:
        d = json.load(open(p, "r", encoding="utf-8"))
        items.append({"path": p, "J": d["J"], "utilities": d["utilities"], "metrics": d["metrics"], "weights": d["weights"]})

    front = []
    for i, a in enumerate(items):
        dominated = False
        for j, b in enumerate(items):
            if i != j and is_dominated(a["utilities"], b["utilities"]):
                dominated = True
                break
        if not dominated:
            front.append(a)

    # Sort by J desc for convenience
    front.sort(key=lambda x: x["J"], reverse=True)
    print(json.dumps(front, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
