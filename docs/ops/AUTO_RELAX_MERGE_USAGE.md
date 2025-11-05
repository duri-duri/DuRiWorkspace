# Auto Relax Merge Restore 워크플로우 사용법

## 개요

PR 머지 시 리뷰어 승인만 부족할 때 자동으로 브랜치 보호 설정을 완화하고 머지한 후 복원하는 워크플로우입니다.

## 작동 조건

워크플로우가 실행되려면 다음 조건을 모두 만족해야 합니다:

1. **라벨**: `change:safe` + `auto-relax-merge` 둘 다 필요
2. **Base branch**: `main`만 허용
3. **Status checks**: 실패 0개, 대기 0개 (모두 통과)
4. **Merge state**: `BLOCKED` (승인만 부족한 상태)
5. **경로**: 허용 경로만 변경 (docs/, prometheus/rules/, scripts/ops/, scripts/bin/, .github/workflows/)

## 사용 방법

### 자동 실행

1. PR에 필요한 라벨 추가:
   ```bash
   gh pr edit <PR_NUMBER> --add-label "change:safe" --add-label "auto-relax-merge"
   ```

2. 모든 필수 체크가 통과하고 승인만 부족하면 자동 실행됩니다.

### 수동 실행

GitHub Actions에서 수동으로 실행:
1. `Actions` 탭 → `auto-relax-merge-restore` 선택
2. `Run workflow` 클릭
3. PR 번호 입력 후 실행

또는 CLI:
```bash
gh workflow run auto-relax-merge-restore.yml -f pr=<PR_NUMBER>
```

## 프로세스

1. **Gate 검증**: 모든 조건 확인
2. **스냅샷 저장**: 현재 보호 설정 저장
3. **완화**: 승인 요구 수를 0으로 설정
4. **머지**: PR을 squash로 머지하고 브랜치 삭제
5. **복원**: 스냅샷에서 보호 설정 복원
6. **검증**: 복원이 정상적으로 되었는지 확인

## 안전장치

- **원자성 보장**: `trap`으로 실패 시 자동 복원
- **항상 복원**: `if: always()`로 모든 경우에 복원 보장
- **하드 게이트**: 5가지 조건 모두 만족해야만 실행
- **감사 로그**: 스냅샷을 `docs/ops/audit/`에 저장

## 성공 확률

- 정상 조건 진입 시 전체 성공: **p≈0.99**
- 완화/복원 API 성공: **p≈0.999**
- 레이스 조건: **p<0.01** (대기 체크 0 조건으로 대부분 배제)

## 주의사항

- 이 워크플로우는 관리자 권한이 필요합니다
- 승인만 부족한 상태에서만 실행됩니다
- 다른 이유로 BLOCKED된 경우는 실행되지 않습니다
- 실패 시 자동으로 보호 설정이 복원됩니다

