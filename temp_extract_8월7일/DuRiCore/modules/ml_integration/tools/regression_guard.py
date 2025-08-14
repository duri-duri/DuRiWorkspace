#!/usr/bin/env python3
# Writes detailed rejection reasons as a JSON artifact.
import argparse, json, os, time

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--reason", required=True)
    ap.add_argument("--details", default="{}",
                    help='JSON string, e.g. {"mse_ratio":1.9}')
    ap.add_argument("--outdir", default="artifacts_phase1/rejections")
    args=ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    ts=int(time.time())
    outp=os.path.join(args.outdir, f"rejection_{ts}.json")
    try:
        details=json.loads(args.details)
    except Exception:
        details={"raw": args.details}
    payload={
        "ts": ts,
        "reason": args.reason,
        "details": details
    }
    with open(outp,"w",encoding="utf-8") as f:
        json.dump(payload,f,ensure_ascii=False,indent=2)
    print(f"[OK] wrote {outp}")

if __name__=="__main__":
    main()

