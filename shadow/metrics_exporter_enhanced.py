#!/usr/bin/env python3
"""
Enhanced Shadow Metrics Exporter
- 기존 메트릭 유지
- canary_promotions, rollback_events 추가
"""

from time import sleep, time

from prometheus_client import Counter, Gauge, start_http_server

# 기존 메트릭
runs = Counter("duri_shadow_runs_total", "Total shadow jobs processed")
hb = Gauge("duri_shadow_heartbeat_seconds", "seconds since last heartbeat")
exporter_up = Gauge("duri_shadow_exporter_up", "1 if exporter loop healthy")

# 새 메트릭
canary_promotions = Counter("duri_shadow_canary_promotions_total", "Canary promotions", ["stage"])
rollback_events = Counter("duri_shadow_rollback_events_total", "Rollback events", ["reason"])


def heartbeat(ts):
    hb.set(max(0, time() - ts))


def main():
    print("[INFO] Enhanced Shadow metrics exporter starting on :9109")
    start_http_server(9109)
    last = time()
    while True:
        try:
            runs.inc(1)
            heartbeat(last)
            exporter_up.set(1)
        except Exception as e:
            print(f"[ERROR] tick failed: {e}")
            exporter_up.set(0)
        last = time()
        sleep(10)


if __name__ == "__main__":
    main()
