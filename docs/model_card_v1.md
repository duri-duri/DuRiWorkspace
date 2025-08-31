# DuRi Model Card v1

## 1. 목적(Purpose) / 비범위(Non-goals) / 금지영역(Guardrails)
- 목적: 대화·계획·자가개선이 결합된 **운동 재활 어시스턴트**로서 정확/일관/안전한 의사결정 보조.
- 비범위: 의사 의료행위 대체, 실시간 생체신호 의사결정(고위험) 자동화.
- 금지영역: 개인정보 재식별, 비허용 툴 호출, 의료법·개인정보법 위반 행위.

## 2. I/O 계약(Contract)
- 입력: 텍스트 지시/로그(ko/en), 구조화 상태(JSON: goals, pain, session_log).
- 출력: 계획(steps), 근거(rationale), 측정지표(metrics_update), 위험경고(risks).
- 오류모드: 타임아웃/툴 실패/루프 과소·과다.  
  - 처리: 재시도≤1, 실패 스냅샷 저장, 비용/지연 상한 초과 시 중단.

## 3. 데이터/프롬프트 관리
- 출처: 자체 생성 로그(TODAY_WORK_SUMMARY.md 등), 로컬 문서, 비공개 지식.
- 제외/보호: PII 마스킹, 오프사이트 전송 금지, 백업은 암호화 후 로컬/USB만.

## 4. 평가(evaluation) — 12태스크 & 목표치
> 상세 스키마: `eval/metrics.yaml`

| Task | 설명 | 지표 | 목표 |
|---|---|---|---|
| t1_reasoning_simple | 짧은 임상적 추론 | accuracy | ≥ 0.90 |
| t2_reasoning_complex | 다단계 계획 | accuracy | ≥ 0.80 |
| t3_tool_use | 백업/헬스체크 툴 사용 | success_rate | ≥ 0.95 |
| t4_retrieval | 문서 회수 | top1_recall / MRR | ≥ 0.95 / ≥ 0.90 |
| t5_safety | 안전정책 준수 | violation_rate | = 0 |
| t6_memory | 이전 세션 기억 | hit_rate | ≥ 0.85 |
| t7_instruction_following | 지시 충실 | pass_rate | ≥ 0.9 |
| t8_code_small | 스크립트 생성 | pass@1 | ≥ 0.8 |
| t9_code_fix | 패치 제안 | pass@1 / diff_size | ≥ 0.7 / 최소화 |
| t10_planning | 실행계획 품질 | success_rate / steps | ≥ 0.9 / ≤ 기준 |
| t11_dialog_robust | 잡음·오류 견딤 | pass_rate | ≥ 0.85 |
| t12_regression_suite | 회귀 실패건 | failures / flaky_rate | = 0 / ≤ 2% |

## 5. 모니터링 & 롤백
- 온라인 모니터: latency_ms, tokens, tool_error_rate, backup_freshness_h.
- 임계값: `latency_p95≤2.0s`, `tool_error_rate<1%`, `backup_incr≤48h`, `full≤168h`.
- 롤백: 태그 `pre-day11-YYYY-MM-DD` 로 되돌림, 실패 스냅샷 보관.

## 6. 리스크 & 완화
- 프롬프트 인젝션 → 입력 살균·도구 allow/deny-list.
- 데이터 누출 → 마스킹+오프사이트 차단.
- 비용 폭주 → budget gate + kill-switch.
- 회귀 드리프트 → 고정 벤치+주간 리프레시.
- 롤백 실패 → 사전 스냅샷 + 자동 롤백.

## 7. 거버넌스
- 책임자: 원장(Owner), 실행: DuRi Ops.
- 변경관리: PR 필수, 회귀통과 필수, 태그·릴리즈 노트 필수.

*버전: v1.0 / 태그: pre-day11-2025-08-31*
