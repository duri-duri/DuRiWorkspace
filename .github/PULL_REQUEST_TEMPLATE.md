# Phase 3 Release Preparation

## 📋 체크리스트

### 모니터링 지표 스냅샷
- [ ] Prometheus 10분 가용률: `sum by (job)(avg_over_time(up[10m]))`
- [ ] 스크랩 지연시간: `avg_over_time(scrape_duration_seconds[10m])`
- [ ] 베이스라인 스냅샷: `.reports/day61/` 디렉토리에 저장

### 롤백 조건
- [ ] `TargetDown` 알림 (기존)
- [ ] `HighScrapeLatency` > 0.1s (3분 지속)
- [ ] `CriticalScrapeLatency` > 0.5s (1분 지속)
- [ ] `PrometheusTSDBHigh` > 100,000 시리즈 (5분 지속)

### 시스템 검증
- [ ] 자가코딩 루프 드라이런 성공
- [ ] 학습 큐레이터 초기화 성공
- [ ] PoU 모니터링 시스템 정상
- [ ] Prometheus 6개 타겟 모두 up=1

### CI 체크 통과
- [ ] `guard` 체크 통과
- [ ] `guards` 체크 통과
- [ ] `tests` 체크 통과

## 🎯 목적
Phase 3 (Day 61-90) 진입을 위한 시스템 안정화 및 모니터링 강화

## 📊 베이스라인 지표
```bash
# 현재 상태 확인
curl -sG http://localhost:9090/api/v1/query \
  --data-urlencode 'query=sum by (job)(avg_over_time(up[10m]))' | \
  jq '.data.result[] | "\(.metric.job): \(.value[1])"'
```

## 🔄 롤백 절차
1. Prometheus 알림 확인
2. `scripts/pre_phase3_gate.sh` 재실행
3. 실패 항목 수정 후 재배포
4. 베이스라인 지표 복구 확인

## 📝 추가 정보
- **학습 큐레이터 ΔScore**: `최근 배치 p(성능)_now - p(성능)_prev` 정의
- **PoU 스모크 테스트**: `PoUPilotManager` 기반 리스트/상태 조회
- **자동 롤백**: 알림 규칙 기반 자동 감지
