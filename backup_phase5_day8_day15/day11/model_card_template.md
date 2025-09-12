# DuRi Model Card v1 — **Autofilled Template**

## 5. 성능 (자동 채움)
| 항목 | 값 | 비고 |
|---|---:|---|
| 회귀 통과율 | **{{PASS_RATE}}** | auto_code_loop_beta/logs/test_result.json |
| p95 지연 | **{{P95_LATENCY}}** | slo_sla_dashboard_v1/metrics.json |
| Fail Rate(회귀) | **{{FAIL_RATE_REG}}** | slo_sla_dashboard_v1/metrics.json |
| 설명충분도 | **{{EXPLAIN_SCORE}}** | slo_sla_dashboard_v1/metrics.json |
| 안전 플래그 적중 | **{{SAFETY_HIT}}** | slo_sla_dashboard_v1/metrics.json |
| HITL 수용률 | **{{HITL_ACCEPT}}** | hitl_quality_report.json |

## 8. HITL 품질 (자동 채움)
- 품질 점수: **{{HITL_QUALITY}}**
- Cohen’s κ: **{{HITL_KAPPA}}**
- p95 처리시간: **{{HITL_P95H}}**
