#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import itertools, json, pathlib, subprocess, sys, time, shutil
from datetime import datetime
try:
    import yaml
except Exception:
    print("[ERR] PyYAML required: pip install pyyaml", file=sys.stderr); raise

ROOT = pathlib.Path(__file__).resolve().parents[1]
CFG  = ROOT / "configs" / "trace_v2_sweep.yaml"
EVAL = ROOT / "eval" / "metrics.yaml"

def atomic_write(p: pathlib.Path, text: str):
    tmp = p.with_suffix(p.suffix + ".tmp"); tmp.write_text(text, encoding="utf-8"); tmp.replace(p)

def run_cmd(cmd: str):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0: raise RuntimeError(f"cmd failed: {cmd}\n{r.stderr}")
    return r.stdout.strip()

def bench_cmd():
    cmd = os.environ.get("TRACE_BENCH_CMD")
    if cmd:
        return cmd
    # Only allow PATH resolution if user installed a real bench there.
    path_cmd = shutil.which("trace_bench")
    if path_cmd:
        return path_cmd
    print("[ERR] TRACE_BENCH_CMD not set and no trace_bench on PATH. No dummy allowed.", file=sys.stderr)
    sys.exit(2)

def assert_real_bench(cmd: str):
    # Contract: prefer --self-check, else --version content check
    try:
        out = subprocess.run([cmd, "--self-check"], capture_output=True, text=True, timeout=5)
        if out.returncode == 0 and out.stdout.startswith("TRACE_BENCH_OK:"):
            return
    except Exception:
        pass
    try:
        out = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=5)
        ver = (out.stdout or out.stderr).strip()
        if (not ver) or ("dummy" in ver.lower()) or ("simulator" in ver.lower()) or ("[bench]" in ver.lower()):
            raise RuntimeError(f"suspect version: {ver!r}")
    except Exception as e:
        print(f"[ERR] real bench verification failed: {e}", file=sys.stderr)
        sys.exit(3)

def load_slo_metrics(path: pathlib.Path):
    d = json.loads(path.read_text(encoding="utf-8"))
    base_p95 = float(d.get("baseline_p95_ms") or d.get("p95_ms") or 750.0)
    base_size = float(d.get("baseline_size_kb", 100.0))
    req = float(d.get("requests", 0.0)); fail = float(d.get("failures", 0.0))
    base_err = (fail/max(1.0, req)) if req > 0 else float(d.get("baseline_error_rate", 0.0))
    return base_p95, base_err, base_size

def validate_policy(w, T_over, T_err):
    if not (0.0 < T_over <= 0.20):  # ≤20%
        raise ValueError(f"max_overhead_pct out of range: {T_over*100:.2f}%")
    if not (0.0 <= T_err <= 0.02):  # ≤2%
        raise ValueError(f"max_error_rate out of range: {T_err:.4f}")
    if not (0.0 <= w["overhead"] <= 1.0 and 0.0 <= w["error"] <= 1.0 and 0.0 <= w["size"] <= 1.0):
        raise ValueError("weights must be in [0,1]")
    s = max(1e-9, (w["overhead"] + w["error"] + w["size"]))
    for k in list(w.keys()): w[k] = w[k] / s
    return w

def main():
    # Verify real bench before starting sweep
    cmd = bench_cmd()
    assert_real_bench(cmd)
    
    cfg = yaml.safe_load(CFG.read_text(encoding="utf-8"))
    eval_cfg = yaml.safe_load(EVAL.read_text(encoding="utf-8"))
    slo_path = ROOT / cfg["io"]["slo_metrics_json"]
    out_dir  = ROOT / cfg["io"]["out_dir"]; out_dir.mkdir(parents=True, exist_ok=True)
    base_p95, base_err, base_size = load_slo_metrics(slo_path)
    tcfg = (eval_cfg.get("trace_v2") or {}).get("tuning") or {}
    T_over = float(tcfg.get("max_overhead_pct", 5.0)) / 100.0
    T_err  = float(tcfg.get("max_error_rate", 0.005))
    W = dict(tcfg.get("weight") or {"overhead":0.6, "error":0.3, "size":0.1})
    W = validate_policy(W, T_over, T_err)
    policy = dict(tcfg.get("policy") or {})
    grid = cfg["grid"]
    levels = list(itertools.product(grid["sampling_rate"], grid["serialization"], grid["compression"]))
    ts = datetime.utcnow().isoformat() + "Z"
    sweep_id = f"sweep_{int(time.time())}"; sweep_dir = out_dir / sweep_id; sweep_dir.mkdir(parents=True, exist_ok=True)
    results, best = [], None
    for i, (samp, ser, comp) in enumerate(levels, 1):
        out_json = sweep_dir / f"res_{i:03d}.json"
        cmd_template = cfg["runner"]["cmd"]
        cmd = cmd_template.format(sampling_rate=samp, serialization=ser, compression=comp, out_json=str(out_json))
        run_cmd(cmd)
        d = json.loads(out_json.read_text(encoding="utf-8"))
        p95  = float(d["p95_ms"]); err = float(d.get("error_rate", 0.0)); size = float(d.get("size_kb", 0.0))
        overhead = max(0.0, (p95 - base_p95) / base_p95); size_inc = max(0.0, (size / base_size) - 1.0)
        feasible = (overhead <= T_over) and (err <= T_err)
        J = W["overhead"]*overhead + W["error"]*err + W["size"]*size_inc + (0.5 if not feasible else 0.0)
        rec = {"sampling_rate": samp, "serialization": ser, "compression": comp,
               "p95_ms": p95, "overhead": overhead, "error_rate": err, "size_kb": size,
               "feasible": feasible, "J": J, "out_file": str(out_json)}
        results.append(rec);  best = rec if (best is None or rec["J"] < best["J"]) else best
    summary = {"schema_version":"trace_tune.v2","generated_at":ts,
               "source":{"sweep_cfg":str(CFG),"eval_metrics":str(EVAL),"slo_metrics":str(slo_path)},
               "baseline":{"p95_ms":base_p95,"error_rate":base_err,"size_kb":base_size},
               "target":{"max_overhead_pct":T_over*100,"max_error_rate":T_err,"weight":W,"policy":policy},
               "total_runs":len(results),"best":best,"results":results}
    atomic_write(sweep_dir / "summary.json", json.dumps(summary, ensure_ascii=False, indent=2))
    md = [f"# Trace v2 Sweep Report — {ts}",
          f"- Baseline p95: **{base_p95:.2f} ms**, size: **{base_size:.1f} KB**",
          f"- Target: overhead ≤ **{T_over*100:.1f}%**, error_rate ≤ **{T_err:.3%}**, weight={W}",
          f"- Total runs: **{len(results)}**","## Best Config",
          f"- sampling_rate: **{best['sampling_rate']}**, serialization: **{best['serialization']}**, compression: **{best['compression']}**",
          f"- p95: **{best['p95_ms']:.2f} ms** (over {best['overhead']*100:.2f}%)",
          f"- error_rate: **{best['error_rate']:.4%}**, size: **{best['size_kb']:.1f} KB**",
          f"- J(score): **{best['J']:.6f}**, feasible: **{best['feasible']}**","## Top-5 by J"]
    for r in sorted(results, key=lambda x: x["J"])[:5]:
        md.append(f"- {r['sampling_rate']}, {r['serialization']}, {r['compression']} → "
                  f"p95={r['p95_ms']:.2f}ms, over={r['overhead']*100:.2f}%, err={r['error_rate']:.3%}, size={r['size_kb']:.1f}KB, J={r['J']:.6f}, feas={r['feasible']}")
    atomic_write(sweep_dir / "report.md", "\n".join(md))
    print(json.dumps({"sweep_dir": str(sweep_dir), "best": best}, ensure_ascii=False))

if __name__ == "__main__":
    main()
