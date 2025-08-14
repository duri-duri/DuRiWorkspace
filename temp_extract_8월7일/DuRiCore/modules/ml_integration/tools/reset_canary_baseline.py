#!/usr/bin/env python3
import json, argparse
from pathlib import Path

ART = Path("artifacts_phase1")
LEAGUE = ART / "league.jsonl"
CANARY = ART / "canary_metrics_baseline.json"

def best_from_league():
    if not LEAGUE.exists():
        return None
    best = None
    with LEAGUE.open() as f:
        for line in f:
            line=line.strip()
            if not line: continue
            row = json.loads(line)
            m = row.get("metrics", {})
            t = m.get("test", {})
            r2 = t.get("r2")
            mse = t.get("mse")
            if r2 is None or mse is None: 
                continue
            if best is None or r2 > best[0] or (r2==best[0] and mse<best[1]):
                best = (r2, mse)
    return best

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--r2", type=float, default=None, help="Override R2 (optional)")
    p.add_argument("--mse", type=float, default=None, help="Override MSE (optional)")
    args = p.parse_args()

    pair = None
    if args.r2 is not None and args.mse is not None:
        pair = (args.r2, args.mse)
    else:
        # league에서 최고 test R2를 기준선으로 복원(권장)
        pair = best_from_league()
        if pair is None:
            raise SystemExit("no league.jsonl available; pass --r2 and --mse explicitly")

    CANARY.write_text(json.dumps({"r2": pair[0], "mse": pair[1]}, indent=2), encoding="utf-8")
    print(f"[RESET] canary baseline -> r2={pair[0]:.4f}, mse={pair[1]:.6f}  ({CANARY})")

if __name__ == "__main__":
    main()

