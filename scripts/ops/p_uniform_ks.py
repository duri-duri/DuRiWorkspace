#!/usr/bin/env python3
# (v) KS-Uniform 품질검정
import os, glob, re, math

try:
    from scipy import stats
    has_scipy = True
except ImportError:
    has_scipy = False

def vals(pattern):
    out = []
    for f in glob.glob(pattern):
        try:
            for line in open(f):
                m = re.match(r'^p_value\s+([0-9.]+)', line)
                if m:
                    out.append(float(m.group(1)))
        except:
            pass
    return out

def safe(v, lo=1e-12, hi=1-1e-12):
    return min(hi, max(lo, v))

root = os.getcwd()
tdir = os.environ.get("TEXTFILE_DIR", os.path.join(root, ".reports/synth"))
out = os.path.join(tdir, "p_uniform_ks.prom")

os.makedirs(tdir, exist_ok=True)

tmp_out = f"{out}.{os.getpid()}"

with open(tmp_out, "w") as w:
    w.write("# HELP duri_p_uniform_ks_stat KS statistic for uniform distribution\n")
    w.write("# TYPE duri_p_uniform_ks_stat gauge\n")
    w.write("# HELP duri_p_uniform_ks_p KS test p-value\n")
    w.write("# TYPE duri_p_uniform_ks_p gauge\n")
    
    for w_name in ("2h", "24h"):
        xs = vals(f"{tdir}/p_values_{w_name}.prom")
        if xs and len(xs) > 2:
            xs_safe = [safe(p) for p in xs]
            if has_scipy:
                d, p_ks = stats.kstest(xs_safe, 'uniform')
            else:
                # 간단한 KS 통계 계산 (scipy 없이)
                xs_sorted = sorted(xs_safe)
                n = len(xs_sorted)
                d = 0.0
                for i, x in enumerate(xs_sorted):
                    d = max(d, abs((i+1)/n - x), abs(i/n - x))
                # p-value는 근사치 생략 (NaN으로 표시)
                p_ks = float('nan')
            w.write(f'duri_p_uniform_ks_stat{{window="{w_name}"}} {d}\n')
            w.write(f'duri_p_uniform_ks_p{{window="{w_name}"}} {p_ks}\n')
        else:
            w.write(f'duri_p_uniform_ks_stat{{window="{w_name}"}} NaN\n')
            w.write(f'duri_p_uniform_ks_p{{window="{w_name}"}} NaN\n')

os.rename(tmp_out, out)

print(f"[OK] KS-Uniform test exported -> {out}")

