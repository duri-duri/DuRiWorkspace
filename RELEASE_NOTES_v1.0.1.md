# Ops-Lock v1.0.1 릴리스 노트

## Apply Ops-Lock v1.0.1

### 1) 검증
```bash
git apply --check dist/ops-lock-v1.0.1.patch
```

### 2) 적용
```bash
git apply --whitespace=fix dist/ops-lock-v1.0.1.patch
```
(또는)
```bash
git am < dist/ops-lock-v1.0.1.mbox
```

### 3) 훅
```bash
pip install pre-commit && pre-commit install
```

### 4) 테스트
```bash
make up && make smoke
```

## 보장사항
- `/health` GET/HEAD=200, JSON 스키마 통일
- `/metrics` GET/HEAD=200 양 서비스
- `scripts/smoke_health_metrics.sh`로 회귀 자동 탐지
- CI 파이프라인 + 로그 아티팩트 수집
- 알림 룰: `DuriServiceDown`, `FiveXXSurge`

## 설치옵션
- tar.gz 번들: `dist/ops-lock-v1.0.1.tar.gz`
- Git patch mbox: `dist/ops-lock-v1.0.1.mbox`
- Git patch 파일: `dist/ops-lock-v1.0.1.patch`

## 운영 가이드
- `RUNBOOK.md` 포함
- `APPLY_OPS_LOCK.md` 상세 가이드 포함
