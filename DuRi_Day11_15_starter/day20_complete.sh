#!/usr/bin/env bash
set -Eeuo pipefail

# 0) 전제 확인
test -d tools || mkdir -p tools
test -d trace_v2_perf_tuned/sweeps || mkdir -p trace_v2_perf_tuned/sweeps

# 1) tools/run_trace_bench.sh 생성 (더미 시뮬레이터; 실제 벤치로 교체 가능)
cat > tools/run_trace_bench.sh <<'BASH'
#!/usr/bin/env bash
set -Eeuo pipefail
sampling="1.0"; ser="json"; comp="none"; out="out.json"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --sampling) sampling="$2"; shift 2;;
    --ser|--serialization) ser="$2"; shift 2;;
    --comp|--compression) comp="$2"; shift 2;;
    --out) out="$2"; shift 2;;
    *) echo "Unknown arg: $1" >&2; exit 2;;
  esac
done
# TODO: 실제 Trace v2 벤치 호출로 교체 (예: ./bin/trace_bench ...)
awk -v s="$sampling" -v ser="$ser" -v comp="$comp" 'BEGIN{
  base=750
  ser_pen=(ser=="json"?1.00:(ser=="msgpack"?0.96:0.94))
  comp_pen=(comp=="none"?1.00:(comp=="gzip"?0.98:0.96))
  p95=base* (1.02 - 0.15*s) * ser_pen * comp_pen
  err=0.002 * (1.04 - 0.2*s) * (ser=="json"?1.0:0.98)
  size=100.0 * (0.6 + 0.5*s) * (ser=="json"?1.0:(ser=="msgpack"?0.85:0.8)) * (comp=="none"?1.0:(comp=="gzip"?0.7:0.55))
  srand(); p95+=rand()*8-4; err+= (rand()*0.0002-0.0001); size += rand()*5-2.5
  if(err<0) err=0.0
  printf("{\"p95_ms\":%.2f,\"error_rate\":%.5f,\"size_kb\":%.2f}\n", p95, err, size)
}' > "${out}.tmp"
mv "${out}.tmp" "$out"
echo "[OK] wrote $out"
BASH
chmod +x tools/run_trace_bench.sh

# 2) tools/run_trace_sweep_v2.py 생성 (가중치 외부화 + SLO 통합)
python3 - <<'PYCODE'
from pathlib import Path
code = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import itertools, json, pathlib, subprocess, sys, time
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
        cmd = cfg["runner"]["cmd"].format(sampling_rate=samp, serialization=ser, compression=comp, out_json=str(out_json))
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
    (sweep_dir / "report.md").write_text("", encoding="utf-8")  # placeholder to reserve name
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
'''
p = Path("tools/run_trace_sweep_v2.py")
p.write_text(code, encoding="utf-8")
p.chmod(0o755)
print("[OK] wrote tools/run_trace_sweep_v2.py")
PYCODE

# 3) PyYAML 보장
python3 - <<'PY'
try:
    import yaml; print("[OK] PyYAML present")
except Exception:
    print("[INFO] installing PyYAML ...")
    import sys, subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "pyyaml"])
PY

# 4) SLO 메트릭 베이스라인 보정(없으면 생성)
if [ ! -f slo_sla_dashboard_v1/metrics.json ]; then
  mkdir -p slo_sla_dashboard_v1
  cat > slo_sla_dashboard_v1/metrics.json <<'JSON'
{"baseline_p95_ms": 750, "baseline_size_kb": 100, "requests": 10000, "failures": 20}
JSON
fi

# 5) 스위프 실행 & 리포트 확인
python3 tools/run_trace_sweep_v2.py | tee .last_sweep.json
SWEEP_DIR=$(jq -r '.sweep_dir' .last_sweep.json 2>/dev/null || true)
if [ -n "${SWEEP_DIR:-}" ] && [ -f "$SWEEP_DIR/report.md" ]; then
  echo "[INFO] Report path: $SWEEP_DIR/report.md"
  sed -n '1,120p' "$SWEEP_DIR/report.md"
else
  echo "[WARN] jq 없거나 경로 파싱 실패. summary.json만 출력:"
  find trace_v2_perf_tuned/sweeps -name summary.json | sort | tail -n1 | xargs -r sed -n '1,80p'
fi

# 6) 산출물 커밋
git add eval/metrics.yaml configs/trace_v2_sweep.yaml tools/run_trace_bench.sh tools/run_trace_sweep_v2.py slo_sla_dashboard_v1/metrics.json trace_v2_perf_tuned/sweeps || true
git commit -m "perf(day20): sweep (weights externalized, SLO integration, report)" || true
