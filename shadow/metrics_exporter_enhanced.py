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

# Transport 메트릭 (하이브리드 시스템)
transport_total = Counter("duri_shadow_transport_total", "Transport calls", ["mode", "service", "status"])
ssh_failures = Counter("duri_shadow_ssh_failures_total", "SSH failures", ["service"])
ssh_latency = Gauge("duri_shadow_ssh_latency_ms", "SSH latency (ms)", ["service"])

# EV 공백 감지 메트릭 (하드닝 #1)
last_ev_unixtime = Gauge("duri_last_ev_unixtime", "Unix timestamp of latest EV bundle creation")


def heartbeat(ts):
    hb.set(max(0, time() - ts))


def _read_transport_metrics(path="var/metrics/transport_metrics.prom"):
    """
    transport_metrics.prom 파일에서 메트릭 읽기
    기존 _read_ab_p_from_prom 패턴 활용
    """
    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # Prometheus 형식: metric_name{labels} value timestamp
                # 예: duri_shadow_transport_total{mode="ssh",service="core",status="success"} 1 1234567890
                if "duri_shadow_transport_total" in line:
                    # 간단 파싱 (정규식으로 라벨 추출)
                    import re
                    match = re.search(r'mode="([^"]+)"', line)
                    mode = match.group(1) if match else "unknown"
                    match = re.search(r'service="([^"]+)"', line)
                    service = match.group(1) if match else "unknown"
                    match = re.search(r'status="([^"]+)"', line)
                    status = match.group(1) if match else "unknown"
                    
                    # 카운터 증가 (중복 계산 방지를 위해 마지막 timestamp만 기록하도록 설계 필요하나,
                    # 여기서는 단순히 카운터만 업데이트)
                    transport_total.labels(mode=mode, service=service, status=status).inc(0)  # 관측만
                    
                    if status == "failure" and mode == "ssh":
                        ssh_failures.labels(service=service).inc(0)  # 관측만
    except FileNotFoundError:
        pass  # 파일 없으면 무시 (정상)
    except Exception as e:
        print(f"[WARN] transport metrics read error: {e}")


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


def _read_last_ev_unixtime():
    """최신 EV 번들의 생성 시간(Unix timestamp) 읽기 (하드닝 #1)"""
    import os
    import glob
    
    try:
        # LATEST 심볼릭 링크 우선 확인
        latest_link = "var/evolution/LATEST"
        if os.path.islink(latest_link):
            ev_dir = os.readlink(latest_link)
            if not os.path.isabs(ev_dir):
                ev_dir = os.path.join(os.path.dirname(latest_link), ev_dir)
            ev_path = os.path.abspath(ev_dir)
        else:
            # LATEST가 없으면 최신 EV 번들 찾기 (mtime 기준)
            ev_dirs = glob.glob("var/evolution/EV-*")
            if not ev_dirs:
                return None
            ev_path = max(ev_dirs, key=os.path.getmtime)
        
        if os.path.isdir(ev_path):
            # 디렉토리 mtime을 Unix timestamp로 반환
            mtime = os.path.getmtime(ev_path)
            return int(mtime)
    except Exception:
        pass
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
            # 기존 메트릭 읽기 (AB p-value)
            p = _read_ab_p_from_prom()
            if p is not None:
                # p-value NaN/Inf 체크 (하드닝 #3: 병적값 감시)
                import math
                if not (math.isfinite(p) and 0.0 <= p <= 1.0):
                    print(f"[WARN] Invalid p-value detected: {p} (NaN/Inf or out of range)")
                else:
                    ab_p_value_gauge.set(p)
            # Transport 메트릭 읽기 (하이브리드 시스템)
            _read_transport_metrics()
            # EV 공백 감지 메트릭 업데이트 (하드닝 #1)
            ev_timestamp = _read_last_ev_unixtime()
            if ev_timestamp is not None:
                last_ev_unixtime.set(ev_timestamp)
        except Exception as e:
            print(f"[ERROR] tick failed: {e}")
            exporter_up.set(0)
        last = time()
        sleep(10)


if __name__ == "__main__":
    main()
