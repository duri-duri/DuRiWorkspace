#!/usr/bin/env python3
# B-5: 추가 지표 3종 (Entropy, Autocorr, Runs)
import os, glob, re, math, tempfile, shutil

TEXTFILE_DIR = os.environ.get("TEXTFILE_DIR", ".reports/synth")
OUT = os.path.join(TEXTFILE_DIR, "p_entropy_autocorr_runs.prom")
WINDOWS = ("2h","24h")

def read_p_values(path_glob):
    xs = []
    for f in glob.glob(path_glob):
        with open(f) as fd:
            for line in fd:
                m = re.match(r'^p_value\s+([0-9.]+)', line)
                if m:
                    xs.append(float(m.group(1)))
    return xs

def entropy_10bin(xs):
    """10-bin entropy (H)"""
    if len(xs) < 2:
        return float('nan')
    bins = [0] * 10
    for x in xs:
        idx = min(int(x * 10), 9)
        bins[idx] += 1
    total = len(xs)
    h = 0.0
    for count in bins:
        if count > 0:
            p = count / total
            h -= p * math.log(p)
    return h

def autocorr_lag1(xs):
    """Lag-1 autocorrelation"""
    if len(xs) < 3:
        return float('nan')
    mean = sum(xs) / len(xs)
    n = len(xs)
    numerator = sum((xs[i] - mean) * (xs[i+1] - mean) for i in range(n-1))
    denominator = sum((x - mean)**2 for x in xs)
    if denominator == 0:
        return float('nan')
    return numerator / denominator

def runs_test_p(xs):
    """Runs test p-value (Wald-Wolfowitz)"""
    if len(xs) < 3:
        return float('nan')
    median = sorted(xs)[len(xs)//2]
    runs = 1
    prev_sign = None
    for x in xs:
        sign = x > median
        if prev_sign is not None and sign != prev_sign:
            runs += 1
        prev_sign = sign
    n1 = sum(1 for x in xs if x > median)
    n2 = len(xs) - n1
    if n1 == 0 or n2 == 0:
        return float('nan')
    mean_runs = (2 * n1 * n2) / (n1 + n2) + 1
    var_runs = (2 * n1 * n2 * (2 * n1 * n2 - n1 - n2)) / ((n1 + n2)**2 * (n1 + n2 - 1))
    if var_runs <= 0:
        return float('nan')
    z = (runs - mean_runs) / math.sqrt(var_runs)
    # 간단한 정규분포 p-value 근사
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
    return max(0.0, min(1.0, p))

def atomic_write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=os.path.dirname(path)) as tmp:
        tmp.write(text)
        tmp.flush()
        os.fsync(tmp.fileno())
    shutil.move(tmp.name, path)

def main():
    lines = []
    for w in WINDOWS:
        xs = read_p_values(os.path.join(TEXTFILE_DIR, f"p_values_{w}.prom"))
        n = len(xs)
        if n > 0:
            h = entropy_10bin(xs)
            rho = autocorr_lag1(xs)
            runs_p = runs_test_p(xs)
        else:
            h = float('nan')
            rho = float('nan')
            runs_p = float('nan')
        
        lines += [
            "# HELP duri_p_entropy_10bin entropy (10 bins)",
            "# TYPE duri_p_entropy_10bin gauge",
            f'duri_p_entropy_10bin{{window="{w}"}} {h}',
            "# HELP duri_p_autocorr_lag1 lag-1 autocorrelation",
            "# TYPE duri_p_autocorr_lag1 gauge",
            f'duri_p_autocorr_lag1{{window="{w}"}} {rho}',
            "# HELP duri_p_runs_p runs test p-value",
            "# TYPE duri_p_runs_p gauge",
            f'duri_p_runs_p{{window="{w}"}} {runs_p}',
            ""
        ]
    atomic_write(OUT, "\n".join(lines))
    print(f"[OK] Entropy/Autocorr/Runs exported -> {OUT}")

if __name__ == "__main__":
    main()

