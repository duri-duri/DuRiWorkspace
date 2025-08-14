#!/usr/bin/env bash
set -euo pipefail

echo "=== Day 9 Simulation: Alert Latency Measurement ==="

# 환경 변수 및 기본값 설정
ITER=${ITER:-20}
TIMEOUT=${TIMEOUT:-10}
LOG=${LOG:-var/logs/alerts.log}
OUT=${OUT:-var/metrics/day9_latency.csv}
SUMMARY_JSON=${SUMMARY_JSON:-var/metrics/day9_summary.json}

# 디렉토리 생성
mkdir -p "$(dirname "$OUT")" "$(dirname "$LOG")" "$(dirname "$SUMMARY_JSON")"

echo "iter,marker,latency_ms,status" > "$OUT"

# 알림 발생 함수 (기존 시스템과 연동)
emit_alert() {
    local marker="$1"
    local timestamp=$(date +%s)
    
    echo "[SIM] 알림 발생: $marker (timestamp: $timestamp)"
    
    # 기존 알림 시스템이 있으면 활용
    if [[ -x scripts/notify_slo_ok.sh ]]; then
        scripts/notify_slo_ok.sh "$marker" >/dev/null 2>&1 || true
    elif [[ -n "${WEBHOOK_URL:-}" ]]; then
        curl -fsS -H 'Content-Type: application/json' \
             -d "{\"text\":\"DAY9_ALERT ${marker}\",\"timestamp\":${timestamp}}" \
             "$WEBHOOK_URL" >/dev/null 2>&1 || true
    else
        # 모의 알림 (기존 로그 시스템 활용)
        python3 - "$marker" "$LOG" "$timestamp" <<'PY'
import sys
import time
import random
import pathlib
import datetime
import json

marker, log_path, timestamp = sys.argv[1], sys.argv[2], int(sys.argv[3])

# 50~500ms 지연 시뮬레이션 (실제 알림 시스템과 유사)
time.sleep(random.uniform(0.05, 0.50))

# 로그 파일에 알림 기록
p = pathlib.Path(log_path)
p.parent.mkdir(parents=True, exist_ok=True)

alert_entry = {
    "trigger_time": timestamp,
    "alert_time": int(time.time()),
    "marker": marker,
    "source": "day9_simulation",
    "timestamp": datetime.datetime.now().isoformat()
}

with p.open('a', encoding='utf-8') as f:
    f.write(json.dumps(alert_entry, ensure_ascii=False) + '\n')

print(f"모의 알림 기록 완료: {marker}")
PY
    fi
}

# 메인 시뮬레이션 루프
echo "[SIM] Day 9 알림 지연 시뮬레이션 시작 (${ITER}회 반복)"
for i in $(seq 1 "$ITER"); do
    marker="DAY9-${i}-$(date +%s)-$RANDOM"
    
    # 백그라운드에서 알림 발생
    emit_alert "$marker" &
    alert_pid=$!
    
    # 알림 지연 측정
    echo "[SIM] 반복 $i: 마커 '$marker' 대기 중..."
    ms=$(python3 tools/day9_measure.py --marker "$marker" --log "$LOG" --timeout "$TIMEOUT" || true)
    
    if [[ "$ms" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
        echo "${i},${marker},${ms},OK" >> "$OUT"
        printf "[OK] 반복=%s 마커=%s 지연=%.1f ms\n" "$i" "$marker" "$ms"
    else
        echo "${i},${marker},,TIMEOUT" >> "$OUT"
        echo "[TIMEOUT] 반복=$i 마커=$marker"
    fi
    
    # 백그라운드 알림 프로세스 완료 대기
    wait $alert_pid 2>/dev/null || true
    
    # 간격 조절 (시스템 부하 방지)
    sleep 0.1
done

# 결과 요약 생성
echo "[SIM] 결과 요약 생성 중..."
python3 - "$OUT" "$SUMMARY_JSON" <<'PY'
import sys
import json
import statistics
from pathlib import Path

def percentile(data, p):
    """백분위수 계산"""
    if not data:
        return None
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * p
    f = int(k)
    c = min(f + 1, len(sorted_data) - 1)
    w = k - f
    return sorted_data[f] * (1 - w) + sorted_data[c] * w

# CSV 파일 읽기
rows = []
csv_path = Path(sys.argv[1])
for line in csv_path.read_text(encoding='utf-8').splitlines()[1:]:
    if ',' in line:
        parts = line.split(',', 3)
        if len(parts) >= 4:
            it, mk, ms, st = parts
            rows.append((it, mk, float(ms) if ms else None, st))

# 지연 시간 데이터 추출
latencies = [r[2] for r in rows if r[2] is not None]
timeouts = sum(1 for r in rows if r[3] != 'OK')

# 요약 통계 계산
summary = {
    "count": len(rows),
    "ok": len(latencies),
    "timeouts": timeouts,
    "timeout_rate": (timeouts / len(rows)) if rows else None,
    "p50_ms": statistics.median(latencies) if latencies else None,
    "p95_ms": percentile(latencies, 0.95),
    "max_ms": max(latencies) if latencies else None,
    "min_ms": min(latencies) if latencies else None,
    "mean_ms": statistics.mean(latencies) if latencies else None,
    "simulation_time": Path(sys.argv[2]).parent.name if len(sys.argv) > 2 else "unknown"
}

# JSON 파일에 저장
summary_path = Path(sys.argv[2])
summary_path.parent.mkdir(parents=True, exist_ok=True)
with summary_path.open('w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print(json.dumps(summary, ensure_ascii=False))
PY

echo "[SIM] Day 9 시뮬레이션 완료"
echo "[SIM] 결과 요약: $SUMMARY_JSON"
echo "[SIM] 상세 로그: $OUT"

# Prometheus Export 실행
echo "[SIM] Prometheus Export 실행 중..."
python3 tools/day9_export_metrics.py

echo "=== Day 9 Simulation completed ==="
