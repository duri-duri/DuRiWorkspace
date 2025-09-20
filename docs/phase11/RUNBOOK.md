# Phase 11 Runbook

## D02 완료 상태 ✅
- 브랜치: `ops/phase11-integration`
- 스캐폴드/문서/스모크/CI/프리즈 규칙: 준비 완료
- 회귀 테스트 커밋 + CI 아티팩트/업데이트 가드: 완료

## 재개 체크리스트 (D02 → D03 시작용)

### 1. 작업 브랜치로 복귀 + 최신화
```bash
git switch ops/phase11-integration
git fetch origin
git rebase origin/main
```

### 2. 로컬 테스트 확인
```bash
python3 -m pytest tests/test_phase11_*.py -q
```

### 3. PR 상태 확인
```bash
gh pr status
gh pr checks --watch
```

### 4. 브랜치 보호 컨텍스트 일치 점검 (필요시)
```bash
gh api repos/:owner/:repo/branches/main/protection | jq '.required_status_checks.contexts'
# 요구 체크: freeze-guard/guard, repo-guards/guards, Phase-2 Suite/tests
```

## D03 즉시 착수 항목 (실연동)
- **DuRiCoreAdapter.reply()** → 실제 Core API/모듈 바인딩
- **InnerThoughtAdapter.reflect()** → 자기성찰 엔진 호출  
- **ExternalLearningAdapter.learn()** → 문서 인덱싱/임베딩 파이프라인 트리거
- **Telemetry.record()** → `insight/` 점수(예: coherence/novelty/brevity) 계산 후 JSONL 기록

## 실행 궤도 유지용 권장
- `scripts/core/phase11/` 안에 `adapters/` 서브패키지로 실제 바인딩을 분리(테스트 더 쉬워짐)

## 테스트/CI 빠른 가드
- **스모크**: assistant/inner 내용 구분 + `learned=True` 검증 (이미 적용)
- **회귀**: 최소 1개 골든, 1개 네거티브 케이스 유지
- **CI**: `.github/workflows/insight-ci.yml`에 `pytest -q tests/test_phase11_*.py` 실행 라인 **남겨두기**

## 모서리 케이스(오토머지 멈춤) → 즉시 복구법
- strict 업데이트로 **브랜치 뒤처짐** 시:
  ```bash
  gh pr view --json isCrossRepository,headRefName,baseRefName,mergeStateStatus
  gh pr edit --add-label automerge
  git fetch origin && git rebase origin/main && git push -f
  ```
- 라벨 누락 시: `automerge` 라벨만 다시 붙이면 재시도됨
- freeze 거부 시: `.github/freeze-allow.txt`의 **임시 규칙**에 Phase11 경로 유지되어 있는지 확인
  (안정화 후 `^tests/test_phase11_.*\.py$` 허용은 런북 TODO대로 축소/삭제)

## 폴더 합의(재확인)
- 코드: `scripts/core/phase11/`
- 문서: `docs/phase11/`
- 테스트: `tests/test_phase11_*.py`
- 텔레메트리 트레이스: `DuRiCore/memory/phase11_traces/*.jsonl` (가볍게 유지)

## 빠른 헬스체크 커맨드(현장용)
```bash
# 전체 상태
git status && gh pr status

# 로컬 스모크/회귀
pytest -q tests/test_phase11_*.py -q

# 텔레메트리 라인 확인
grep -R "phase11::telemetry" -n scripts/core/phase11 || true

# 보호 규칙 컨텍스트
gh api repos/:owner/:repo/branches/main/protection | jq '.required_status_checks.contexts'
```

## D03 완료 기준(AC)
- 실제 어댑터 on/off를 **플래그 한 줄**로 전환 가능
- 실패 시 **폴백 경로**가 항상 동작(테스트로 보장)
- CI에서 골든/실패 케이스 전부 통과
- RUNBOOK에 **롤백 절차**(플래그 off + 데모 로직) 명시
- 임시 freeze 허용 패턴 축소(PR로 제거)

## TODO: D03 끝나면 `^tests/test_phase11_.*\.py$` 허용 제거