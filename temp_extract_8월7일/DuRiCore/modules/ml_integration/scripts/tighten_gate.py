#!/usr/bin/env python3
import sys, yaml

OVR="configs/evolve_override.yaml"
with open(OVR, "r") as f:
    cfg = yaml.safe_load(f)

cfg.setdefault("gate", {})
cfg["gate"]["max_mse_ratio"] = 1.40
cfg["gate"]["max_r2_gap"] = 0.06

with open(OVR, "w") as f:
    yaml.safe_dump(cfg, f, allow_unicode=True, sort_keys=False)

print("✅ Gate tightened: max_mse_ratio=1.40, max_r2_gap=0.06")
print(f"   file: {OVR}")

