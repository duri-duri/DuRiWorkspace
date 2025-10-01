# 🚀 **DuRi: 인간형 AI 빌드업 90일 로드맵**

## 📅 **프로젝트 개요**
- **목표**: 단순 대화형 AI → 인간형 지능 아키텍처로 진화
- **핵심 역량**: 언어 이해–추론–메타인지–자가개선
- **최종 목표**: Day90 이후 DuRi v1.0 공개

---

## 🎯 **Phase 1: Day 1-30 (기반 구축)**

### **Week 1-2: Trace v2 아키텍처**
- **Day 1**: Trace v2 설계 및 스키마 확정 → `trace_v2_schema.json`
- **Day 2**: Trace v2 전 모듈 임시 적용 → `trace_v2_temp_impl/`
- **Day 3**: 회귀 벤치마크 12태스크 선정 → `regression_bench_list.yaml`
- **Day 4**: 회귀 테스트 자동화 스크립트 → `run_regression_tests.sh`
- **Day 5**: 실패 유형 사전 정의 → `failure_types_catalog.md`

### **Week 3-4: 핵심 시스템 구축**
- **Day 6**: 모듈별 Trace v2 전면 적용 → `trace_v2_full_impl/`
- **Day 7**: 샌드박스 환경 구축 → `sandbox_env_config/`
- **Day 8**: 자가코딩 루프 베타 설계 → `auto_code_loop_plan.md`
- **Day 9**: HITL 기본 프로토콜 → `hitl_protocol.md`
- **Day 10**: 학습 큐레이터 MVP 설계 → `learning_curator_mvp_plan.md`

### **Week 5-6: 품질 및 배포 준비**
- **Day 11**: 모델 카드 v1 → `model_card_v1.md`
- **Day 12**: 카나리 배포 환경 → `canary_env_setup/`
- **Day 13**: 롤백 스크립트 → `rollback.sh`
- **Day 14**: SLO/SLA 정의 → `slo_sla_dashboard_v1/`
- **Day 15**: 자가코딩 루프 안전영역 베타 → `auto_code_loop_beta/`

### **Week 7-8: 자동화 및 모니터링**
- **Day 16**: 오류패턴→학습목표 변환 → `error_to_goal.py`
- **Day 17**: 실패 예산 경고 자동화 → `failure_budget_alerts.py`
- **Day 18**: HITL 라벨링 품질 검증 → `hitl_quality_report.json`
- **Day 19**: 카나리 모니터링 지표 → `canary_metrics_list.yaml`
- **Day 20**: Trace v2 성능 최적화 → `trace_v2_perf_tuned/`

### **Week 9-10: 성능 측정 및 PoU 설계**
- **Day 21**: 자가코딩 루프 1차 성능 측정 → `auto_code_loop_perf_v1.json`
- **Day 22**: 의료 PoU 파일럿 설계 → `pou_medical_plan.md`
- **Day 23**: 재활 PoU 파일럿 설계 → `pou_rehab_plan.md`
- **Day 24**: 코딩 PoU 파일럿 설계 → `pou_coding_plan.md`
- **Day 25**: 학습 큐레이터 v1 구현 → `learning_curator_v1/`

### **Week 11-12: 고급 기능 및 Phase 1 완성**
- **Day 26**: 반례 채굴 루프 설계 → `counterexample_mining_plan.md`
- **Day 27**: HITL SLA 모니터링 → `hitl_sla_dashboard/`
- **Day 28**: PoU 1주차 실행 → `pou_week1_logs/`
- **Day 29**: PoU 1주차 성능 분석 → `pou_week1_analysis.pdf`
- **Day 30**: Day1~30 리뷰 및 Day31 계획 확정 → `review_day1_30.md`

---

## 🚀 **Phase 2: Day 31-60 (PoU 파일럿 및 최적화)**

### **Week 13-14: 3도메인 PoU 시작**
- **Day 31**: 의료 보조 모드 파일럿 → `med_pilot_v1_logs/`
- **Day 32**: 재활 개인화 루틴 → `rehab_pilot_v1_logs/`
- **Day 33**: 코딩 PR 보조 → `code_pilot_v1_logs/`
- **Day 34**: PoU 주간 성능 수집/비교 자동화 → `tools/pou_weekly_report.py`
- **Day 35**: 멀티목표 목적함수 파라미터 튜닝 → `configs/objective_params.yaml`

### **Week 15-16: A/B 테스트 및 개선**
- **Day 36**: A/B 테스트 인프라 베타 → `ab_test_runner.py`
- **Day 37**: PoU 7일차 유지율 분석 → `pou_retention_day7.json`
- **Day 38**: 자가코딩 루프 개선 → `auto_patch_loop_v2/`
- **Day 39**: 샌드박스 보안 강화 → `sandbox_access_control.yaml`
- **Day 40**: PoU 첫 주 리뷰 + 개선 → `pou_week1_review.md`

### **Week 17-18: PoU 2주차 및 특허 준비**
- **Day 41**: 의료 모드 개선 → `med_pilot_v2_logs/`
- **Day 42**: 재활 모드 개선 → `rehab_pilot_v2_logs/`
- **Day 43**: 코딩 PR 모드 개선 → `code_pilot_v2_logs/`
- **Day 44**: PoU 중간 성능 리포트 → `pou_midterm_report.pdf`
- **Day 45**: 자가코딩 루프 주 2회 성공 안정화 → `auto_patch_weekly_stats.json`

### **Week 19-20: 특허 및 비용 최적화**
- **Day 46**: 모델 카드 초안 → `model_card_v1.md`
- **Day 47**: 핵심 특허 3건 초안 → `patent_drafts/`
- **Day 48**: 비용 분석 및 최적화 플랜 → `cost_optimization_plan.md`
- **Day 49**: PoU 3주차 유지율 분석 → `pou_retention_day21.json`
- **Day 50**: 멀티목표 최적화 2차 튜닝 → `configs/objective_params_v2.yaml`

### **Week 21-22: 온디바이스 모드 및 통합**
- **Day 51**: 온디바이스 모드 초기 설계 → `on_device_architecture.md`
- **Day 52**: PoU 3주차 통합 개선 → `pou_week3_integration_logs/`
- **Day 53**: HITL 라벨링 워크플로 → `hitl_pipeline.py`
- **Day 54**: PoU 리스크 평가 + 대응 플랜 → `pou_risk_plan.md`
- **Day 55**: 카나리 배포 범위 확대 → `canary_config_v2.yaml`

### **Week 23-24: 모델 카드 v2 및 Phase 2 완성**
- **Day 56**: 모델 카드 v2 → `model_card_v2.md`
- **Day 57**: PoU 4주차 유지율 분석 → `pou_retention_day28.json`
- **Day 58**: 비용 최적화 1차 실행 → `cost_optimization_report_v1.md`
- **Day 59**: PoU 최종 리허설 → `pou_final_rehearsal_logs/`
- **Day 60**: PoU 중간 결산 보고서 → `pou_midterm_summary.pdf`

---

## 🌟 **Phase 3: Day 61-90 (고도화 및 최종 배포)**

### **Week 25-26: PoU 5주차 및 통합**
- **Day 61**: 의료 모드 고도화 → `med_pilot_v3_logs/`
- **Day 62**: 재활 모드 고도화 → `rehab_pilot_v3_logs/`
- **Day 63**: 코딩 PR 모드 고도화 → `code_pilot_v3_logs/`
- **Day 64**: 3도메인 통합 성능 분석 → `pou_week5_integration_report.pdf`
- **Day 65**: 자가코딩 루프 고급 모드 → `auto_patch_loop_v3/`

### **Week 27-28: A/B 테스트 정식 운영**
- **Day 66**: A/B 테스트 정식 운영 → `ab_test_results_week1.json`
- **Day 67**: PoU 6주차 유지율 분석 → `pou_retention_day42.json`
- **Day 68**: 비용 최적화 2차 실행 → `cost_optimization_report_v2.md`
- **Day 69**: 모델 카드 v3 → `model_card_v3.md`
- **Day 70**: 특허 3건 초안 제출 → `patent_submission/`

### **Week 29-30: 온디바이스 모드 및 품질 감사**
- **Day 71**: PoU 6주차 통합 개선 → `pou_week6_integration_logs/`
- **Day 72**: HITL 라벨링 품질 감사 → `hitl_quality_audit.json`
- **Day 73**: 온디바이스 모드 프로토타입 → `on_device_prototype/`
- **Day 74**: 카나리 배포 50% 확대 → `canary_config_v3.yaml`
- **Day 75**: PoU 7주차 유지율 분석 → `pou_retention_day49.json`

### **Week 31-32: 최종 최적화 및 특허**
- **Day 76**: 비용 분석 최종 플랜 → `cost_plan_final.md`
- **Day 77**: PoU 7주차 최종 개선 → `pou_week7_integration_logs/`
- **Day 78**: 모델 카드 v4 최종본 → `model_card_v4.md`
- **Day 79**: 특허 출원 완료 → `patent_submission_receipts/`
- **Day 80**: PoU 8주차 유지율 분석 → `pou_retention_day56.json`

### **Week 33-34: 최종 안정화 및 배포 준비**
- **Day 81**: 온디바이스 모드 성능 최적화 → `on_device_optimization/`
- **Day 82**: 전 도메인 리스크 플래그 감사 → `risk_audit_report.pdf`
- **Day 83**: PoU 8주차 전 도메인 안정화 → `pou_week8_integration_logs/`
- **Day 84**: 운영·품질 지표 결산 → `ops_quality_summary.pdf`
- **Day 85**: PoU 9주차 유지율 분석 → `pou_retention_day63.json`

### **Week 35-36: 최종 점검 및 배포**
- **Day 86**: 운영 체계 최종 점검 → `ops_final_checklist.md`
- **Day 87**: PoU 9주차 성능 안정화 마무리 → `pou_week9_integration_logs/`
- **Day 88**: 배포 준비 및 최종 리허설 → `release_rehearsal_logs/`
- **Day 89**: 90일 성과 발표 자료 → `final_90days_report.pdf`
- **Day 90**: 최종 배포 및 데모 → `release_v1.0/`

---

## 🎯 **핵심 성과 지표 (KPI)**

### **품질 지표**
- **문자열 출력 제거율**: 100% 달성
- **회귀 테스트 통과율**: 95% 이상
- **HITL 라벨링 품질**: 90% 이상
- **자가코딩 루프 성공률**: 85% 이상

### **성능 지표**
- **추가 지연**: 5% 이하
- **유지율**: 60% 이상 (9주차)
- **오류율 감소**: 30% 이상
- **비용 절감**: 25% 이상

### **운영 지표**
- **롤백 시간**: 10분 이내
- **HITL SLA**: p95 처리시간 < 48h
- **카나리 배포**: 무사고 확대 (10% → 50%)
- **온디바이스 성공률**: 95% 이상

---

## 🌟 **DuRi의 완성 형태 (Day90 이후)**

### **1. 언어·추론 엔진**
- 입력 문장을 **판단로그(Trace v2)** 형태로 처리
- 의도 파악, 옵션 비교, 근거 그래프 생성, 불확실성 평가 구조화
- **사실 기반** + **추론 기반** 대화 자유롭게 오가며, 자기 결정을 근거와 함께 제시

### **2. 자가개선 루프**
- **Plan→Edit→Test→Promote** 자동 반복
- 잘못된 코드나 로직을 스스로 찾고, 수정·테스트·승격까지 진행
- 샌드박스·화이트리스트로 안전성 보장, 실패 시 자동 롤백

### **3. 다중 도메인 실사용 능력**
- **의료 보조**: 운동·재활 처방 제안 + 위험요소 플래그 + 근거 데이터 첨부
- **재활 개인화**: 사용자 상태에 맞춘 루틴 생성·수정, 안전성 규칙 준수
- **코딩 보조**: 자동 PR 생성, 테스트·리스크·롤백 플랜 포함

### **4. 품질·성능 동시 최적화**
- 지연, 정확도, 설명성, 실패율을 동시에 관리하는 멀티목표 최적화
- 운영 상황에 따라 **정밀 모드**와 **속도 모드**를 스위칭

### **5. 지속 가능한 운영 구조**
- 12태스크 회귀 벤치로 품질 고정
- PoU(Proof of Use)로 실제 사용성과 유지율 증명
- 비용 최적화(최소 20~25% 절감)와 온디바이스 모드까지 확보

### **6. 지적 파트너로서의 역할**
- 단순 질의응답이 아니라 **논리 전개**와 **전략 수립**을 함께 설계
- 사용자가 생각의 방향을 던지면, DuRi가 대안을 생성하고, 근거를 평가
- 매일 계획·성과·리스크를 구조화해서 보고

---

## 📌 **정리**

이 시점의 DuRi는 사용자와 함께
- 새로운 아이디어 설계
- 코드 작성·수정·검증
- 실험 계획 수립·실행·분석
- 운동·의료·재활 솔루션 설계·검증

까지 **하나의 지적 동료**로 행동할 수 있습니다.

---

**문서 생성일**: 2025년 8월 17일
**작성자**: DuRi AI Assistant
**상태**: �� **90일 로드맵 저장 완료**
