# 소음(Noise) 튜닝 가이드

## 🎯 목표
오경보(월) 기대치 ≤ 1.2회 → **0.8회 예상** 달성

## 📊 현재 임계값
- `QualityZScoreAnomaly`: `z <= -2`
- `QualityWoWRegression`: `-5%`
- `SLO breach for:` `30m`

## 🔧 미분적 튜닝 접근법

### 1. z-score 임계값 조정
```yaml
# 현재
expr: duri_ndcg_z <= -2

# 후보값들
expr: duri_ndcg_z <= -2.2  # 경계값 탐색
expr: duri_ndcg_z <= -2.5  # 더 엄격
```

**기대 효과**: 경보/일 0.3↓, 미탐지↑ 0.05 내

### 2. WoW 회귀 임계값 조정
```yaml
# 현재
expr: duri_ndcg_wow_pct < -0.05

# 후보값들
expr: duri_ndcg_wow_pct < -0.06  # -6%
expr: duri_ndcg_wow_pct < -0.07  # -7%
```

**기대 효과**: 릴리즈 주간에 불필요 알람 20-30% 감소

### 3. SLO breach 지속시간 조정
```yaml
# 현재
for: 30m

# 후보값
for: 45m  # 페이지 부하↓ 25%
```

## 📈 ROC 곡선 기반 최적화

### F1-balanced 공식
```
F1_balanced = 2*(TPR*(1-FPR)) / (TPR + (1-FPR))
```

### 최적 임계값 탐색
```bash
# 최근 14일 데이터로 ROC 분석
argmax_t F1_balanced = 2*(TPR*(1-FPR)) / (TPR + (1-FPR))
```

## 🚀 튜닝 절차

### 1단계: 베이스라인 수집
```bash
# 현재 알람 발생률 측정 (7일간)
curl -s "http://localhost:9090/api/v1/alerts" | jq '.data.alerts | length'
```

### 2단계: 임계값 조정
```yaml
# prometheus/rules/quality_alerts.rules.yml 수정
- alert: QualityZScoreAnomaly
  expr: duri_ndcg_z <= -2.2  # -2 → -2.2
  for: 15m
```

### 3단계: 효과 측정
```bash
# 조정 후 알람 발생률 재측정
# TPR, FPR 계산
# F1-balanced 점수 계산
```

### 4단계: 반복 최적화
- 임계값을 미분적으로 조정
- F1-balanced가 최대가 되는 지점 탐색
- 운영팀 피드백 반영

## 📋 모니터링 지표

### 정확도 지표
- **True Positive Rate (TPR)**: 실제 이슈 탐지율
- **False Positive Rate (FPR)**: 오경보율
- **F1-balanced**: 균형잡힌 성능 지표

### 운영 지표
- **월간 알람 수**: 목표 ≤ 0.8회
- **평균 응답 시간**: Critical < 5분
- **해결 시간**: Warning < 30분

## 🎯 Day 69 확장 계획

### Burn Rate 알람
```yaml
- alert: QualityBurnRate2h
  expr: max_over_time(duri_ndcg_errbudget[2h]) > 0.1
  for: 15m

- alert: QualityBurnRate24h
  expr: max_over_time(duri_ndcg_errbudget[24h]) > 0.05
  for: 30m
```

### Synthetic Probe
- 스토리형 쿼리 세트 50개 고정
- 시간당 1회 자동 평가
- 탐지 민감도 레퍼런스 제공

## 🔍 24시간 검증 체크리스트

- [ ] Alertmanager `/-/ready` **200**
- [ ] 경보 건수/팀별 분포: 경고≤페이지
- [ ] nDCG/MRR **MA7** 수렴 추이 정상
- [ ] DR 타이머 확인
- [ ] 월간 알람 수 ≤ 0.8회 달성


