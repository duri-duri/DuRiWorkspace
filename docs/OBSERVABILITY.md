# DuRi 관찰 가능성 시스템

## 🎯 개요

Day 68에서 구현된 하이브리드 관찰 가능성 시스템으로, 통계적 이상감지와 SLO/에러버짓을 결합하여 운영 안정성을 확보합니다.

## 📊 시스템 구성

### **1. 통계적 이상감지 (A안)**
- **z-score 이상감지**: MA7/STD7 기준 통계적 이상 탐지
- **WoW 회귀감지**: 주간 대비 성능 하락 감지
- **즉시 급락감지**: 임계값 이하 즉시 알림

### **2. SLO/에러버짓 (B안)**
- **SLO breach 감지**: MA7 기준 서비스 수준 목표 위반
- **에러버짓 추적**: 허용 오차 범위 내 성능 모니터링
- **DoD 급락감지**: 전일 대비 급격한 성능 하락

### **3. 운영 안정성 (C안)**
- **CI 엄격 모드**: GA_ENFORCE=1, CROSS_TYPE_ENFORCE=1
- **DR 리허설**: 월 1회 백업 복구 검증
- **테스트 신뢰성**: 운영용/테스트용 룰 분리

## 🔧 Prometheus Rules

### **운영용 룰 (7d 윈도우)**
- `prometheus/rules/quality_recording.rules.yml`: 통계적 지표 계산
- `prometheus/rules/quality_slo.rules.yml`: SLO/에러버짓 계산
- `prometheus/rules/quality_alerts.rules.yml`: 알림 규칙

### **테스트용 룰 (5m 윈도우)**
- `tests/prom_rules/quality_recording.TEST.rules.yml`: 테스트용 통계 지표
- `tests/prom_rules/quality_alerts.test.yml`: 테스트 시나리오

## 📈 메트릭 지표

### **품질 지표**
- `duri_ndcg_at_k`: nDCG@3 (목표: ≥0.90)
- `duri_mrr_at_k`: MRR@3 (목표: ≥0.88)
- `duri_recall_at_k`: Recall@3 (목표: ≥0.98)

### **통계적 지표**
- `duri_ndcg_ma7`: 7일 이동평균
- `duri_ndcg_std7`: 7일 표준편차
- `duri_ndcg_wow_pct`: 주간 대비 변화율
- `duri_ndcg_z`: z-score

### **SLO 지표**
- `duri_ndcg_errbudget`: nDCG 에러버짓
- `duri_mrr_errbudget`: MRR 에러버짓
- `duri_recall3_errbudget`: Recall 에러버짓

## 🚨 알림 규칙

### **Critical (즉시 대응)**
- `QualityDropImmediate`: nDCG < 0.80 (5분)

### **Warning (모니터링)**
- `QualityWoWRegression`: WoW 하락 >5% (30분)
- `QualityZScoreAnomaly`: z-score <= -2 (15분)

### **Page (SLO 위반)**
- `RerankerNDCGSLOBreached`: nDCG SLO breach (30분)
- `RerankerMRRSLOBreached`: MRR SLO breach (30분)

### **Ticket (추적)**
- `RerankerQualityDoDDrop`: DoD 급락 >3% (15분)

## 🔄 CI/CD 통합

### **Makefile 타깃**
- `make prom-rules-verify`: Prometheus 룰 검증
- `make prom-rules-test`: Prometheus 룰 테스트
- `make prom-rules-ci`: 통합 검증
- `make validate-prom-all`: 모든 메트릭 파일 검증

### **PR 게이트**
- `make ci-pr-gate`: 전체 CI 게이트 (prom-rules-ci 포함)

## 🛡️ 백업 및 복구

### **DR 리허설**
- **서비스**: `kimshin-dr-restore.service`
- **타이머**: `kimshin-dr-restore.timer` (월 1회)
- **스크립트**: `backup/verify_and_restore.sh`

### **백업 시스템**
- **암호화**: age 기반 패스워드 암호화
- **무결성**: SHA256 체크섬 검증
- **해시 체인**: 로그 해시 체인 관리

## 📋 운영 가이드

### **일상 모니터링**
1. Grafana 대시보드에서 MA7, z-score, SLO 상태 확인
2. 알림 발생 시 심각도별 대응 절차 수행
3. 주간 성능 트렌드 분석 및 개선점 도출

### **장애 대응**
1. Critical 알림: 즉시 대응 (5분 내)
2. Warning 알림: 모니터링 강화 (15-30분)
3. SLO breach: 서비스 수준 회복 (30분 내)

### **정기 점검**
1. 월 1회 DR 리허설 실행
2. 분기별 SLO 목표 재검토
3. 연간 관찰 가능성 시스템 개선

## 🎯 성공 지표

### **탐지 정확도**
- False Positive: <5%
- False Negative: <1%
- 평균 탐지 시간: <15분

### **운영 안정성**
- CI 게이트 통과율: >95%
- DR 리허설 성공률: 100%
- 시스템 가용성: >99.9%

### **성능 목표**
- nDCG@3: ≥0.90
- MRR@3: ≥0.88
- Recall@3: ≥0.98
