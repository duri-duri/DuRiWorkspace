#!/usr/bin/env python3
"""
Δ3: 전력(파워) 테이블 산출
효과크기(d) 대비 필요한 n 산출을 정적 테이블로 prom에 내보내 로그로도 남김.
"""
import os, json, math
from scipy import stats

root = os.getcwd()
tdir = os.environ.get("TEXTFILE_DIR", os.path.join(root, ".reports/synth"))
out_json = os.path.join(tdir, "ab_power.json")
out_prom = os.path.join(tdir, "ab_power.prom")

# 검출하고 싶은 Δp (effect size)
delta_ps = [0.02, 0.03, 0.05]
alpha = 0.05
power = 0.8  # 1 - beta
beta = 1 - power

# Two-sample proportion test sample size calculation
# H0: p_A = p_B, H1: p_A != p_B
# Effect size d = |p_A - p_B|
# n per group = (Z_alpha/2 + Z_beta)^2 * (p_A*(1-p_A) + p_B*(1-p_B)) / (p_A - p_B)^2
# For simplicity, assume p_A ≈ p_B ≈ 0.5 under H0

z_alpha_half = stats.norm.ppf(1 - alpha/2)
z_beta = stats.norm.ppf(power)

p0 = 0.5  # 귀무가설에서의 p

power_table = {}
for delta_p in delta_ps:
    p1 = p0 + delta_p  # Alternative hypothesis
    # Simplified formula for equal allocation
    p_pooled = (p0 + p1) / 2
    variance = p_pooled * (1 - p_pooled)
    n_per_group = (z_alpha_half + z_beta)**2 * 2 * variance / (delta_p**2)
    n_total = int(math.ceil(n_per_group * 2))  # Total sample size (both groups)
    power_table[f"delta_{delta_p:.2f}"] = {
        "delta_p": delta_p,
        "n_per_group": int(math.ceil(n_per_group)),
        "n_total": n_total,
        "alpha": alpha,
        "power": power
    }

os.makedirs(tdir, exist_ok=True)

# JSON 출력
with open(out_json, "w") as f:
    json.dump(power_table, f, indent=2)

# Prometheus 메트릭 출력 (최소 n_total을 gauge로)
min_n_total = min(v["n_total"] for v in power_table.values())

with open(out_prom, "w") as f:
    f.write("# HELP ab_power_n_total_min minimum total sample size for detectable effect\n")
    f.write("# TYPE ab_power_n_total_min gauge\n")
    f.write(f'ab_power_n_total_min{{delta_p="0.02"}} {power_table["delta_0.02"]["n_total"]}\n')
    f.write(f'ab_power_n_total_min{{delta_p="0.03"}} {power_table["delta_0.03"]["n_total"]}\n')
    f.write(f'ab_power_n_total_min{{delta_p="0.05"}} {power_table["delta_0.05"]["n_total"]}\n')
    f.write("# HELP ab_power_n_per_group_min minimum sample size per group\n")
    f.write("# TYPE ab_power_n_per_group_min gauge\n")
    f.write(f'ab_power_n_per_group_min{{delta_p="0.02"}} {power_table["delta_0.02"]["n_per_group"]}\n')
    f.write(f'ab_power_n_per_group_min{{delta_p="0.03"}} {power_table["delta_0.03"]["n_per_group"]}\n')
    f.write(f'ab_power_n_per_group_min{{delta_p="0.05"}} {power_table["delta_0.05"]["n_per_group"]}\n')

print(f"[OK] Power table exported: {out_json}, {out_prom}")
print(f"  Minimum n_total for Δp=0.02: {power_table['delta_0.02']['n_total']}")
print(f"  Minimum n_total for Δp=0.05: {power_table['delta_0.05']['n_total']}")

