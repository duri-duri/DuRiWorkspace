# 🚨 DuRi 회귀 대응 런북

## 🎯 **회귀 발생 시 3단계 대응**

### **1️⃣ 확인 (Detection)**

#### **CI 로그에서 회귀 감지**
```bash
# CI 로그에서 GUARD_RESULT=regression 라인 캡처
grep "GUARD_RESULT=regression" artifacts/guard.out
```

#### **프로메테우스 알람 확인**
```promql
duri_guard_last_exit_code{k="3",scope="all",domain="ALL"} == 2
```

### **2️⃣ 구분 (Classification)**

#### **Exit Code 기반 즉시 분기**
- **Exit 1 (인프라 오류)**: 파일 없음, 파싱 오류, NaN 등
- **Exit 2 (회귀)**: 성능 임계치 미달

#### **구분 명령어**
```bash
# 인프라 오류 확인
bash scripts/alerts/threshold_guard.sh /no/such.tsv 3; echo "exit:$?"

# 회귀 확인
TH_NDCG=0.99 TH_MRR=0.99 TH_ORACLE=1.1 GUARD_STRICT=1 \
  bash scripts/alerts/threshold_guard.sh .reports/metrics/day66_metrics.tsv 3; echo "exit:$?"
```

### **3️⃣ 재현 (Reproduction)**

#### **같은 SHA에서 재현**
```bash
# 현재 SHA에서 메트릭 재생성
make metrics-dashboard

# 결과 확인
cat .reports/metrics/day66_metrics.tsv
```

#### **베이스라인 SHA와 비교**
```bash
# 베이스라인 SHA로 체크아웃
git checkout day66-metrics-ga

# 베이스라인에서 메트릭 생성
make metrics-dashboard

# 결과 비교
diff .reports/metrics/day66_metrics.tsv /tmp/baseline_metrics.tsv
```

## 🔧 **대응 절차**

### **인프라 오류 (Exit 1)**
1. **파일 존재 확인**: `.reports/metrics/day66_metrics.tsv`
2. **헤더 형식 확인**: `scope\tdomain\tcount\tndcg@3\tmrr\toracle_recall@3`
3. **all 라인 확인**: 첫 번째 데이터 라인이 `all\t-\t...`
4. **수치 유효성 확인**: NaN, 빈 값 없음

### **회귀 (Exit 2)**
1. **임계치 확인**: `TH_NDCG`, `TH_MRR`, `TH_ORACLE` 값
2. **성능 비교**: 현재 vs 베이스라인 성능
3. **원인 분석**: 최근 변경사항 검토
4. **롤백 결정**: 필요시 이전 버전으로 롤백

## 📊 **모니터링 지표**

### **정상 상태**
- `duri_guard_last_exit_code{k="3",scope="all",domain="ALL"} = 0`
- `duri_ndcg_at_k{k="3",scope="all",domain="ALL"} >= 0.85`
- `duri_mrr{scope="all",domain="ALL"} >= 0.8`
- `duri_oracle_recall_at_k{k="3",scope="all",domain="ALL"} >= 0.9`

### **경고 상태**
- `duri_guard_last_exit_code{k="3",scope="all",domain="ALL"} = 1`
- 성능 지표 임계치 근접

### **위험 상태**
- `duri_guard_last_exit_code{k="3",scope="all",domain="ALL"} = 2`
- 성능 지표 임계치 미달

## 🚀 **자동 복구**

### **인프라 오류 자동 복구**
```bash
# 메트릭 파일 재생성
make metrics-dashboard

# 가드 재실행
bash scripts/alerts/threshold_guard.sh .reports/metrics/day66_metrics.tsv 3
```

### **회귀 자동 복구**
```bash
# 이전 버전으로 롤백
git checkout day66-metrics-ga

# 시스템 재시작
make restart-shadow
```


