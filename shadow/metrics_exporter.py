from time import sleep, time

from prometheus_client import Counter, Gauge, start_http_server

runs = Counter("duri_shadow_runs_total", "Total shadow jobs processed")
hb = Gauge("duri_shadow_heartbeat_seconds", "seconds since last heartbeat")
exporter_up = Gauge("duri_shadow_exporter_up", "1 if exporter loop healthy")


def heartbeat(ts):
    hb.set(max(0, time() - ts))


def main():
    print("[INFO] Shadow metrics exporter starting on :9109")
    start_http_server(9109)
    last = time()
    while True:
        try:
            # 여기에 실제 작업 주입/처리 연결하면 됨
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
