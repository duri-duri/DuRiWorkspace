# Grafana 빠른 패널 쿼리

## DORA 메트릭 대시보드 쿼리

### 1. 최근 24시간 배포 수
```
duri_deploys_24h
```

### 2. 배포 이벤트 추이 (1시간 단위)
```
increase(duri_deployment_events_total[1h])
```

### 3. 리드타임 (초)
```
duri_lead_time_seconds
```

### 4. 변경실패율
```
duri_change_failure_rate
```

### 5. 평균 복구 시간 (MTTR)
```
duri_mttr_seconds
```

### 6. 영속 배포 이벤트 (Redis 기반)
```
duri_deployment_events_persisted
```

## 패널 설정 예시

### 배포 빈도 패널
- **Title**: "Deployment Frequency (24h)"
- **Query**: `duri_deploys_24h`
- **Visualization**: Stat
- **Unit**: Short

### 배포 이벤트 추이 패널
- **Title**: "Deployment Events Trend"
- **Query**: `increase(duri_deployment_events_total[1h])`
- **Visualization**: Time series
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
