#!/usr/bin/env python3
# Minimal A/B significance check on J using Welch's t-test
import argparse
import glob
import json
import math
import statistics as stats


def load_J_values(paths):
    vals = []
    for p in paths:
        with open(p, "r", encoding="utf-8") as f:
            d = json.load(f)
        vals.append(float(d["J"]))
    return vals


def welch_t_test(a, b):
    mean_a, mean_b = stats.mean(a), stats.mean(b)
    var_a, var_b = stats.pvariance(a), stats.pvariance(b)
    na, nb = len(a), len(b)
    t = (mean_a - mean_b) / math.sqrt(var_a / na + var_b / nb)
    # df approximation (Welch–Satterthwaite)
    df = ((var_a / na + var_b / nb) ** 2) / (
        (var_a**2) / ((na**2) * (na - 1)) + (var_b**2) / ((nb**2) * (nb - 1))
    )
    return t, df, mean_a, mean_b


def main():
    ap = argparse.ArgumentParser(description="AB t-test on J values")
    ap.add_argument(
        "--glob_a",
        required=True,
        help="glob for variant A JSONs (evaluate_objective outputs)",
    )
    ap.add_argument("--glob_b", required=True, help="glob for variant B JSONs")
    args = ap.parse_args()

    A = load_J_values(glob.glob(args.glob_a))
    B = load_J_values(glob.glob(args.glob_b))
    if len(A) < 2 or len(B) < 2:
        raise SystemExit("Need ≥2 samples per variant")
    t, df, ma, mb = welch_t_test(A, B)
    # p-value via survival function approximation (two-sided) using Student-t needs SciPy; we output t, df only.
    out = {
        "n_A": len(A),
        "n_B": len(B),
        "mean_A": ma,
        "mean_B": mb,
        "t_stat": t,
        "df": df,
        "note": "Compute p-value externally or compare |t|>2 as heuristic (~p<0.05 for large df).",
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
