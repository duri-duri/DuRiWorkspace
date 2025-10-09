# 📊 DuRi Observability 가이드

## 🎯 **메트릭 라벨 계약 (GA 품질)**

### **라벨셋 표준**

모든 메트릭은 다음 3개 라벨을 사용합니다:
- `k`: 숫자만 (예: `"3"`)
- `scope`: 범위 (예: `"all"`, `"domain"`)
- `domain`: 도메인 (예: `"ALL"`, `"health"`)

### **라벨 정규화 규칙**

1. **`scope="all"`일 때 `domain="ALL"`** (대문자)
2. **`k`는 숫자만** (콤마 없음)
3. **라벨 순서**: `k, scope, domain` 고정

### **예제 라인**

```prometheus
# HELP duri_ndcg_at_k NDCG@k
# TYPE duri_ndcg_at_k gauge
duri_ndcg_at_k{k="3",scope="all",domain="ALL"} 0.922629
duri_ndcg_at_k{k="3",scope="domain",domain="health"} 0.922629

# HELP duri_mrr Mean Reciprocal Rank
# TYPE duri_mrr gauge
duri_mrr{scope="all",domain="ALL"} 0.9
duri_mrr{scope="domain",domain="health"} 0.9

# HELP duri_oracle_recall_at_k Oracle recall@k
# TYPE duri_oracle_recall_at_k gauge
duri_oracle_recall_at_k{k="3",scope="all",domain="ALL"} 1.0
duri_oracle_recall_at_k{k="3",scope="domain",domain="health"} 1.0

# HELP duri_guard_last_exit_code Guard script last exit code (0 ok, 1 infra, 2 regression)
# TYPE duri_guard_last_exit_code gauge
duri_guard_last_exit_code{k="3",scope="all",domain="ALL"} 0
```

### **상태코드 계약**

- `0`: 정상 또는 비엄격 모드
- `1`: 인프라/파싱 오류 (파일 없음, all 라인 누락, NaN 등)
- `2`: 회귀 (엄격 모드)

### **표준 출력 형식**

```
GUARD_RESULT=ok|regression K=<k> ndcg=<...> mrr=<...> oracle=<...>
```

## 🔍 **프로메테우스 쿼리 스니펫**

### **현재 값**
```promql
duri_ndcg_at_k{k="3",scope="all",domain="ALL"}
```

### **6시간 이동평균**
```promql
avg_over_time(duri_ndcg_at_k{k="3",scope="all",domain="ALL"}[6h])
```

### **드롭 알람**
```promql
avg_over_time(duri_ndcg_at_k{k="3",scope="all",domain="ALL"}[1h]) < on() (avg_over_time(duri_ndcg_at_k{k="3",scope="all",domain="ALL"}[6h]) - 0.05)
```

### **회귀 탐지**
```promql
duri_guard_last_exit_code{k="3",scope="all",domain="ALL"} == 2
```

## 📊 **대시보드 설정**

### **기본 변수**
- `domain`: `ALL` (기본값)
- `scope`: `all` (기본값)
- `k`: `3` (기본값)

### **Guard 상태 패널**
```promql
duri_guard_last_exit_code{domain="$domain",scope="$scope",k="$k"}
```

## 🚨 **알람 규칙**

### **회귀 탐지 (5분 지속)**
```yaml
- alert: RAG_Regression_Detected
  expr: duri_guard_last_exit_code{k="3",scope="all",domain="ALL"} == 2
  for: 5m
  labels: { severity: critical }
  annotations:
    summary: "RAG 성능 회귀 감지"
    description: "Guard exit code가 2로 지속됨 (회귀 모드)"
```

### **nDCG 하락**
```yaml
- alert: RAG_NDCG_Drop
  expr: (duri_ndcg_at_k:avg_6h - duri_ndcg_at_k:avg_1h) > 0.05
  for: 15m
  labels: { severity: warning }
  annotations:
    summary: "nDCG drop over last 6h (moving average)"
    description: "nDCG@{{ $labels.k }} fell by >0.05. 6h_avg={{ $value }}, 1h_avg={{ $labels.avg_1h }}"
```
