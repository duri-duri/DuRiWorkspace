# Phase 11 Runbook
## Run
- `scripts/core/phase11/run_phase11.sh`

## CI
- 존재하는 테스트 잡(Phase-2 Suite/tests) 안에서 `pytest tests/test_phase11_*.py` 실행

## 장애
- Core/Inner/Learning 중 하나 실패 시 해당 단계 재시도 후 degrade 모드로 진행
- `freeze` 라벨로 자동화 즉시 중단