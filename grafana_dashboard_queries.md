# Grafana 대시보드 쿼리 (라벨 메트릭)

## DORA 메트릭 대시보드

### 1. 시간당 배포 추이
```
sum by (env,service)(increase(duri_deployment_events_labeled_total[1h]))
```

### 2. 오늘 배포 카운트
```
sum by (env,service)(increase(duri_deployment_events_labeled_total[24h]))
```

### 3. 영속 합계 뷰
```
duri_deployment_events_persisted
```

### 4. 배포 빈도 (24시간)
```
duri_deploys_24h
```

### 5. 리드타임 (초)
```
duri_lead_time_seconds
```

### 6. 변경실패율
```
duri_change_failure_rate
```

### 7. 평균 복구 시간 (MTTR)
```
duri_mttr_seconds
```

## 패널 설정 예시

### 배포 추이 패널
- **Title**: "Deployment Trend by Environment/Service"
- **Query**: `sum by (env,service)(increase(duri_deployment_events_labeled_total[1h]))`
- **Visualization**: Time series
- **Unit**: Short
- **Legend**: `{{env}}/{{service}}`

### 배포 카운트 패널
- **Title**: "Today's Deployment Count"
- **Query**: `sum by (env,service)(increase(duri_deployment_events_labeled_total[24h]))`
- **Visualization**: Stat
- **Unit**: Short
- **Legend**: `{{env}}/{{service}}`

### 영속 합계 패널
- **Title**: "Persistent Deployment Events"
- **Query**: `duri_deployment_events_persisted`
- **Visualization**: Stat
- **Unit**: Short

### 배포 빈도 패널
- **Title**: "Deployment Frequency (24h)"
- **Query**: `duri_deploys_24h`
- **Visualization**: Stat
- **Unit**: Short

### 리드타임 패널
- **Title**: "Lead Time for Changes"
- **Query**: `duri_lead_time_seconds`
- **Visualization**: Stat
- **Unit**: Seconds

### 변경실패율 패널
- **Title**: "Change Failure Rate"
- **Query**: `duri_change_failure_rate`
- **Visualization**: Stat
- **Unit**: Percent (0-1)

### MTTR 패널
- **Title**: "Mean Time to Recovery"
- **Query**: `duri_mttr_seconds`
- **Visualization**: Stat
- **Unit**: Seconds
