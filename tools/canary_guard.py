#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Canary 가드: Prometheus에서 최근 구간의 p95/p99 시계열을 불러와
SLO 초과 비율의 Wilson Upper Bound로 유의하게 악화되었는지 판단합니다.

예)
  python3 tools/canary_guard.py \
    --prom-url http://localhost:9090 \
    --window 15m --step 15s \
    --p95-slo-ms 350 --p99-slo-ms 500 \
    --min-exceed-ratio 0.2 --confidence 0.95

종료코드:
  0 = 모두 통과
  2 = 하나 이상 실패(경보)
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def _z_from_conf(conf: float) -> float:
    # 양측 95% ≈ 1.96, 90% ≈ 1.64
    table = {0.90: 1.6449, 0.95: 1.96, 0.975: 2.24, 0.99: 2.5758}
    return table.get(conf, 1.96)


def wilson_upper(p_hat: float, n: int, z: float) -> float:
    if n == 0:
        return 0.0
    denom = 1 + z**2 / n
    center = p_hat + z * z / (2 * n)
    rad = z * math.sqrt((p_hat * (1 - p_hat) / n) + (z * z) / (4 * n * n))
    return (center + rad) / denom


def prom_query_range(base: str, query: str, start: float, end: float, step_s: int):
    params = {
        "query": query,
        "start": f"{start:.3f}",
        "end": f"{end:.3f}",
        "step": f"{step_s}",
    }
    url = f"{base.rstrip('/')}/api/v1/query_range?{urlencode(params)}"
    with urlopen(Request(url)) as r:
        payload = json.loads(r.read().decode("utf-8"))
    if payload.get("status") != "success":
        raise RuntimeError(f"Prometheus error: {payload}")
    return payload["data"]["result"]


def parse_step(step: str) -> int:
    step = step.strip().lower()
    if step.endswith("ms"):
        return max(1, int(round(float(step[:-2]) / 1000.0)))
    if step.endswith("s"):
        return int(float(step[:-1]))
    if step.endswith("m"):
        return int(float(step[:-1]) * 60)
    if step.endswith("h"):
        return int(float(step[:-1]) * 3600)
    return int(step)


def parse_window(w: str) -> int:
    return parse_step(w)


def series_to_floats(series):
    vals = []
    for ts, v in series:
        try:
            x = float(v)
            if math.isfinite(x):
                vals.append(x)
        except ValueError:
            pass
    return vals


def guard(args):
    now = time.time()
    start = now - parse_window(args.window)
    step_s = parse_step(args.step)
    z = _z_from_conf(args.confidence)

    q_p95 = "duri:latency_p95"
    q_p99 = "duri:latency_p99"

    p95 = prom_query_range(args.prom_url, q_p95, start, now, step_s)
    p99 = prom_query_range(args.prom_url, q_p99, start, now, step_s)

    slo95 = args.p95_slo_ms / 1000.0
    slo99 = args.p99_slo_ms / 1000.0
    min_ratio = args.min_exceed_ratio

    def analyze(vec, slo, name):
        failures = []
        report = []
        for item in vec:
            phase = item["metric"].get("phase", "unknown")
            vals = series_to_floats(item["values"])
            n = len(vals)
            if n == 0:
                report.append((name, phase, n, 0, 0.0, 0.0, "NO DATA"))
                continue
            exceed = sum(1 for x in vals if x > slo)
            p_hat = exceed / n
            ub = wilson_upper(p_hat, n, z)
            last = vals[-1]
            status = "OK"
            if last > slo or ub > min_ratio:
                status = "FAIL"
                failures.append(phase)
            report.append((name, phase, n, exceed, p_hat, ub, status))
        return report, failures

    rep95, fail95 = analyze(p95, slo95, "p95")
    rep99, fail99 = analyze(p99, slo99, "p99")

    # 출력
    def print_block(rep, slo_ms):
        print(
            f"\n=== Guard against SLO {rep[0][0]} <= {slo_ms:.0f} ms (window={args.window}, step={args.step}, conf={args.confidence}) ==="  # noqa: E501
        )
        print("metric  phase          n   exceed  p_hat   wilson_UB  status")
        for m, phase, n, ex, p, ub, st in rep:
            print(f"{m:<6} {phase:<12} {n:4d} {ex:7d}  {p:6.3f}   {ub:9.3f}  {st}")

    print_block(rep95, args.p95_slo_ms)
    print_block(rep99, args.p99_slo_ms)

    bad = set(fail95) | set(fail99)
    if bad:
        print(f"\n❌ Canary guard FAILED for phases: {', '.join(sorted(bad))}")
        return 2
    print("\n✅ Canary guard PASSED for all phases")
    return 0


def main():
    ap = argparse.ArgumentParser(description="DuRi Canary Guard")
    ap.add_argument("--prom-url", default="http://localhost:9090", help="Prometheus URL")
    ap.add_argument("--window", default="15m", help="분석 윈도우 (예: 10m, 1h)")
    ap.add_argument("--step", default="15s", help="샘플 간격 (예: 15s, 30s)")
    ap.add_argument("--p95-slo-ms", type=float, default=350.0, help="p95 SLO (ms)")
    ap.add_argument("--p99-slo-ms", type=float, default=500.0, help="p99 SLO (ms)")
    ap.add_argument(
        "--min-exceed-ratio",
        type=float,
        default=0.2,
        help="위반 비율의 윌슨 상한이 이 값 초과면 실패",
    )
    ap.add_argument(
        "--confidence",
        type=float,
        default=0.95,
        help="윌슨 상한 신뢰수준 (0.90/0.95/0.99)",
    )
    args = ap.parse_args()
    sys.exit(guard(args))


if __name__ == "__main__":
    main()
