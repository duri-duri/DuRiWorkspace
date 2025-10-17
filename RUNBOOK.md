# DuRi 운영 런북

## 증상: 헬스 5xx / 스크레이프 실패

### 1단계: 로그 확인
```bash
make logs
```

### 2단계: 스모크 테스트 재확인
```bash
make smoke
```

### 3단계: 의존 서비스 상태 확인
```bash
docker compose ps
```

### 4단계: 컨테이너 재시작
```bash
make restart
```

### 5단계: 실패 시 이전 태그로 롤백
```bash
git checkout v1.0.0-lock && docker compose up -d --build
```

## 안정 태그로 즉시 롤백
```bash
git checkout v1.0.1-opslock && docker compose up -d --build
make smoke
```

## 빠른 명령어
- `make up` - 서비스 기동
- `make down` - 서비스 중지
- `make restart` - 서비스 재시작
- `make smoke` - 스모크 테스트
- `make logs` - 로그 확인

## 알람 원인 판별 → 롤백/재시도 → RAG 미적중 점검 → 비용 급증 대응

### AgentTaskSuccessLow / AgentHallucinationHigh
1. **즉시 조치**: `make logs` → 최근 에러 로그 확인
2. **RAG 점검**: 벡터 검색 품질, 인용 누락 패턴 분석
3. **롤백**: `make rollback` 또는 `git checkout v1.2-agentops-opslock && docker compose up -d --build`
4. **비용 급증**: `increase(cost_usd_total[5m])` 모니터링, 쿼터/모델 교체 고려

### AgentLatencyP95High
1. **부하 확인**: `docker stats` → CPU/메모리 사용률
2. **의존성 점검**: PostgreSQL/Redis 응답시간
3. **스케일링**: `docker compose up -d --scale duri_control=2` (임시)

### AgentErrorBudgetBurnFast/Slow
1. **에러 패턴 분석**: `jq '.signals.hallucination_rate' reports/duri_eval_v3_1.json`
2. **모델 교체**: 더 보수적인 모델로 임시 전환
3. **트래픽 제한**: Rate limiting 활성화
