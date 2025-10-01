#!/usr/bin/env python3
import argparse
from collections import defaultdict
import csv
from datetime import datetime, timedelta, timezone
import glob
import json
import os
from pathlib import Path
from statistics import mean
import subprocess
import time


def load_cfg(p):
    import yaml

    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_jsonl(path):
    with open(path, encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            try:
                yield json.loads(ln)
            except Exception:
                yield json.loads(ln.replace(": .", ": 0."))


def norm(rec):
    # 표준 키 정규화
    lat = rec.get("p95_latency_ms") or rec.get("latency_ms") or rec.get("latency") or 0
    acc = rec.get("accuracy", 0)
    exp = rec.get("explainability", rec.get("explain", 0))
    status = rec.get("status", "ok")
    fail = 1.0 if status not in {"ok", "success"} else 0.0
    ts = rec.get("timestamp")  # ISO
    return {
        "ts": ts,
        "latency_ms": float(lat),
        "accuracy": float(acc),
        "explainability": float(exp),
        "failure": float(fail),
    }


def bin_key(ts_iso, bin_minutes):
    dt = datetime.fromisoformat(ts_iso.replace("Z", "+00:00")).astimezone(timezone.utc)
    minute = (dt.minute // bin_minutes) * bin_minutes
    dt2 = dt.replace(minute=0, second=0, microsecond=0) + timedelta(minutes=minute)
    return dt2.replace(tzinfo=timezone.utc)


def p95(xs):
    if not xs:
        return 0.0
    xs = sorted(xs)
    k = max(0, min(len(xs) - 1, int(round(0.95 * (len(xs) - 1)))))
    return float(xs[k])


def write_json(p, obj):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def append_series_csv(path, row_dict, header):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    new = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=header)
        if new:
            w.writeheader()
        w.writerow(row_dict)


def eval_J(evaluator, cfg, preset, metrics_dict):
    # evaluator는 example_metrics.json 형태를 받으므로 temp로 전달
    import json
    import tempfile

    with tempfile.NamedTemporaryFile(
        "w", delete=False, suffix=".json", encoding="utf-8"
    ) as tf:
        json.dump(metrics_dict, tf)
        tmp = tf.name
    try:
        cmd = [
            "python",
            evaluator,
            "--metrics",
            tmp,
            "--config",
            cfg,
            "--weight_preset",
            preset,
        ]
        out = subprocess.check_output(cmd, text=True)
        return json.loads(out)["J"]
    finally:
        try:
            os.remove(tmp)
        except:
            pass


def run_once(cfg):
    now = datetime.now(timezone.utc)
    bin_minutes = cfg["bin_minutes"]
    bins_out = Path(cfg["outdir"]["bins"])
    series_out = Path(cfg["outdir"]["series"])
    alerts_out = Path(cfg["outdir"]["alerts"])
    objective = cfg["objective"]

    for dom in cfg["domains"]:
        files = []
        for pat in cfg["log_globs"][dom].split(","):
            files.extend(glob.glob(pat.strip()))
        by_bin = defaultdict(list)
        for fp in files:
            for rec in parse_jsonl(fp):
                if not rec.get("timestamp"):
                    continue
                r = norm(rec)
                by_bin[bin_key(r["ts"], bin_minutes)].append(r)

        # 최신 bin만 처리(직전 bin까지 확정)
        if not by_bin:
            continue
        latest_complete = max(by_bin.keys())
        rows = by_bin[latest_complete]
        lat_list = [r["latency_ms"] for r in rows]
        acc_list = [r["accuracy"] for r in rows]
        exp_list = [r["explainability"] for r in rows]
        fail_list = [r["failure"] for r in rows]

        metrics = {
            "latency_ms_p95": p95(lat_list),
            "accuracy_mean": mean(acc_list) if acc_list else 0.0,
            "explain_mean": mean(exp_list) if exp_list else 0.0,
            "failure_rate": mean(fail_list) if fail_list else 0.0,
            "n": len(rows),
            "bin_start_utc": latest_complete.isoformat(),
        }
        # 목적함수 입력 형태로 매핑
        J = eval_J(
            objective["evaluator"],
            objective["config"],
            objective["weight_preset"],
            {
                "latency_ms": metrics["latency_ms_p95"],
                "accuracy": metrics["accuracy_mean"],
                "explainability": metrics["explain_mean"],
                "failure_rate": metrics["failure_rate"],
            },
        )
        metrics["J"] = J

        # 저장
        bin_file = bins_out / dom / f'{latest_complete.strftime("%Y%m%d_%H%M")}.json'
        write_json(bin_file, metrics)

        # 시계열 CSV 추가
        append_series_csv(
            series_out / f"{dom}.csv",
            {
                "ts_utc": metrics["bin_start_utc"],
                "n": metrics["n"],
                "latency_ms_p95": round(metrics["latency_ms_p95"], 3),
                "accuracy_mean": round(metrics["accuracy_mean"], 6),
                "explain_mean": round(metrics["explain_mean"], 6),
                "failure_rate": round(metrics["failure_rate"], 6),
                "J": round(J, 9),
            },
            header=[
                "ts_utc",
                "n",
                "latency_ms_p95",
                "accuracy_mean",
                "explain_mean",
                "failure_rate",
                "J",
            ],
        )

        # 알람
        al_cfg = cfg["alerts"]

        # 최근 k bins 확인
        def last_k(domain, k, key):
            path = series_out / f"{domain}.csv"
            if not path.exists():
                return []
            import pandas as pd

            df = pd.read_csv(path)
            return list(df[key].tail(k).values)

        alerts = []
        fr_seq = last_k(dom, al_cfg["fail_rate_persist_bins"], "failure_rate")
        if len(fr_seq) == al_cfg["fail_rate_persist_bins"] and all(
            x > al_cfg["fail_rate_p95_threshold"] for x in fr_seq
        ):
            alerts.append({"type": "FAIL_RATE_HIGH", "value_seq": fr_seq})
        lat_seq = last_k(dom, al_cfg["latency_persist_bins"], "latency_ms_p95")
        if len(lat_seq) == al_cfg["latency_persist_bins"] and all(
            x > al_cfg["latency_p95_ms_threshold"] for x in lat_seq
        ):
            alerts.append({"type": "LATENCY_HIGH", "value_seq": lat_seq})

        if alerts:
            event = {
                "ts_utc": now.isoformat(),
                "domain": dom,
                "bin_start_utc": metrics["bin_start_utc"],
                "alerts": alerts,
                "action_hint": (
                    "consider_canary_rollback"
                    if any(a["type"] == "FAIL_RATE_HIGH" for a in alerts)
                    else "monitor"
                ),
            }
            outp = alerts_out / dom / f'{now.strftime("%Y%m%d_%H%M%S")}.json'
            write_json(outp, event)
            print(f"[ALERT] {dom}: {alerts}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/monitoring.yaml")
    ap.add_argument("--loop", action="store_true", help="지속 실행(60s 주기)")
    args = ap.parse_args()

    cfg = load_cfg(args.config)
    os.makedirs(cfg["outdir"]["bins"], exist_ok=True)
    os.makedirs(cfg["outdir"]["series"], exist_ok=True)
    os.makedirs(cfg["outdir"]["alerts"], exist_ok=True)
    os.makedirs(cfg["outdir"]["daily"], exist_ok=True)

    if args.loop:
        while True:
            try:
                run_once(cfg)
            except Exception as e:
                print("[monitoring] error:", e)
            time.sleep(60)
    else:
        run_once(cfg)


if __name__ == "__main__":
    main()
