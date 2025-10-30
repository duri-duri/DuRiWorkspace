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
ab_p_value_gauge = Gauge("duri_ab_p_value", "Two-tailed p-value from AB eval")

# 새 메트릭
canary_promotions = Counter("duri_shadow_canary_promotions_total", "Canary promotions", ["stage"])
rollback_events = Counter("duri_shadow_rollback_events_total", "Rollback events", ["reason"])


def heartbeat(ts):
    hb.set(max(0, time() - ts))


def _read_ab_p_from_prom(path="var/metrics/ab_eval.prom"):
    """Read p-value from Prom textfile; tolerate labels/timestamps; pick first numeric <=1e3."""
    try:
        with open(path, "r") as f:
            for line in f:
                if not line or line.startswith("#"):
                    continue
                if line.startswith("duri_ab_p_value"):
                    # remove labels braces to split tokens uniformly
                    tokens = line.replace("{", " ").replace("}", " ").split()
                    for tk in tokens:
                        try:
                            v = float(tk)
                            if 0.0 <= v <= 1e3:
                                return v
                        except Exception:
                            continue
    except FileNotFoundError:
        return None
    except Exception:
        return None
    return None


def main():
    print("[INFO] Enhanced Shadow metrics exporter starting on :9109")
    start_http_server(9109)
    last = time()
    while True:
        try:
            runs.inc(1)
            heartbeat(last)
            exporter_up.set(1)
            p = _read_ab_p_from_prom()
            if p is not None:
                ab_p_value_gauge.set(p)
        except Exception as e:
            print(f"[ERROR] tick failed: {e}")
            exporter_up.set(0)
        last = time()
        sleep(10)


if __name__ == "__main__":
    main()
