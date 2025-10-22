# Day 15 DoD (Auto Code Loop Beta)

## Gates
- [ ] G0 정책 파일 존재 (policies/auto_code_loop/gate_policy.yaml)
- [ ] G1 PR rate-limit 준수 (≤ 3/day)
- [ ] G2 정책 검증 통과 (policy_verify.sh --policy …)
- [ ] G3 Unit 테스트 통과 (또는 N/A)
- [ ] G4 회귀 12태스크 통과 (run_regression_tests.sh)
- [ ] G5 Security 재검증 통과 (--scan)
- [ ] G6 롤백 스모크 테스트 통과 (smoke_restore_test.sh)

## 배포/운영
- [ ] 커밋/태그: `[auto-code-loop] PR: … [policy:v1]`, 태그 `day15-beta-YYYYMMDD_HHMM`
- [ ] 카나리 10% 적용, Grafana 주석 남김
- [ ] 카나리 기준 위반 시 자동 롤백 확인(p95↑>10% 또는 err>1%)
- [ ] 로그 보존: `logs/auto_code_loop_beta/YYYY-MM-DD/`

## 산출물
- [ ] 실행 로그(run.log), unit.log, regression.log, security.log, restore.log, canary.log
- [ ] 변경 파일 요약 및 diff 링크(또는 첨부)
- [ ] 리스크 레지스터 업데이트(필요 시)
