# DuRi Monitoring Runbook

## Quick Commands

### Top5 메모리 비율
```promql
topk(5, duri:container:mem_ratio)
```

### 제한 컨테이너 수/무제한 수
```promql
duri:containers:limitgt0
duri:containers:limit0
```

### Blackbox 타깃별 p95
```promql
duri:blackbox:p95
```

### 레코딩 드리프트 가드
```promql
absent(duri:container:mem_ratio) or (count(duri:container:mem_ratio) < duri:containers:limitgt0)
```

### 현재 firing 알람
```bash
curl -s localhost:9090/api/v1/alerts \
| jq -r '.data.alerts[] | "\(.labels.severity)\t\(.labels.alertname)\t\(.labels.name // .labels.instance // "-")"'
```

### 현재 비율 TOP5
```bash
promq 'topk(5, duri:container:mem_ratio)' \
| jq -r '.data.result[] | "\(.metric.name): \(.value[1])"'
```

## Grafana Dashboard

- **Import**: Grafana → Dashboards → Import → `grafana/duri-obsv-overview.json`
- **Data Source**: Prometheus
- **Refresh**: 10s
- **Variables**: container, target (multi-select)

## Alert Thresholds

- **Memory Ratio**: 90% (warning), 95% (critical)
- **Blackbox p95**: 1s (warning)
- **Recording Drift**: 5m (warning)

## Troubleshooting

1. **High Memory Ratio**: Check container memory usage and limits
2. **Blackbox p95 High**: Check network latency and target health
3. **Recording Drift**: Check Prometheus rule evaluation and relabel configs
