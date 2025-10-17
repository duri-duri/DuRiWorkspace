# 📊 Grafana 빠른 패널 스니펫

## 🎯 **Guard 상태 패널**

### **쿼리**
```promql
max by() (duri_guard_last_exit_code{scope="all",domain="ALL"})
```

### **설정**
- **Panel Type**: Stat
- **Unit**: None
- **Thresholds**:
  - 0: Green (정상)
  - 1: Yellow (인프라 오류)
  - 2: Red (회귀)

## 📈 **품질 추세 패널**

### **쿼리**
```promql
avg_over_time(duri_ndcg_at_k{k="3",scope="all",domain="ALL"}[6h])
```

### **설정**
- **Panel Type**: Time series
- **Unit**: Percent (0-1)
- **Y-axis**: 0 to 1

## 🚨 **회귀 탐지 패널**

### **쿼리**
```promql
duri_guard_last_exit_code{k="3",scope="all",domain="ALL"} == 2
```

### **설정**
- **Panel Type**: Stat
- **Unit**: None
- **Thresholds**:
  - 0: Green (정상)
  - 1: Red (회귀 감지)

## 📊 **메트릭 대시보드**

### **nDCG@3 추이**
```promql
duri_ndcg_at_k{k="3",scope="all",domain="ALL"}
```

### **MRR 추이**
```promql
duri_mrr{scope="all",domain="ALL"}
```

### **Oracle-Recall@3 추이**
```promql
duri_oracle_recall_at_k{k="3",scope="all",domain="ALL"}
```

## 🔧 **빌드 정보 패널**

### **Git SHA**
```promql
duri_build_info{git_sha!=""}
```

### **메트릭 생성 시간**
```promql
duri_metrics_generated_seconds
```

## 🚨 **알람 상태 패널**

### **텍스트파일 정체**
```promql
time() - duri_metrics_generated_seconds > 15*60
```

### **설정**
- **Panel Type**: Stat
- **Unit**: None
- **Thresholds**:
  - 0: Green (정상)
  - 1: Red (정체)

## 📋 **기본 변수**

- `domain`: `ALL` (기본값)
- `scope`: `all` (기본값)
- `k`: `3` (기본값)
- `git_sha`: `.*` (모든 SHA)


