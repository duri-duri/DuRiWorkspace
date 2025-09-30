# Day 38 — Auto Code Loop Improvements

## 목표
- 실패 패턴 자동 추출 → 규칙화 → 패치 후보 제안 → 게이트/테스트 재실행 자동화

## 범위
- CI 로그/테스트 실패로부터 신호 수집
- 규칙 저장소(failure_patterns.yml) 및 자동 패치 제안기(auto_fix_suggester.py)
- Make 타깃과 워크플로(github actions) 연동

## 산출물
- tools/auto_fix_suggester.py
- tools/failure_patterns.yml
- tests/day38/test_auto_fix_suggester.py
- Makefile: day38.* 타깃
- .github/workflows/proof-gates.yml: day38 단계 훅

## 마일스톤
- M1(룰 베이스): 실패 패턴 → 제안 패치 diff 출력
- M2(안전 실행): 제안 패치 dry-run & 로컬 테스트
- M3(CI 통합): PR 코멘트로 패치 제안, 옵트인 적용

## 리스크/가드
- 잘못된 자동 수정을 막기 위해: 모든 패치는 --dry-run/PR-suggestion only
- 게이트: tests + guards + ab-days 전부 통과 필요

## M2: Dry-run Patch Generator

### 목표
- 제안된 패치를 실제 파일에 적용하지 않고 diff로 출력
- 로컬 테스트 자동 실행으로 패치 검증
- 안전한 패치 생성 및 검증 파이프라인 구축

### 구현 계획
- `tools/patch_generator.py`: AST 기반 파일 수정
- `tools/dry_run_patcher.py`: 안전한 패치 적용 및 롤백
- `tests/day38/test_patch_generator.py`: 패치 생성 테스트
- `Makefile`: `day38.patch` 타깃 추가

### 리스크 관리
- 모든 패치는 `--dry-run` 모드로만 실행
- 실제 파일 수정 전 백업 및 롤백 메커니즘
- 패치 적용 후 자동 테스트 실행
