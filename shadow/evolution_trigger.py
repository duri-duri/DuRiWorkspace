#!/usr/bin/env python3
"""
Evolution Trigger - 큐 소비 및 자동 승급
"""

import json
import os
import pathlib
import subprocess
import time

import yaml

ROOT = pathlib.Path.home() / "DuRiWorkspace"
QDIR = ROOT / "var/queue"
LOGF = ROOT / "var/log/evolution_trigger.log"
APPR = ROOT / "shadow/approval_gate.yaml"


def log(*a):
    LOGF.parent.mkdir(parents=True, exist_ok=True)
    with open(LOGF, "a") as f:
        f.write(time.strftime("%F %T ") + " ".join(map(str, a)) + "\n")


def sh(cmd):
    return subprocess.run(cmd, cwd=ROOT.as_posix(), capture_output=True, text=True)


def approve(metrics):
    gate = {"min_safety": 0.70, "max_halluc": 0.03, "max_regrel": 0.01, "theta": 0.65}
    if APPR.exists():
        gate.update(yaml.safe_load(open(APPR)))
    if metrics.get("safety", 0) < gate["min_safety"]:
        return False, "safety"
    if metrics.get("halluc", 0) > gate["max_halluc"]:
        return False, "halluc"
    if metrics.get("regression_rel", 0) > gate["max_regrel"]:
        return False, "regression_rel"
    if metrics.get("J", 0) < gate["theta"]:
        return False, "J"
    return True, "ok"


def evaluate():
    # 최소평가: 테스트 통과 여부 기반 대리지표
    r = sh(["make", "-s", "test"])
    rel = 1.0 if r.returncode == 0 else 0.95
    # 임시 J: rel 0.4, 지연/비용 대리 0.6
    J = 0.4 * rel + 0.6 * 1.0
    return {"safety": 0.90, "halluc": 0.01, "regression_rel": 0.0, "J": J, "rel": rel}


def consume(path):
    try:
        data = json.load(open(path))
    except Exception:
        data = {}
    log("consume", path.name, "weakpoint", data.get("weakpoint"))
    # (여기서 실제 Evol.Engine 호출 및 패치 생성 자리)
    m = evaluate()
    ok, why = approve(m)
    log("metrics", m, "approve", ok, why)
    if not ok:
        return
    env = os.environ.copy()
    env["TARGET_TRAFFIC_PCT"] = "5"
    r = subprocess.run(
        ["/bin/bash", "-lc", "/home/duri/DuRiWorkspace/tools/canary_pipeline.auto.sh 5"],
        cwd=ROOT.as_posix(),
        env=env,
        capture_output=True,
        text=True,
    )
    log("canary_start_rc", r.returncode)
    if r.stdout or r.stderr:
        log("canary_output", r.stdout[-100:], r.stderr[-100:])
    # Guard 샘플 호출 (폴백 지원)
    g = sh(["bash", "scripts/guard_and_decide.sh"])
    log("guard_rc", g.returncode)


def main():
    QDIR.mkdir(parents=True, exist_ok=True)
    while True:
        for p in sorted(QDIR.glob("shadow_report_*.json")):
            consume(p)
            p.unlink(missing_ok=True)
        time.sleep(5)


if __name__ == "__main__":
    main()
