#!/usr/bin/env bash
set -euo pipefail
export DURI_UNIFIED_REASONING_MIRROR=${DURI_UNIFIED_REASONING_MIRROR:-25}

TOTAL=${1:-500}
SLEEP=${2:-0.12}
OUT=var/reports/mirror/samples.jsonl
mkdir -p "$(dirname "$OUT")"

# 재개용: 이미 처리한 줄 수 확인
done_cnt=0
[[ -f "$OUT" ]] && done_cnt=$(wc -l < "$OUT" || echo 0)

python - <<'PY' "$TOTAL" "$SLEEP" "$done_cnt"
import json, subprocess, sys, time, random, pathlib
TOTAL = int(sys.argv[1]); SLEEP=float(sys.argv[2]); start_done=int(sys.argv[3])
samples = [{"query": q} for q in (
    ["1+1","2*3","root test","math 12*7","list 3 prime numbers",
     "explain cache warmup","factorial 10","gcd 84 30","fib 20",
     "sort 5 3 9 1","is prime 101"]*60
)]
ok = err = 0
for i in range(TOTAL):
    s = samples[(start_done + i) % len(samples)]
    r = subprocess.run(["python","scripts/mirror_feed.py"],
                       input=json.dumps(s).encode(),
                       capture_output=True, timeout=10)
    ok += (r.returncode==0); err += (r.returncode!=0)
    if (i+1) % 50 == 0:
        print(f"{start_done+i+1}/{start_done+TOTAL} fed (ok={ok}, err={err})", flush=True)
    time.sleep(SLEEP)
print(f"[done] fed={TOTAL}, ok={ok}, err={err}", flush=True)
PY
