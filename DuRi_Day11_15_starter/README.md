# DuRi Day11 & Day15 Starter Pack

## 구성
- `model_card_v1.md` — Day 11 산출물 초안
- `auto_code_loop_beta/` — Day 15 베타 스켈레톤
  - `policy.yaml`, `runner.py`, `gates/*`, `promote.sh`, `logs/`
- `slo_sla_dashboard_v1/metrics.json` — 실패예산 소스 메트릭 샘플
- `failure_budget_alerts.py` — Day 17 알림 스크립트(미리 포함)
- `error_to_goal.py` — Day 16 변환 스크립트(미리 포함)

## 빠른 실행
```bash
# 1) 회귀 더미 결과 생성
bash auto_code_loop_beta/gates/run_regression_tests.sh

# 2) 리스크 계산 + 프로모션 시도
python auto_code_loop_beta/runner.py

# 3) 실패예산 확인(OK/FREEZE.FLAG 생성)
python failure_budget_alerts.py

# 4) 실패→학습목표 변환
python error_to_goal.py --in auto_code_loop_beta/logs/test_result.json --out auto_code_loop_beta/logs/goals.json
```
