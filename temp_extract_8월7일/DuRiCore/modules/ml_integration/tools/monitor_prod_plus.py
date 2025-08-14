#!/usr/bin/env python3
# Lightweight add-on monitor: reads thresholds.yaml, prints alert-level,
# and optionally posts to Slack via SLACK_WEBHOOK_URL.
import argparse, json, os, sys, datetime
from typing import Dict, Any
try:
    import yaml, requests, pytz
except Exception as e:
    print("[WARN] missing deps; install: pip install PyYAML requests pytz", file=sys.stderr)
    raise

def load_yaml(p:str)->Dict[str,Any]:
    with open(p,"r",encoding="utf-8") as f:
        return yaml.safe_load(f)

def classify(metrics:Dict[str,float], th:Dict[str,Any])->str:
    # hard-fail first
    hf = th.get("hard_fail",{})
    if (metrics.get("nrmse_ratio",0)>hf.get("nrmse_ratio",1e9)) or \
       (metrics.get("mse_ratio",0)>hf.get("mse_ratio",1e9)):
        return "hard-fail"
    alert = th.get("alert",{})
    crit = alert.get("crit",{})
    warn = alert.get("warn",{})
    if (metrics.get("nrmse_ratio",0)>crit.get("nrmse_ratio",1e9)) or \
       (metrics.get("mse_ratio",0)>crit.get("mse_ratio",1e9)) or \
       (metrics.get("r2_gap",0)>crit.get("r2_gap",1e9)):
        return "crit"
    if (metrics.get("nrmse_ratio",0)>warn.get("nrmse_ratio",1e9)) or \
       (metrics.get("mse_ratio",0)>warn.get("mse_ratio",1e9)) or \
       (metrics.get("r2_gap",0)>warn.get("r2_gap",1e9)):
        return "warn"
    return "ok"

def slack_post(text:str):
    url=os.environ.get("SLACK_WEBHOOK_URL","").strip()
    if not url: return
    try:
        requests.post(url, json={"text": text}, timeout=5)
    except Exception as e:
        print(f"[WARN] slack post failed: {e}", file=sys.stderr)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="registry/current.json")
    ap.add_argument("--out", required=True, help="output json path")
    ap.add_argument("--thresholds", default="configs/thresholds.yaml")
    ap.add_argument("--tz", default="UTC")
    ap.add_argument("--alert-level", default="", choices=["","ok","warn","crit","hard-fail"])
    args=ap.parse_args()

    tz=pytz.timezone(args.tz)
    now=datetime.datetime.now(tz).isoformat()

    with open(args.model,"r",encoding="utf-8") as f:
        model=json.load(f)

    # minimal metric extraction (fallback-safe)
    meta=model.get("meta",{})
    gap=meta.get("gap",{})
    metrics={
        "nrmse_ratio": float(gap.get("nrmse_ratio", 0)),
        "mse_ratio": float(gap.get("mse_ratio", 0)),
        "r2_gap": float(gap.get("r2_gap", 0)),
    }
    th=load_yaml(args.thresholds)
    level=classify(metrics, th)
    if args.alert_level and args.alert_level!=level:
        # explicit filter: if user asked for specific level, only emit when matching
        print(f"[SKIP] computed={level} but --alert-level={args.alert_level}")
        return

    out={
        "ts": now,
        "model": os.path.abspath(args.model),
        "metrics": metrics,
        "level": level,
        "thresholds": th.get("alert",{})
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out,"w",encoding="utf-8") as f:
        json.dump(out,f,ensure_ascii=False,indent=2)

    msg=f"📈 monitor @ {now}\nlevel={level} metrics={metrics}"
    print(msg)
    if level in ("warn","crit","hard-fail"):
        slack_post(f":rotating_light: {msg}")
    elif level=="ok":
        slack_post(f":white_check_mark: {msg}")

if __name__=="__main__":
    main()

