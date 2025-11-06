# Label Policy Schema - 단일 소스 규칙

## 개요

이 문서는 PR 라벨 정책의 단일 소스(Single Source of Truth)입니다. 모든 라벨 자동화는 이 스키마를 기준으로 동작합니다.

## 라벨 정책 규칙

### 1. AB 그룹 라벨 (상호 배타)

**규칙**: `ab:` 라벨은 **정확히 하나만** 존재해야 합니다.

| 라벨 | 사용 조건 | 충돌 |
|------|----------|------|
| `ab:A` | risky-change가 있는 경우 | `ab:B`, `ab:none` |
| `ab:B` | risky-change + B 분기 실험 | `ab:A`, `ab:none` |
| `ab:none` | safe-change가 있는 경우 | `ab:A`, `ab:B` |

**자동 해결 규칙**:
- `safe-change` → `ab:none` 강제 (ab:A/ab:B 자동 제거)
- `risky-change` → `ab:A` 또는 `ab:B` 필요 (ab:none 자동 제거)
- 둘 다 없으면 → 파일 패턴 기반 자동 판단

### 2. Change-Safety 라벨 (필수)

**규칙**: `safe-change` 또는 `risky-change` 중 **정확히 하나** 필요합니다.

| 라벨 | 파일 패턴 | 자동 판단 기준 |
|------|----------|---------------|
| `safe-change` | `prometheus/rules/`, `scripts/ops/`, `docs/ops/`, `.gitignore`, `.githooks/` | 기본값 (안전한 변경) |
| `risky-change` | `config/`, `.slo/`, `rulepack/` | 위험한 경로 포함 시 |

### 3. 메타데이터 라벨 (권장)

| 카테고리 | 라벨 형식 | 예시 | 자동 판단 기준 |
|---------|---------|------|---------------|
| Type | `type:*` | `type:ops`, `type:feature`, `type:fix` | 변경 파일 패턴 분석 |
| Area | `area:*` | `area:observability`, `area:backend` | 변경 파일 경로 분석 |
| Size | `size:*` | `size:S`, `size:M`, `size:L` | 변경 파일 수 기준 |

**Size 판단 기준**:
- `size:S`: 변경 파일 < 5개
- `size:M`: 변경 파일 5-20개
- `size:L`: 변경 파일 > 20개

## 정책 적용 우선순위

1. **Conflict Resolution** (최우선)
   - `safe-change` + `ab:A` → `ab:A` 제거, `ab:none` 추가
   - `risky-change` + `ab:none` → `ab:none` 제거, `ab:A` 추가

2. **Missing Label Detection**
   - change-safety 없음 → 파일 패턴 분석 후 자동 추가
   - ab: 그룹 없음 → 기본값 `ab:none` 추가
   - type/area/size 없음 → 변경 파일 기반 자동 추가

3. **Duplication Cleanup**
   - ab: 그룹 중복 → 정책에 따라 하나만 유지
   - 같은 카테고리 라벨 중복 → 우선순위 기반 선택

## 자동화 스크립트

### ci_self_heal.sh
- CI 실패 감지 시 자동 실행
- 정책 규칙 자동 적용
- 충돌 자동 해결

### ci_fix_label_and_ready.sh
- 원샷 PR 라벨 정리
- 필수 라벨 자동 추가
- Draft 해제 제안

## 사용 예시

```bash
# 자동 라벨 정리
bash scripts/ops/ci_fix_label_and_ready.sh 86

# Self-Healing Agent 실행
bash scripts/ops/ci_self_heal.sh

# Dry-Run (테스트)
bash scripts/ops/ci_self_heal.sh --dry-run
```

## 재발 방지

1. **GitHub Actions 통합**
   - PR 생성/업데이트 시 자동 실행
   - 라벨 변경 이벤트 트리거

2. **Pre-commit Hook**
   - 라벨 스키마 준수 검증
   - 잘못된 조합 사전 차단

3. **단일 소스 유지**
   - 이 문서가 유일한 정책 정의
   - 모든 스크립트는 이 스키마 기반

## 버전

- **생성일**: 2025-11-06
- **버전**: 1.0.0
- **상태**: Stable

