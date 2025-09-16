#!/usr/bin/env python3
import os, json, math, csv, subprocess
from pathlib import Path
from datetime import datetime, timezone

CFG = "configs/monitoring.yaml"

def load_cfg():
    import yaml
    with open(CFG, encoding="utf-8") as f: return yaml.safe_load(f)

def eval_J(evaluator, cfg, preset, m):
    import tempfile
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json", encoding="utf-8") as tf:
        json.dump(m, tf); tmp = tf.name
    try:
        out = subprocess.check_output(["python", evaluator, "--metrics", tmp, "--config", cfg, "--weight_preset", preset], text=True)
        return json.loads(out)["J"]
    finally:
        os.remove(tmp)

def finite_diff_sensitivity(evaluator, cfg, preset, m, delta=0.05):
    # w_fail ±δ 로 목적함수 preset 임시 수정은 불가 → 메트릭 기반 근사치:
    # 실패율에 대한 J의 국소 민감도: J(m)와 J(m') 비교 (m'의 failure_rate를 ε 변화시켜 근사)
    # 여기선 정책 가중치가 아니라 메트릭 변동 민감도(운영 의사결정에 충분)
    eps = 0.001
    J0 = eval_J(evaluator, cfg, preset, m)
    m2 = dict(m); m2["failure_rate"] = max(0.0, min(1.0, m["failure_rate"] + eps))
    J1 = eval_J(evaluator, cfg, preset, m2)
    dJ_dfail = (J1 - J0) / eps
    # latency 민감도도 같이
    m3 = dict(m); m3["latency_ms"] = m["latency_ms"] + 50.0
    J2 = eval_J(evaluator, cfg, preset, m3)
    dJ_dlat50 = (J2 - J0) / 50.0
    return J0, dJ_dfail, dJ_dlat50

def main():
    cfg = load_cfg()
    series_dir = Path(cfg["outdir"]["series"])
    outdir = Path(cfg["outdir"]["daily"]); outdir.mkdir(parents=True, exist_ok=True)

    lines = ["# Day38 Daily Ops Report", f"Generated: {datetime.now(timezone.utc).isoformat()}",
             "", "| Domain | last_ts | n | p95_latency | acc | explain | fail_rate | J | ∂J/∂fail | ∂J/∂lat(ms) |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for dom in cfg["domains"]:
        f = series_dir / f"{dom}.csv"
        if not f.exists(): 
            lines.append(f"| {dom} | - | 0 | - | - | - | - | - | - | - |")
            continue
        *_, last = open(f, encoding="utf-8").read().strip().splitlines()
        hdr, row = None, None
        with open(f, encoding="utf-8") as fh:
            rdr = csv.DictReader(fh)
            rows = list(rdr)
            if not rows: 
                lines.append(f"| {dom} | - | 0 | - | - | - | - | - | - | - |")
                continue
            r = rows[-1]
        m = {
          "latency_ms": float(r["latency_ms_p95"]),
          "accuracy": float(r["accuracy_mean"]),
          "explainability": float(r["explain_mean"]),
          "failure_rate": float(r["failure_rate"]),
        }
        J0, dJ_dfail, dJ_dlat = finite_diff_sensitivity(
            cfg["objective"]["evaluator"], cfg["objective"]["config"], cfg["objective"]["weight_preset"], m)
        lines.append(f'| {dom} | {r["ts_utc"]} | {r["n"]} | {r["latency_ms_p95"]} | {float(r["accuracy_mean"]):.3f} | {float(r["explain_mean"]):.3f} | {float(r["failure_rate"]):.4f} | {float(r["J"]):.4f} | {dJ_dfail:.3f} | {dJ_dlat:.6f} |')

    (outdir / "daily_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {outdir/'daily_report.md'}")

if __name__ == "__main__":
    main()
