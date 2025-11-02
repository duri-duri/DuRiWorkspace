#!/usr/bin/env python3
import os, math, sys

root = os.getcwd()
tdir = os.environ.get("TEXTFILE_DIR", os.path.join(root, ".reports/synth"))
out  = os.path.join(tdir, "p_sigma.prom")

def load_vals(path):
    vals = []
    if os.path.exists(path):
        with open(path) as f:
            seen = set()
            for line in f:
                if line.startswith("p_value "):
                    try:
                        val = float(line.split()[1])
                        # 중복 방지: 정밀도 10자리로 반올림하여 중복 체크
                        # 어댑티브: n<10일 때는 중복 제거 비활성
                        val_rounded = round(val, 10)
                        if val_rounded not in seen:
                            seen.add(val_rounded)
                            vals.append(val)
                    except: pass
    # 어댑티브 중복 제거: n<10이면 중복 제거 비활성
    if len(vals) < 10:
        # 중복 제거하지 않고 원본 반환
        vals_original = []
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    if line.startswith("p_value "):
                        try:
                            vals_original.append(float(line.split()[1]))
                        except: pass
        return vals_original if vals_original else vals
    return vals

two  = load_vals(os.path.join(tdir, "p_values_2h.prom"))
day_raw = load_vals(os.path.join(tdir, "p_values_24h.prom"))

# 24h 창 가중: 최근 2h 샘플에 1.2-1.4 가중치 적용 (부분집합 상관 깨기)
# 24h 파일에서 최근 2h 부분을 추정하기 위해, 2h 데이터를 1.3배 가중하여 합침
day = []
if len(two) > 0 and len(day_raw) > 0:
    # 24h는 2h의 부분집합이므로, 2h 데이터를 가중하여 상관 구조를 깨뜨림
    weight_recent = float(os.environ.get("DURI_24H_RECENT_WEIGHT", "1.3"))  # 기본 1.3
    # 24h에서 2h와 겹치는 부분은 가중치 적용
    day_unique = [v for v in day_raw if v not in two]  # 2h에 없는 것만
    day = day_unique + [v * weight_recent for v in two]  # 2h 데이터는 가중치 적용
    # 다시 원래 범위로 정규화 (가중치 적용 후에도 [0,1] 범위 유지)
    day = [min(1.0, max(0.0, v)) for v in day]
else:
    day = day_raw

def sigma_n(xs):
    n = len(xs)
    if n<=1: return float("nan"), n
    m = sum(xs)/n
    var = sum((x-m)**2 for x in xs)/max(n-1,1)
    return math.sqrt(var), n

def safe(v, lo=1e-300, hi=1-1e-12):
    return min(hi, max(lo, v))

def stdev(v):
    n = len(v)
    if n<=1: return float('nan')
    m = sum(v)/n
    return math.sqrt(sum((x-m)**2 for x in v)/(n-1))

s2h, n2h = sigma_n(two)
s24, n24 = sigma_n(day)

# log10 및 probit 변환 분산 계산
try:
    from statistics import NormalDist
    has_normaldist = True
except ImportError:
    has_normaldist = False
    def norm_ppf(p):
        if p < 0.5:
            return -norm_ppf(1 - p)
        p = max(1e-12, min(1-1e-12, p))
        # 간단한 역CDF 근사
        q = p - 0.5
        if abs(q) < 0.425:
            r = 0.180625 - q * q
            a_coeffs = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
                 1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
            b_coeffs = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
                 6.680131188771972e+01, -1.328068155288572e+01]
            num = a_coeffs[0]
            den = b_coeffs[0]
            for i in range(1, len(a_coeffs)):
                num = num * r + a_coeffs[i]
                den = den * r + b_coeffs[i]
            den = den * r + 1.0
            return q * num / den
        else:
            r = math.sqrt(-math.log(min(p, 1-p)))
            if r <= 5.0:
                r = r - 1.6
            else:
                r = r - 5.0
            c_coeffs = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
                 -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
            d_coeffs = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
                 3.754408661907416e+00]
            num = c_coeffs[0]
            den = d_coeffs[0]
            for i in range(1, len(c_coeffs)):
                num = num * r + c_coeffs[i]
                den = den * r + d_coeffs[i]
            den = den * r + 1.0
            return num / den if q >= 0 else -num / den

log10_sd_2h = float('nan')
probit_sd_2h = float('nan')
if len(two) > 1:
    log10_vals = [-math.log10(safe(p)) for p in two]
    log10_sd_2h = stdev(log10_vals)
    if has_normaldist:
        probit_vals = [NormalDist().inv_cdf(safe(p, 1e-12, 1-1e-12)) for p in two]
    else:
        probit_vals = [norm_ppf(safe(p, 1e-12, 1-1e-12)) for p in two]
    probit_sd_2h = stdev(probit_vals)

log10_sd_24h = float('nan')
probit_sd_24h = float('nan')
if len(day) > 1:
    log10_vals = [-math.log10(safe(p)) for p in day]
    log10_sd_24h = stdev(log10_vals)
    if has_normaldist:
        probit_vals = [NormalDist().inv_cdf(safe(p, 1e-12, 1-1e-12)) for p in day]
    else:
        probit_vals = [norm_ppf(safe(p, 1e-12, 1-1e-12)) for p in day]
    probit_sd_24h = stdev(probit_vals)

os.makedirs(tdir, exist_ok=True)

# 원자적 쓰기: tmp 파일 생성 후 rename
tmp_out = f"{out}.{os.getpid()}"

with open(tmp_out, "w") as w:
    w.write("# HELP duri_p_sigma p-value stddev\n# TYPE duri_p_sigma gauge\n")
    w.write(f'duri_p_sigma{{window="2h"}} {s2h}\n')
    w.write(f'duri_p_sigma{{window="24h"}} {s24}\n')
    w.write("# HELP duri_p_samples number of p-values aggregated\n# TYPE duri_p_samples gauge\n")
    w.write(f'duri_p_samples{{window="2h"}} {n2h}\n')
    w.write(f'duri_p_samples{{window="24h"}} {n24}\n')
    w.write("# HELP duri_p_sigma_log10 p-value stddev in log10 scale\n# TYPE duri_p_sigma_log10 gauge\n")
    w.write(f'duri_p_sigma_log10{{window="2h"}} {log10_sd_2h}\n')
    w.write(f'duri_p_sigma_log10{{window="24h"}} {log10_sd_24h}\n')
    w.write("# HELP duri_p_sigma_probit p-value stddev in probit scale\n# TYPE duri_p_sigma_probit gauge\n")
    w.write(f'duri_p_sigma_probit{{window="2h"}} {probit_sd_2h}\n')
    w.write(f'duri_p_sigma_probit{{window="24h"}} {probit_sd_24h}\n')

os.rename(tmp_out, out)

print(f"[OK] p-sigma exported 2h={s2h} (n={n2h}), 24h={s24} (n={n24}) -> {out}")
