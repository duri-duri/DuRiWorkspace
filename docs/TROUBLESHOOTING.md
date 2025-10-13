# 핵심 회고 (문제 → 원인 → 해법)

## 1. MA7 기대값 불일치

**문제:** `exp 0.894285…` vs `got 0.895` 미스매치.

**원인:** promtool의 샘플 시점/윈도우 경계(평균에 포함되는 포인트 개수)가 테스트 `interval`·`eval_time` 조합과 딱 안 맞았어요.

**해법:** `eval_time`을 창 크기 끝에 정렬하고 기대값을 재계산. 최종적으로 **MA7 계산만 검증**하는 테스트로 분리해 안정화 ✅

## 2. for: 15m 알람 테스트가 발화 안 됨

**문제:** `MRR_SLO_Breach`(for: 15m) 기대 알람이 `got: []`.

**원인:** 임계 하회 구간이 "연속 15m"로 충분히 유지되지 못하거나, MA7이 실제로 SLO 미만으로 내려오지 않은 타이밍에 `eval_time`을 찍음.

**해법(일반 패턴):**
- **충분한 워밍업**(정상값) → **충분한 위반 구간**(for 시간보다 길게) → `eval_time`은 위반 시작 시점 + for + ε.
- 예: `interval: 1m`, `values: '0.90x30 0.86x20'`, `eval_time: 46m` (위반 16분 경과) 처럼 "for 충족 + 1분" 지점에서 확인.

## 3. runbook_url 주입 후 YAML 오류

**문제:** `did not find expected key`(들여쓰기/inline map).

**원인:** `labels: {…}` 한 줄 맵에 `runbook_url`을 별도 줄로 추가하면서 들여쓰기가 깨짐.

**해법:** `labels:`를 블록 맵으로 변환해 정식 들여쓰기 유지. 이후 전 파일 재정렬로 해결 ✅

## 4. 라벨 가드 스크립트

**문제:** awk 버전/예약어(`in`) 차이 + 라벨 범위 오검출.

**해법:** **Python판으로 교체 + `labels:` 블록 한정 + 재귀 스캔**. 파일 끝 마지막 알람까지 평가하도록 flush 로직 추가 ✅

## 5. pre-commit 구성 충돌

**문제:** hook 리포 섞임/중복 문서/없는 훅 선언.

**해법:** `pre-commit-hooks`와 `black/isort/flake8`를 **각 리포 원본으로 분리 선언**. yamllint는 로컬 규칙(.yamllint)로 경고 완화 또는 제거. 최종 전부 PASS ✅

---

# 앞으로의 재발 방지 팁 (짧고 굵게)

## 알람 테스트는 계산과 알람을 분리

1. 녹화(레코딩/집계) 식의 **수치 검증** 테스트
2. 그 결과를 사용한 **알람(for 포함) 검증** 테스트
   → 지금처럼 분리하면 원인 추적이 훨씬 쉬워져요.

## for 테스트의 정석 매크로

```yaml
# 분 단위 예시
# 정상(0.90) 30분 → 위반(0.86) 16분 → eval_time 46m (위반 시작 + 16m)
interval: 1m
values: '0.90x30 0.86x20'
alert_rule_test:
  - eval_time: 46m  # 15m 충족 + 1m
    alertname: YOUR_ALERT
    exp_alerts: [ ... ]
```

## 라벨 가드 정확도 유지

지금처럼 **labels 블록 내부만** 검사하면 annotations/description에 있는 단어와 충돌하지 않습니다.

## 워크플로 길이/진실값 경고

길 수밖에 없는 GitHub Actions YML은 `.yamllint`에서만 완화하거나(지금처럼) 아예 ignore 해두면 잡음이 사라집니다.

---

## 현재 상태

- ✅ 모든 검증 PASS
- ✅ 운영/재현성/가독성 삼박자 완성
- ✅ Phase 3 진입 준비 100% 완료
- 🧊 조용히 잘 도는 레포 모드

## 중복 억제(inhibit) 규칙 가이드

### 현재 설정: Quick_Drop ↔ SLO_Breach 억제

```yaml
# alertmanager/alertmanager.yml
inhibit_rules:
- source_matchers: ['alertname="MRR_SLO_Breach"','team="search"']
  target_matchers: ['alertname="MRR_Quick_Drop"','team="search"']
  equal: ['team']
```

### 의도 및 시나리오

**목적:** SLO 위반 알람이 발생하면 더 세밀한 Quick Drop 알람을 억제하여 알람 소음을 줄임

**시나리오:**
1. MRR이 0.85 이하로 급락 → `MRR_Quick_Drop` 알람 발생
2. 15분 후 MA7이 0.88 이하로 내려감 → `MRR_SLO_Breach` 알람 발생
3. `MRR_SLO_Breach` 발생 시 `MRR_Quick_Drop` 자동 억제

**레이블 매칭 예시:**
```yaml
# 억제되는 Quick_Drop 알람
alertname: MRR_Quick_Drop
team: search
severity: warning

# 억제를 트리거하는 SLO_Breach 알람
alertname: MRR_SLO_Breach
team: search
severity: warning
```

### 주의사항

- `equal: ['team']`로 인해 동일한 팀의 알람만 억제됨
- 다른 팀의 Quick_Drop 알람은 영향받지 않음
- `severity`나 `service` 라벨은 매칭 조건에 포함되지 않음

### 확장 예제

```yaml
# 여러 알람 간 억제
inhibit_rules:
- source_matchers: ['alertname="CriticalServiceDown"']
  target_matchers: ['alertname="HighErrorRate"']
  equal: ['service', 'team']
- source_matchers: ['severity="critical"']
  target_matchers: ['severity="warning"']
  equal: ['service']
```

## 억제(inhibit) E2E 리허설 가이드

### 관측된 라우팅/억제 스크린샷 첨부 체크리스트

**PR 생성 시 필수 확인 사항:**

1. **Alertmanager UI 스크린샷**
   - [ ] 활성 알람 목록에서 `MRR_Quick_Drop` 알람 발생
   - [ ] `MRR_SLO_Breach` 알람 발생 시 `MRR_Quick_Drop` 자동 억제 확인
   - [ ] 억제된 알람이 "Inhibited" 상태로 표시되는지 확인

2. **라우팅 규칙 동작 스크린샷**
   - [ ] `team="search"` 알람이 `search-slack` 리시버로 라우팅
   - [ ] `severity="critical"` 알람이 적절한 리시버로 라우팅
   - [ ] `group_by: ['alertname','team']` 그룹핑이 올바르게 작동

3. **Slack/이메일 알림 수신 스크린샷**
   - [ ] 실제 알림 수신 확인
   - [ ] 알림 내용에 `runbook_url` 링크 포함 확인
   - [ ] 알림 그룹핑이 올바르게 작동하는지 확인

### 리허설 시나리오

**시나리오 1: Quick_Drop → SLO_Breach 억제**
1. `duri_mrr_at_k` 값을 0.85 이하로 설정
2. 15분 후 `MRR_Quick_Drop` 알람 발생 확인
3. `duri_mrr_at_k` 값을 0.86으로 설정하여 MA7이 0.88 이하로 내려가도록 함
4. `MRR_SLO_Breach` 알람 발생 시 `MRR_Quick_Drop` 억제 확인

**시나리오 2: 라우팅 규칙 검증**
1. `severity="critical"` 알람 생성
2. `team="search"` 알람 생성
3. 각각 올바른 리시버로 라우팅되는지 확인

### 문제 해결

**억제가 작동하지 않는 경우:**
- `equal: ['team']` 조건 확인
- 알람 라벨이 정확히 매칭되는지 확인
- Alertmanager 로그에서 억제 규칙 적용 여부 확인

**라우팅이 작동하지 않는 경우:**
- `matchers` 조건 확인
- 리시버 설정 확인
- Alertmanager 설정 리로드 확인
