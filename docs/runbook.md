# DuRi Runbook

## Prometheus Rules Testing

### Label Matching Requirements
promtool 테스트는 라벨까지 정확히 일치해야 합니다. 테스트 작성 시 주의사항:

- 기대값에 `__name__` 라벨 포함 필요
- 모든 메트릭 라벨(`k`, `scope`, `domain` 등) 정확히 매칭
- 값 정밀도도 정확히 일치해야 함

### Example
```yaml
exp_samples:
  - labels: '{__name__="duri_mrr_ma7", domain="ALL", k="3", scope="all"}'
    value: 0.8742857142857143
```

## Alert Management

### Alertmanager Configuration
- Slack webhook은 `${SLACK_WEBHOOK_URL}` 환경변수 사용
- 팀별 라우팅은 `labels` 기반으로 설정

### Grafana Dashboard Provisioning
- 대시보드 JSON: `/var/lib/grafana/dashboards`
- 프로비저닝 YAML: `/etc/grafana/provisioning/dashboards/*.yml`
