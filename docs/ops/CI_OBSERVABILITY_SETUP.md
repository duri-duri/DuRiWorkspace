# CI 전용 관측 스택 설정

## compose.observation.ci.yml

CI 환경에서 사용하는 최소 관측 스택입니다.

```yaml
services:
  prometheus:
    image: prom/prometheus:v2.54.1
    container_name: prometheus-ci
    command:
      - --web.enable-admin-api
      - --config.file=/etc/prometheus/prometheus.yml
      - --storage.tsdb.path=/prometheus
    ports: ["9090:9090"]
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:9090/-/ready"]
      interval: 5s
      timeout: 3s
      retries: 20
    volumes:
      - ./prometheus:/etc/prometheus:ro
      - ./prometheus/rules:/etc/prometheus/rules:ro
      - ./prometheus-data-ci:/prometheus

  pushgateway:
    image: prom/pushgateway:v1.7.0
    container_name: pushgateway-ci
    ports: ["9091:9091"]
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:9091/metrics"]
      interval: 5s
      timeout: 3s
      retries: 20
```

## prometheus/prometheus.yml.ci

CI용 최소 Prometheus 설정입니다.

```yaml
global:
  scrape_interval: 5s
  evaluation_interval: 5s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['prometheus:9090']
  
  - job_name: 'pushgateway'
    honor_labels: true
    static_configs:
      - targets: ['pushgateway:9091']

rule_files:
  - /etc/prometheus/rules/heartbeat.rules.yml
```

## scripts/ci/obs_smoke.sh

CI 스모크 테스트 스크립트입니다.

```bash
#!/usr/bin/env bash
# CI Observability Smoke Test
# Purpose: Seed heartbeat metrics via Pushgateway and verify recording rules
# Usage: bash scripts/ci/obs_smoke.sh

set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

PROM_URL="${PROM_URL:-http://localhost:9090}"
PUSHGATEWAY_URL="${PUSHGATEWAY_URL:-http://localhost:9091}"

log() {
  echo "[CI] $*" >&2
}

log "Bring up stack"
docker compose -f compose.observation.ci.yml up -d --wait

log "Seed heartbeat x2 via pushgateway"
for i in 1 2; do
  TS=$(date +%s)
  SEQ=$i
  cat <<EOF | curl -sf --data-binary @- "${PUSHGATEWAY_URL}/metrics/job/duri_heartbeat/instance/local"
# TYPE duri_textfile_heartbeat_seq gauge
duri_textfile_heartbeat_seq{metric_realm="prod"} ${SEQ}
# TYPE duri_textfile_heartbeat_ts gauge
duri_textfile_heartbeat_ts{metric_realm="prod"} ${TS}
EOF
  sleep 2
done

log "Safe reload + wait eval"
curl -sf -X POST "${PROM_URL}/-/reload" >/dev/null || true
sleep 8

log "Verify heartbeat metrics"
ok=$(curl -sf --get "${PROM_URL}/api/v1/query" \
  --data-urlencode 'query=duri_heartbeat_ok{metric_realm="prod"}' | \
  jq -r '.data.result[]?.value[1] // "N/A"')

fresh=$(curl -sf --get "${PROM_URL}/api/v1/query" \
  --data-urlencode 'query=duri_heartbeat_fresh_120s{metric_realm="prod"}' | \
  jq -r '.data.result[]?.value[1] // "N/A"')

changes=$(curl -sf --get "${PROM_URL}/api/v1/query" \
  --data-urlencode 'query=duri_heartbeat_changes_6m{metric_realm="prod"}' | \
  jq -r '.data.result[]?.value[1] // "N/A"')

log "duri_heartbeat_ok=$ok, fresh_120s=$fresh, changes_6m=$changes"

# Validation
if [ "$ok" != "1" ]; then
  log "FAIL: heartbeat_ok not 1 (got: $ok)"
  exit 1
fi

if [ "$fresh" = "N/A" ] || (( $(echo "$fresh" | awk '{if ($1 > 120) exit 1; exit 0}') )); then
  log "FAIL: freshness bad (got: $fresh)"
  exit 1
fi

log "OK: All heartbeat metrics verified"
exit 0
```

