# 24시간 검증 체크리스트

## 🎯 목표
Day 68 하이브리드 관찰 가능성 시스템 배포 후 24시간 내 안정성 검증

## ✅ 체크리스트

### **1. Alertmanager 상태 확인**
- [ ] `curl -s http://localhost:9093/-/ready` → **200 OK**
- [ ] `curl -s http://localhost:9093/api/v1/status` → 정상 응답
- [ ] 설정 파일 로드 확인: `alertmanager.yml` 문법 오류 없음

### **2. Prometheus 룰 로드 확인**
- [ ] `curl -s http://localhost:9090/api/v1/rules` → 룰 그룹 정상 로드
- [ ] `quality-recordings`, `quality-slo`, `quality-alerts` 그룹 확인
- [ ] 총 22개 룰 정상 로드 (recording: 10, slo: 6, alerts: 6)

### **3. 경보 발생 현황**
- [ ] 경보 건수/팀별 분포: 경고 ≤ 페이지
- [ ] Critical 알림: 월간 ≤ 0.8회 목표
- [ ] False Positive Rate: < 5% 목표
- [ ] 평균 응답 시간: Critical < 5분

### **4. 성능 지표 수렴**
- [ ] nDCG@3 MA7: 안정적 수렴 확인
- [ ] MRR@3 MA7: 안정적 수렴 확인
- [ ] z-score: 정상 범위 내 (±2)
- [ ] WoW%: 주간 변동성 정상

### **5. DR 리허설 시스템**
- [ ] `systemctl --user list-timers | grep dr-restore` → 활성 상태
- [ ] 수동 리허설 테스트: `systemctl --user start kimshin-dr-restore.service`
- [ ] 로그 확인: `journalctl --user -u kimshin-dr-restore.service -n 100`

### **6. Grafana 대시보드**
- [ ] Day68 Quality Overview 대시보드 정상 표시
- [ ] MA7, z-score, ErrBudget 메트릭 정상 표시
- [ ] 임계값 설정 정상 (녹색: 정상, 빨간색: 0.9 이하)

### **7. 백업 시스템**
- [ ] 룰 백업 파일 생성: `rules_*.tar.gz`
- [ ] SHA256 체크섬 검증: `*.sha256` 파일
- [ ] 복구 테스트: `./scripts/rules_backup_restore.sh restore <archive>`

## 🚨 문제 발생 시 대응

### **알람 과다 발생**
1. z-score 임계값 조정: `-2` → `-2.2`
2. WoW% 임계값 조정: `-5%` → `-6%`
3. SLO breach 지속시간 조정: `30m` → `45m`

### **알람 미발생**
1. 임계값 완화: z-score `-2` → `-1.8`
2. 지속시간 단축: `30m` → `15m`
3. WoW% 임계값 완화: `-5%` → `-4%`

### **성능 지표 이상**
1. MA7 수렴 지연: 데이터 품질 확인
2. z-score 이상: 표준편차 계산 검증
3. ErrBudget 계산 오류: SLO 목표값 재검토

## 📊 성공 지표

### **정확도**
- True Positive Rate: > 95%
- False Positive Rate: < 5%
- F1-balanced: > 90%

### **운영**
- 월간 알람 수: ≤ 0.8회
- 평균 응답 시간: Critical < 5분
- 시스템 가용성: > 99.9%

### **성능**
- nDCG@3: ≥ 0.90
- MRR@3: ≥ 0.88
- Recall@3: ≥ 0.98

## 🔄 24시간 후 다음 단계

### **Day 69 준비**
- [ ] 소음 튜닝 결과 분석
- [ ] Alert 라우팅 고도화 계획
- [ ] 사후리포트 템플릿 자동화
- [ ] Burn rate 알람 구현
- [ ] Synthetic probe 시스템 구축

### **장기 개선**
- [ ] 서비스/도메인별 서브라우트
- [ ] 근무시간/야간 라우팅
- [ ] Alert → JIRA/MD 템플릿 생성
- [ ] Multi-window burn rate 알람
- [ ] 스토리형 쿼리 세트 50개 고정

## 📋 실행 명령어

```bash
# 1. Alertmanager 상태 확인
curl -s http://localhost:9093/-/ready

# 2. Prometheus 룰 확인
curl -s http://localhost:9090/api/v1/rules | jq '.data.groups[].name'

# 3. DR 타이머 상태
systemctl --user list-timers | grep dr-restore

# 4. 수동 DR 리허설
systemctl --user start kimshin-dr-restore.service

# 5. 로그 확인
journalctl --user -u kimshin-dr-restore.service -n 100 --no-pager

# 6. 룰 백업 확인
ls -la rules_*.tar.gz

# 7. Grafana 대시보드 확인
# 브라우저에서 http://localhost:3000 접속
# Day68 Quality Overview 대시보드 확인
```

## ✅ 완료 기준

- [ ] 모든 체크리스트 항목 완료
- [ ] 24시간 내 안정성 검증 완료
- [ ] 성공 지표 달성
- [ ] Day 69 준비 완료


