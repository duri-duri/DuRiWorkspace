#!/usr/bin/env python3
import json
import pathlib
import re

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
MAP = yaml.safe_load((ROOT / "clinic" / "mapping.yaml").read_text(encoding="utf-8"))
DER = ROOT / "clinic" / "_derived"
out_triggers = []
for p in DER.glob("*.txt"):
    txt = p.read_text(encoding="utf-8", errors="ignore")
    # 예: 금기/주의 문장 → high_risk_triggers
    for line in txt.splitlines():
        if re.search(r"(금기|주의|악화|흉통|실신|어지러움)", line):
            out_triggers.append(
                {"regex": re.escape(line[:24]), "action": "stop_and_consult"}
            )
# 덮어쓰기 대신 덧대기(실전에서는 병합 로직 보강)
rules = ROOT / "auto_code_loop_beta/gates/risk_checks_rehab_protocol.yaml"
y = yaml.safe_load(rules.read_text(encoding="utf-8"))
y.setdefault("high_risk_triggers", [])
y["high_risk_triggers"] = (y["high_risk_triggers"] + out_triggers)[:100]
rules.write_text(
    yaml.safe_dump(y, allow_unicode=True, sort_keys=False), encoding="utf-8"
)
print(
    "[OK] mapped contraindications -> risk_checks_rehab_protocol.yaml (+",
    len(out_triggers),
    ")",
)
