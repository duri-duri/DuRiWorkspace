# 📊 메트릭스 검증 시스템

## 🎯 개요
Prometheus 메트릭스 파일의 품질을 보장하는 검증 시스템입니다.

## 🔧 환경변수

### `GA_ENFORCE`
- **기본값**: `false`
- **설명**: Google Analytics 강제 적용 여부
- **사용법**: `GA_ENFORCE=true bash scripts/metrics/validate_prom.sh file.prom`

### `MAX_PROM_SIZE`
- **기본값**: `1048576` (1MB)
- **설명**: 최대 파일 크기 제한 (바이트)
- **사용법**: `MAX_PROM_SIZE=2097152 bash scripts/metrics/validate_prom.sh file.prom`

## 📋 검증 규칙

### 1. HELP/TYPE 순서
- 모든 메트릭은 `# HELP` 다음에 `# TYPE`이 와야 함
- 중복된 HELP/TYPE 선언 금지

### 2. TYPE 상충 검사
- 동일한 메트릭명에 서로 다른 TYPE 선언 시 FAIL
- 예: `counter` ↔ `gauge` 상충

### 3. 숫자 표기 검증
- 지원 형식: `0`, `+0`, `-0`, `1.`, `.5`, `1.0`, `1e9`, `1E-9`, `+Inf`, `-Inf`, `NaN`
- 잘못된 형식은 promtool에서 자동 검출

### 4. 파일 크기 제한
- `MAX_PROM_SIZE`를 초과하는 파일은 거부
- 대용량 파일은 스트리밍 처리 권장

## 🚀 빠른 실행 예

### 기본 검증
```bash
bash scripts/metrics/validate_prom.sh my_metrics.prom
```

### 환경변수와 함께
```bash
GA_ENFORCE=true MAX_PROM_SIZE=2097152 bash scripts/metrics/validate_prom.sh my_metrics.prom
```

### 스트리밍 검증 (대용량 파일)
```bash
cat large_file.prom | bash scripts/metrics/validate_prom.sh /dev/stdin
```

## ❌ 실패 예시

### TYPE 상충
```prom
# HELP foo Foo counter
# TYPE foo counter
foo 1
# TYPE foo gauge  # ❌ 상충!
foo 2
```

### 잘못된 HELP/TYPE 순서
```prom
# TYPE foo gauge  # ❌ HELP가 먼저 와야 함
# HELP foo Foo
foo 1
```

### 잘못된 숫자 형식
```prom
# HELP foo Foo
# TYPE foo gauge
foo invalid_number  # ❌ 잘못된 형식
```

## 🧪 테스트 실행

### 스모크 테스트
```bash
# TYPE 상충 테스트
bash tests/smoke/test_prom_type_conflict.sh

# 숫자 더티케이스 테스트
bash tests/smoke/test_numbers_dirty.sh
```

### 전체 테스트
```bash
make ci-pr-gate
```

## 🔍 문제 해결

### promtool 오류
- `promtool`이 설치되어 있는지 확인
- `PATH`에 `promtool`이 포함되어 있는지 확인

### 권한 오류
- 스크립트에 실행 권한이 있는지 확인: `chmod +x scripts/metrics/validate_prom.sh`

### 메모리 부족
- `MAX_PROM_SIZE`를 줄이거나 스트리밍 처리 사용

## 📚 관련 문서
- [Prometheus 메트릭스 형식](https://prometheus.io/docs/concepts/metric_types/)
- [promtool 사용법](https://prometheus.io/docs/prometheus/latest/configuration/unit_testing_rules/)


