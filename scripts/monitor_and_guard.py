#!/usr/bin/env python3
import json
import re
import subprocess as sp
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOGCSV = ROOT / "var/reports/rollout_watch.csv"
BASEF = ROOT / "var/reports/baseline.json"
INTERVAL = 600  # 10분
ITER = 24  # 총 4시간 (원하면 늘리세요)


def sh(cmd):
    r = sp.run(["bash", "-lc", cmd], text=True, capture_output=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def parse_number(txt):
    m = re.search(r"([0-9]+(?:\.[0-9]+)?)", txt.replace(",", ""))
    return float(m.group(1)) if m else None


def bench_once():
    vals = {}
    for k, cmd in {
        "advanced": "scripts/rollout_ops.sh bench_advanced",
        "general": "scripts/rollout_ops.sh bench_general",
        "math": "scripts/rollout_ops.sh bench_math",
    }.items():
        rc, out, err = sh(cmd)
        if rc == 0 and out:
            v = parse_number(out)
            if v is not None:
                vals[k] = v
    return vals


def grep_errors():
    # 운영 로그 error/fail/traceback 스캔(없어도 OK)
    rc, out, err = sh(r"ls -1 var/reports/final_verify_*/run.log 2>/dev/null | tail -n 2")
    files = [l for l in out.splitlines() if l.strip()]  # noqa: E741
    bad = []
    for f in files:
        rc2, out2, _ = sh(rf"grep -Ein 'error|fail|traceback' {f} || true")
        if out2.strip():
            bad.append((f, out2[:500]))
    return bad


def read_baseline():
    if BASEF.exists():
        try:
            return json.loads(BASEF.read_text())
        except:  # noqa: E722
            return {}
    return {}


def now_status():
    rc, out, err = sh("scripts/rollout_ops.sh status")
    return out


def append_csv(row):
    head = not LOGCSV.exists()
    with LOGCSV.open("a", encoding="utf-8") as f:
        if head:
            f.write("ts,rollout,adv,gen,math,err_count,alerts\n")
        f.write(
            ",".join(str(row.get(k, "")) for k in ["ts", "rollout", "adv", "gen", "math", "err_count", "alerts"]) + "\n"
        )


def extract_rollout(status_txt):
    m = re.search(r"ROLLOUT:\s*([0-9]+)%", status_txt)
    return int(m.group(1)) if m else None


def main():
    base = read_baseline()
    base_m = base.get("metrics") or {}
    print("[monitor] start; baseline:", base_m)
    for i in range(ITER):
        ts = int(time.time())
        status = now_status()
        rollout = extract_rollout(status) or ""
        errs = grep_errors()
        bvals = bench_once()
        alerts = []

        # 비교/가드
        for name, val in bvals.items():
            b = base_m.get(name)
            if b is None:
                continue
            delta = (val - b) / b * 100.0
            # 목표 / 하드 가드
            if abs(delta) > 5:
                alerts.append(f"{name} {delta:+.2f}% vs baseline")
            if abs(delta) > 10:
                alerts.append(f"HARD-{name} {delta:+.2f}%")

        if errs:
            alerts.append(f"errors:{len(errs)}")

        # 로그 남기기
        append_csv(
            {
                "ts": ts,
                "rollout": rollout,
                "adv": bvals.get("advanced", ""),
                "gen": bvals.get("general", ""),
                "math": bvals.get("math", ""),
                "err_count": len(errs),
                "alerts": "|".join(alerts) if alerts else "",
            }
        )

        # 콘솔 피드백
        print(
            f"[{i+1}/{ITER}] ts={ts} rollout={rollout} adv={bvals.get('advanced')} gen={bvals.get('general')} math={bvals.get('math')} err={len(errs)}"  # noqa: E501
        )
        if alerts:
            print("  ALERT:", "; ".join(alerts))
            # 하드가드 트리거 시 즉시 권고 출력
            if any(a.startswith("HARD-") for a in alerts) or len(errs) > 0:
                print("  >>> 권고: 즉시 완화(roll back) ↓")
                print("      export DURI_UNIFIED_REASONING_ROLLOUT=50 && bash scripts/rollout_ops.sh status")
        if i < ITER - 1:
            time.sleep(INTERVAL)

    print("[monitor] done. csv -> var/reports/rollout_watch.csv")


if __name__ == "__main__":
    main()
