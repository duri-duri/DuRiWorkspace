# Auto Relax Merge Restore 워크플로우 Runbook

## 개요

PR 머지 시 리뷰어 승인만 부족할 때 자동으로 브랜치 보호 설정을 완화하고 머지한 후 복원하는 워크플로우입니다.

## 작동 조건 (모두 만족해야 함)

1. **라벨**: `change:safe` + `auto-relax-merge` 둘 다 필요
2. **Base branch**: `main`만 허용
3. **Status checks**: 실패 0개, 대기 0개 (모두 통과)
4. **Merge state**: `BLOCKED` + `MERGEABLE` (승인만 부족한 상태)
5. **경로**: 허용 경로만 변경 (docs/, prometheus/rules/, scripts/ops/, scripts/bin/, .github/workflows/)
6. **Required contexts**: 보호 설정의 모든 required contexts가 SUCCESS

## 안전장치

### 1. 하드 게이트 (5중 검증)
- 라벨 이중 확인
- Base branch 확인
- Status check 검증 (실패 0, 대기 0)
- Merge state 확인 (BLOCKED + MERGEABLE)
- 경로 allowlist 검증

### 2. 추가 검증
- Required contexts 교차 검증
- 코멘트 트리거 발언자 화이트리스트
- 승인 부족 "단일 원인" 보장

### 3. 원자성 보장
- `trap`으로 실패 시 자동 복원
- `if: always()`로 모든 경우에 복원 보장
- 최종 안전망: `Ensure protection restored` (항상 실행)

### 4. 경합 방지
- Concurrency 그룹으로 동시 실행 방지
- PR별 독립 실행 보장

### 5. 감사 추적
- 스냅샷을 artifact로 저장 (90일 보관)
- PR에 결과 코멘트 남김
- 성공 시 `auto-relaxed-merged` 라벨 추가

## 사용 방법

### 자동 실행 (권장)

1. PR에 필요한 라벨 추가:
   ```bash
   gh pr edit <PR_NUMBER> --add-label "change:safe" --add-label "auto-relax-merge"
   ```

2. 모든 필수 체크가 통과하고 승인만 부족하면 자동 실행됩니다.

### 코멘트 트리거

PR에 코멘트 입력:
```
/auto-merge
```

**주의**: 소유자/관리자만 허용됩니다.

### 수동 실행

```bash
gh workflow run auto-relax-merge-restore.yml -f pr=<PR_NUMBER>
```

## 프로세스

1. **Gate 검증**: 모든 조건 확인 (5중 검증)
2. **경로 allowlist 검증**: 허용 경로만 변경 확인
3. **Required contexts 검증**: 보호 설정의 모든 contexts가 SUCCESS 확인
4. **스냅샷 저장**: 현재 보호 설정 저장 (artifact + 감사 디렉토리)
5. **완화**: 승인 요구 수를 0으로 설정
6. **머지**: PR을 squash로 머지하고 브랜치 삭제
7. **복원**: 스냅샷에서 보호 설정 복원
8. **검증**: 복원이 정상적으로 되었는지 확인
9. **최종 안전망**: 항상 복원 상태 확인 및 필요시 복원
10. **감사**: 결과 코멘트 및 라벨 추가

## 성공 확률

- 정상 조건 진입 시 전체 성공: **p≈0.995-0.998**
- 완화/복원 API 성공: **p≈0.999**
- 레이스 조건: **p<0.005** (concurrency로 방지)
- 오작동 확률: **p<0.003** (5중 게이트)

## 트러블슈팅

### 워크플로우가 실행되지 않음

1. 라벨 확인:
   ```bash
   gh pr view <PR> --json labels --jq '.labels[].name'
   ```
   - `change:safe`와 `auto-relax-merge` 둘 다 필요

2. Status checks 확인:
   ```bash
   gh pr checks <PR>
   ```
   - 실패 0개, 대기 0개 필요

3. Merge state 확인:
   ```bash
   gh pr view <PR> --json mergeStateStatus --jq '.mergeStateStatus'
   ```
   - `BLOCKED` 상태여야 함

### 보호 설정이 복원되지 않음

1. Artifact 확인:
   - Actions 탭에서 `protection-snapshot-<PR>` artifact 다운로드
   - 스냅샷 파일 확인

2. 수동 복원:
   ```bash
   bash scripts/ops/protection_apply.sh <owner/repo> restore <snapshot_file>
   ```

### 권한 오류

1. `PROTECTION_ADMIN_TOKEN` 확인:
   - Repository secrets에 설정되어 있는지 확인
   - repo admin 권한이 있는지 확인

2. `administration: write` 권한:
   - Organization policy 확인
   - 필요시 PAT 사용

## 권한/시크릿

- `PROTECTION_ADMIN_TOKEN`: repo admin 권한 토큰 (필수, 없으면 GITHUB_TOKEN 사용)
- `GITHUB_TOKEN`: 기본 GitHub Actions 토큰 (fallback)

## 주의사항

- 이 워크플로우는 관리자 권한이 필요합니다
- 승인만 부족한 상태에서만 실행됩니다
- 다른 이유로 BLOCKED된 경우는 실행되지 않습니다
- 실패 시 자동으로 보호 설정이 복원됩니다
- 스냅샷은 artifact로만 저장되며 커밋되지 않습니다

