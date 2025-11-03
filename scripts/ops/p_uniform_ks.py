#!/usr/bin/env python3
import os, glob, re, math, tempfile, shutil

from statistics import NormalDist

TEXTFILE_DIR = os.environ.get("TEXTFILE_DIR", ".reports/synth")
OUT = os.path.join(TEXTFILE_DIR, "p_uniform_ks.prom")
WINDOWS = ("2h","24h")
ROUND_DP = int(os.environ.get("P_DEDUP_ROUND_DP", "8"))  # unique(8dp) 기본

def read_p_values(path_glob):
    xs=[]
    for f in glob.glob(path_glob):
        with open(f) as fd:
            for line in fd:
                m=re.match(r'^p_value\s+([0-9.]+)', line)
                if m: xs.append(float(m.group(1)))
    return xs

def ks_statistic_uniform(xs):
    # 두 방향 supremum
    n=len(xs)
    if n==0: return float('nan')
    ys=sorted(xs)
    d_plus=max((i+1)/n - y for i,y in enumerate(ys))
    d_minus=max(y - i/n for i,y in enumerate(ys))
    return max(d_plus,d_minus)

def clamp(p): return max(1e-12, min(1-1e-12, p))

def ks_pvalue_asymptotic(d, n):
    # Kolmogorov 분포 근사 (Smirnov), n>0, d>=0
    if n==0 or not math.isfinite(d): return float('nan')
    en = math.sqrt(n)
    x = (en + 0.12 + 0.11/en) * d
    # 빠른 합 근사
    s = 0.0
    for k in range(1, 101):
        term = (-1)**(k-1) * math.exp(-2*(k*k)*(x*x))
        s += term
        if abs(term) < 1e-12: break
    return max(0.0, min(1.0, 2*s))

def unique_ratio(xs, dp=8):
    if not xs: return float('nan')
    tot=len(xs)
    uniq=len({round(v, dp) for v in xs})
    return uniq/tot

def atomic_write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=os.path.dirname(path)) as tmp:
        tmp.write(text)
        tmp.flush(); os.fsync(tmp.fileno())
    shutil.move(tmp.name, path)

def main():
    lines=[]
    for w in WINDOWS:
        xs = [clamp(v) for v in read_p_values(os.path.join(TEXTFILE_DIR, f"p_values_{w}.prom"))]
        n = len(xs)
        if n>0:
            d = ks_statistic_uniform(xs)
            p = ks_pvalue_asymptotic(d, n)
            ur = unique_ratio(xs, ROUND_DP)
        else:
            d = float('nan'); p = float('nan'); ur = float('nan')

        lines += [
            "# HELP duri_p_uniform_ks KS statistic vs U(0,1)",
            "# TYPE duri_p_uniform_ks gauge",
            f'duri_p_uniform_ks{{window="{w}"}} {d}',
            "# HELP duri_p_uniform_ks_p Asymptotic p-value of KS",
            "# TYPE duri_p_uniform_ks_p gauge",
            f'duri_p_uniform_ks_p{{window="{w}"}} {p}',
            "# HELP duri_p_unique_ratio unique(8dp)/total ratio",
            "# TYPE duri_p_unique_ratio gauge",
            f'duri_p_unique_ratio{{window="{w}"}} {ur}',
            ""
        ]
    atomic_write(OUT, "\n".join(lines))
    print(f"[OK] KS/unique exported -> {OUT}")

if __name__=="__main__":
    main()
