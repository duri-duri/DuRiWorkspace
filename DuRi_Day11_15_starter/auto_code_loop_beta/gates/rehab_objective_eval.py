#!/usr/bin/env python3
import argparse
import json
import pathlib

import yaml

ap = argparse.ArgumentParser()
ap.add_argument("--objective", required=True)
ap.add_argument("--rules", required=True)
ap.add_argument("--infile", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()
obj = yaml.safe_load(open(a.objective, "r", encoding="utf-8"))
rl = yaml.safe_load(open(a.rules, "r", encoding="utf-8"))
w = obj["weights"]
th = obj["thresholds"]


def eff(effect, minutes):
    return effect / max(minutes, 10)


def safety(risk):
    return 1.0 - risk


rows = []
for line in open(a.infile, "r", encoding="utf-8"):
    if not line.strip():
        continue
    x = json.loads(line)
    _eff = eff(x["effect_score"], x["time_minutes"])
    _saf = safety(x["risk_score"])
    _sus = x["sustainability_score"]
    _adh = x["adherence_ratio"]
    J = (
        w["efficiency"] * _eff
        + w["sustainability"] * _sus
        + w["safety"] * _saf
        + w["adherence"] * _adh
    )
    v = {}
    if _saf < th["min_safety"]:
        v["safety"] = f"{_saf:.2f}<{th['min_safety']}"
    if _sus < th["min_sustainability"]:
        v["sustainability"] = f"{_sus:.2f}<{th['min_sustainability']}"
    if _eff < th["min_efficiency"]:
        v["efficiency"] = f"{_eff:.3f}<{th['min_efficiency']}"
    if _adh < th["min_adherence"]:
        v["adherence"] = f"{_adh:.2f}<{th['min_adherence']}"
    rows.append(
        {
            "input": x["input"],
            "efficiency": round(_eff, 4),
            "safety": round(_saf, 4),
            "sustainability": round(_sus, 4),
            "adherence": round(_adh, 4),
            "J": round(J, 4),
            "violations": v,
        }
    )
report = {
    "items": rows,
    "summary": {
        "mean_J": round(sum(r["J"] for r in rows) / len(rows), 4),
        "violations_total": sum(len(r["violations"]) for r in rows),
    },
}
pathlib.Path(a.out).write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(f"[OK] rehab objective report -> {a.out}")
