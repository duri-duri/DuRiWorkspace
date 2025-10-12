# Day 68 DoD — 운영형 알림·이상감지 + SLO/DR/CI

## 🎯 목표
하이브리드 관찰 가능성 시스템 구현: 통계적 이상감지 + SLO/에러버짓 + CI/DR 리허설

## ✅ 체크리스트

### **Prometheus Rules 검증**
- [x] promtool check rules (prod) PASS
- [x] promtool test rules (test profiles) PASS
- [x] CI PR 게이트에 prom-rules-ci/validate-prom-all 편입

### **통계적 이상감지**
- [x] z-score·WoW% NaN/±Inf 미발생 (clamp_min 반영) NaN/±Inf 미발생 (clamp_min 반영)
- [x] 즉시 급락 알림 (nDCG < 0.80) (nDCG < 0.80)
- [x] WoW 회귀 알림 (주간 대비 >5% 하락) (주간 대비 >5% 하락)
- [x] z-score 이상 알림 (z <= -2) (z <= -2)

### **SLO/에러버짓**
- [x] nDCG@3 SLO breach 알림 (MA7 < 0.90) (MA7 < 0.90)
- [ ] MRR SLO breach 알림 (MA7 < 0.88)
- [ ] DoD 급락 알림 (전일 대비 >3% 하락)

### **운영 안정성**
- [ ] Grafana: nDCG/MRR MA7·z-score·SLO(에러버짓) 보드 배포
- [ ] DR 리허설 타이머 활성 (systemd --user)
- [ ] rules/ 디렉터리 tar+sha256 백업 복구 확인

### **테스트 신뢰성**
- [ ] 운영용 룰 (7d 윈도우) vs 테스트용 룰 (5m 윈도우) 분리
- [ ] 테스트 전용 룰에서 offset 7d → offset 3m 축소
- [ ] NaN/Inf 방지를 위한 clamp_min 적용

## 📊 성공 지표

### **탐지 커버리지**
- 통계적 이상감지: z-score, WoW%, 즉시 급락
- SLO/에러버짓: MA7 기준 임계값 breach
- 운영 안정성: CI 엄격 모드, 월 1회 DR 리허설

### **운영 일관성**
- CI PR 게이트에 prom-rules-ci 통합
- 테스트 신뢰성: flaky 테스트 제거
- 롤백 안전성: rules 백업 및 복구 시스템

## 🚀 실행 명령어

```bash
# Prometheus rules 검증
make prom-rules-ci

# 전체 CI 게이트
make ci-pr-gate

# DR 리허설 타이머 활성화
systemctl --user daemon-reload
systemctl --user enable --now kimshin-dr-restore.timer
systemctl --user list-timers | grep dr-restore
```

## 📋 완료 기준

- [ ] 모든 체크리스트 항목 완료
- [ ] CI PR 게이트 통과
- [ ] DR 리허설 타이머 정상 작동
- [ ] Grafana 대시보드 배포 완료
- [ ] 백업 및 복구 시스템 검증 완료
