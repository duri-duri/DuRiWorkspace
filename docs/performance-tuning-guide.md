# DuRi Performance Tuning Guide - Phase 4
# 성능 최적화 및 튜닝 가이드

## 🎯 **성능 목표**
- **응답 시간**: 95%ile < 500ms
- **처리량**: RPS > 100
- **가용성**: 99.9% (Core/Control), 99.5% (Brain), 99.0% (Evolution)
- **리소스 사용률**: CPU < 80%, Memory < 85%

## 📊 **성능 모니터링 지표**

### 1. 애플리케이션 레벨
```yaml
# HTTP 응답 시간
http_request_duration_seconds:
  buckets: [0.1, 0.25, 0.5, 1, 2.5, 5, 10]

# HTTP 요청 수
http_requests_total:
  labels: [method, endpoint, status]

# 에러율
http_error_rate:
  calculation: "5xx_requests / total_requests"
```

### 2. 인프라스트럭처 레벨
```yaml
# 컨테이너 리소스
container_cpu_usage_seconds_total
container_memory_usage_bytes
container_network_receive_bytes_total
container_network_transmit_bytes_total

# 시스템 리소스
node_cpu_seconds_total
node_memory_MemAvailable_bytes
node_filesystem_avail_bytes
```

### 3. 데이터베이스 레벨
```yaml
# PostgreSQL
pg_stat_activity_count
pg_stat_database_tup_returned
pg_stat_database_tup_fetched

# Redis
redis_memory_used_bytes
redis_connected_clients
redis_keyspace_hits
redis_keyspace_misses
```

## ⚡ **성능 최적화 전략**

### 1. 애플리케이션 최적화
```python
# 비동기 처리
import asyncio
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# 연결 풀 최적화
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)

# 캐싱 전략
import redis
from functools import lru_cache

redis_client = redis.Redis(host='duri-redis', port=6379, db=0)

@lru_cache(maxsize=1000)
def expensive_calculation(param):
    # 캐시된 계산
    pass
```

### 2. 데이터베이스 최적화
```sql
-- 인덱스 최적화
CREATE INDEX CONCURRENTLY idx_user_created_at ON users(created_at);
CREATE INDEX CONCURRENTLY idx_session_user_id ON sessions(user_id);

-- 쿼리 최적화
EXPLAIN ANALYZE SELECT * FROM users WHERE created_at > NOW() - INTERVAL '1 day';

-- 연결 풀 설정
-- postgresql.conf
max_connections = 200
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
```

### 3. Redis 최적화
```redis
# 메모리 최적화
CONFIG SET maxmemory 512mb
CONFIG SET maxmemory-policy allkeys-lru

# 지속성 최적화
CONFIG SET save "900 1 300 10 60 10000"
CONFIG SET appendonly yes
CONFIG SET appendfsync everysec

# 연결 최적화
CONFIG SET tcp-keepalive 60
CONFIG SET timeout 300
```

### 4. Docker 최적화
```yaml
# docker-compose.yml
services:
  duri_core:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    environment:
      - PYTHONOPTIMIZE=1
      - PYTHONDONTWRITEBYTECODE=1
```

## 🔧 **성능 튜닝 도구**

### 1. 프로파일링 도구
```python
# cProfile 사용
import cProfile
import pstats

def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()
    # 실행할 코드
    profiler.disable()
    
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)

# 메모리 프로파일링
from memory_profiler import profile

@profile
def memory_intensive_function():
    # 메모리 집약적 코드
    pass
```

### 2. 모니터링 스크립트
```bash
#!/bin/bash
# performance-monitor.sh

# CPU 사용률 모니터링
cpu_usage=$(docker stats --no-stream --format "{{.CPUPerc}}" duri_core_container | sed 's/%//')
if (( $(echo "$cpu_usage > 80" | bc -l) )); then
    echo "WARNING: High CPU usage: ${cpu_usage}%"
fi

# 메모리 사용률 모니터링
memory_usage=$(docker stats --no-stream --format "{{.MemUsage}}" duri_core_container)
echo "Memory usage: $memory_usage"

# 응답 시간 모니터링
response_time=$(curl -w "%{time_total}" -s -o /dev/null http://localhost:8080/health)
echo "Response time: ${response_time}s"
```

### 3. 부하 테스트
```python
# locust를 사용한 부하 테스트
from locust import HttpUser, task, between

class DuRiUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def health_check(self):
        self.client.get("/health")
    
    @task(1)
    def api_call(self):
        self.client.get("/api/v1/status")
```

## 📈 **성능 벤치마크**

### 1. 기준선 설정
```yaml
baseline_metrics:
  response_time_95p: 200ms
  response_time_99p: 500ms
  throughput: 100 RPS
  error_rate: 0.1%
  cpu_usage: 50%
  memory_usage: 60%
```

### 2. 성능 테스트 시나리오
```yaml
test_scenarios:
  - name: "Normal Load"
    users: 50
    duration: "10m"
    expected_response_time: "< 200ms"
  
  - name: "Peak Load"
    users: 200
    duration: "5m"
    expected_response_time: "< 500ms"
  
  - name: "Stress Test"
    users: 500
    duration: "2m"
    expected_response_time: "< 1000ms"
```

### 3. 성능 회귀 감지
```yaml
regression_detection:
  threshold: 20%  # 20% 이상 성능 저하 시 알람
  comparison_period: "1d"
  metrics:
    - response_time_95p
    - throughput
    - error_rate
```

## 🚨 **성능 알람 임계값**

### 1. 응답 시간 알람
```yaml
response_time_alerts:
  warning:
    threshold: 500ms
    duration: "5m"
  critical:
    threshold: 1000ms
    duration: "2m"
```

### 2. 처리량 알람
```yaml
throughput_alerts:
  warning:
    threshold: 50 RPS
    duration: "10m"
  critical:
    threshold: 10 RPS
    duration: "5m"
```

### 3. 리소스 사용률 알람
```yaml
resource_alerts:
  cpu_warning: 80%
  cpu_critical: 95%
  memory_warning: 85%
  memory_critical: 95%
```

## 📋 **성능 최적화 체크리스트**

### 애플리케이션 레벨
- [ ] 비동기 처리 구현
- [ ] 연결 풀 최적화
- [ ] 캐싱 전략 적용
- [ ] 데이터베이스 쿼리 최적화
- [ ] 메모리 사용량 최적화

### 인프라스트럭처 레벨
- [ ] Docker 리소스 제한 설정
- [ ] 네트워크 최적화
- [ ] 스토리지 최적화
- [ ] 로드 밸런싱 설정
- [ ] 오토스케일링 구성

### 모니터링 레벨
- [ ] 성능 메트릭 수집
- [ ] 알람 규칙 설정
- [ ] 대시보드 구성
- [ ] 로그 분석 설정
- [ ] 성능 테스트 자동화

## 🔄 **지속적 성능 개선**

### 1. 정기 성능 검토
```yaml
performance_review:
  frequency: "weekly"
  metrics:
    - response_time_trend
    - throughput_trend
    - error_rate_trend
    - resource_usage_trend
```

### 2. 성능 회귀 방지
```yaml
regression_prevention:
  - 코드 리뷰 시 성능 영향 검토
  - 배포 전 성능 테스트 실행
  - 성능 메트릭 모니터링
  - 자동 롤백 설정
```

### 3. 성능 개선 로드맵
```yaml
improvement_roadmap:
  - phase1: "기본 성능 최적화"
  - phase2: "고급 캐싱 전략"
  - phase3: "마이크로서비스 아키텍처"
  - phase4: "AI 기반 성능 최적화"
```
