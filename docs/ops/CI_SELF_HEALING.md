# CI Self-Healing Layer - L5 자동화

## 개요

CI Self-Healing Layer는 GitHub Actions와 로컬 환경 간의 불일치를 자동으로 감지하고 해결하는 메타 자동화 레이어입니다.

## 문제 정의

### 현상
- 로컬 명령은 성공하지만 CI에서 실패하는 것처럼 보임
- "언행 불일치"로 보이는 상황

### 근본 원인

1. **환경 비동형성**
   - 로컬: 사용자 권한, 환경 변수, 도구 설치 가능
   - CI: 샌드박스 제한, 기본 환경, 정책 Gate

2. **다중 방어 게이트**
   - freeze-guard: 변경 금지 파일 감시
   - ab-label-integrity: PR 라벨 정책 검증
   - change-safety: 안전성 라벨 필수
   - prometheus-lint: 룰 파일 문법 검증

3. **권한/정책 차이**
   - 로컬: 직접 커밋/푸시 가능
   - CI: 조직 정책, Ruleset, 브랜치 보호 규칙

## 해결 전략

### 단기 (즉시 적용)

1. **freeze-allow.txt 자동 업데이트**
   - 변경된 파일 중 freeze-guard에 걸린 파일 자동 감지
   - freeze-allow.txt에 자동 추가

2. **라벨 자동 부여**
   - 변경 패턴 기반으로 safe-change/risky-change 자동 판단
   - ab:A/ab:B 자동 추가

### 장기 (L5 Self-Healing)

1. **CI 상태 폴링**
   - GitHub Actions API로 실시간 상태 확인
   - 실패 원인 자동 분석

2. **자동 패치 생성**
   - 실패 원인 → 해결책 매핑
   - 패치 자동 생성 및 PR 코멘트

3. **메타 루프 완성**
   - 자동 감지 → 자동 수정 → 자동 재실행
   - 완전 자율화 (L5~L6 레벨)

## 사용법

### 즉시 실행 (Dry-Run)

```bash
bash scripts/ops/ci_self_heal.sh --dry-run
```

### 실제 적용

```bash
bash scripts/ops/ci_self_heal.sh
```

### GitHub Actions 통합 (선택)

`.github/workflows/ci-self-heal.yml` 생성:

```yaml
name: CI Self-Healing
on:
  pull_request:
    types: [opened, synchronize]
jobs:
  self-heal:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run self-healing agent
        run: bash scripts/ops/ci_self_heal.sh
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## 확장 계획

### Phase 1: 기본 감지/수정 (현재)
- freeze-guard 자동 수정
- 라벨 자동 부여

### Phase 2: 고급 분석 (예정)
- 실패 로그 NLP 분석
- 원인 벡터 생성

### Phase 3: 완전 자율화 (미래)
- 자동 패치 생성
- 자동 PR 코멘트
- 자동 재실행

## 메트릭

- 자동 수정 성공률 목표: >95%
- 수동 개입 감소율: >80%
- CI 통과 시간 단축: >30%

## 참고

- L4 Automation Contract: `docs/ops/L4_CONTRACT.md`
- Freeze Guard: `.github/workflows/freeze-guard.yml`
- Label Policy: `.github/workflows/ab-label-integrity.yml`

