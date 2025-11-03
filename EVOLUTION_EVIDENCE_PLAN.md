# DuRi 자가 진화 증거 수집 계획

**작성일**: 2025-10-31  
**목적**: 기존 코드를 활용하여 자가 진화 증거를 자동으로 수집

---

## 📋 현재 상태 분석

### ✅ 이미 존재하는 구성 요소

1. **Evidence 파이프라인**
   - `scripts/evolution/evidence_bundle.sh`: EV 번들 생성
   - `scripts/evolution/evidence_score.sh`: EV 점수 계산
   - Systemd 타이머: `duri-evidence.timer` (1시간마다 실행)

2. **Shadow 훈련장 시스템**
   - `scripts/shadow_duri_integration_final.sh`: Shadow 메인 루프
   - `scripts/lib/transport.sh`: 하이브리드 전송 시스템
   - 메트릭 수집: `shadow/metrics_exporter_enhanced.py`

3. **자가 진화 시스템 코드**
   - `duri_modules/self_awareness/integrated_self_evolution_system.py`
   - `duri_modules/self_awareness/self_evolution_tracker.py`
   - `DuRiCore/modules/evolution/self_evolution_manager.py`

4. **메트릭**
   - AB 테스트 p-value (`duri_ab_p_value`)
   - Transport 메트릭 (`duri_shadow_transport_total`)
   - SSH 성공/실패 (`duri_shadow_ssh_failures_total`)

### ⚠️ 현재 누락된 연결

1. **Shadow → Evidence 자동 연결**
   - Shadow 훈련 완료 후 EV 번들 자동 생성 안 됨
   - 자가 진화 시스템 호출 안 됨

2. **진화 지표 통합**
   - Shadow 메트릭과 자가 진화 시스템 연결 안 됨
   - 진화 점수가 EV 번들에 기록 안 됨

---

## 🎯 진화 증거 수집 계획

### 1단계: Shadow 훈련 완료 시 EV 번들 자동 생성

**목표**: Shadow 훈련이 완료되면 자동으로 EV 번들 생성

**방법**:
- `scripts/shadow_duri_integration_final.sh`의 `main_training_loop()` 끝에
- `scripts/evolution/evidence_bundle.sh` 호출 추가
- Shadow 훈련 메트릭을 EV 번들에 포함

### 2단계: 자가 진화 시스템 호출 및 결과 기록

**목표**: Shadow 훈련 데이터를 자가 진화 시스템에 전달하여 진화 지표 계산

**방법**:
- `duri_modules/self_awareness/integrated_self_evolution_system.py` 호출
- 진화 지표를 EV 번들 `summary.txt`에 기록
- 진화 단계, 개선율, 성능 점수 기록

### 3단계: 진화 메트릭 통합

**목표**: Shadow 메트릭 + 자가 진화 메트릭을 통합하여 종합 진화 증거 생성

**방법**:
- AB p-value + Transport 성공률 + 진화 점수 통합
- 시간 경과에 따른 진화 추세 분석
- EV 번들에 진화 메트릭 기록

### 4단계: 자동화 강화

**목표**: Systemd 타이머와 Shadow 훈련을 연계하여 완전 자동화

**방법**:
- Shadow 훈련 완료 → EV 번들 생성 → 자가 진화 분석 → 메트릭 통합
- 주기적 진화 보고서 생성 (일/주 단위)

---

## 📊 진화 증거 수집 가능한 데이터

### 현재 수집 가능한 메트릭

1. **Shadow 훈련 메트릭**
   - Transport 성공/실패율 (HTTP vs SSH)
   - SSH 실패율 추이
   - 카나리 확률 변화
   - 훈련 세션 수

2. **AB 테스트 메트릭**
   - p-value (통계적 유의성)
   - 시간 경과에 따른 p-value 변화

3. **자가 진화 시스템 메트릭** (호출 시)
   - 성능 점수 (performance_score)
   - 학습 효율 (learning_efficiency)
   - 자율 수준 (autonomy_level)
   - 문제 해결 능력 (problem_solving_capability)
   - 개선율 (improvement_rate)
   - 진화 단계 (evolution_stage)

4. **EV 번들 메타**
   - ANCHOR.SHA256SUMS (코드베이스 무결성)
   - STATE.SHA256SUMS.snapshot (상태 스냅샷)
   - Transport 방식 (HTTP/SSH/MIXED)
   - 타임스탬프

### 추가로 수집 가능한 메트릭

1. **Shadow 훈련 성능**
   - 평균 응답 시간 (HTTP vs SSH)
   - 에러율
   - 회복 시간

2. **진화 추세**
   - EV 번들별 p-value 변화
   - 진화 점수 추이
   - Transport 방식별 성능 비교

---

## 🔧 구현 계획

### 즉시 구현 가능 (기존 코드 활용)

1. **Shadow 훈련 완료 시 EV 번들 생성**
   ```bash
   # scripts/shadow_duri_integration_final.sh 끝에 추가
   bash scripts/evolution/evidence_bundle.sh
   bash scripts/evolution/evidence_score.sh
   ```

2. **자가 진화 시스템 호출**
   ```bash
   # Shadow 훈련 데이터 수집 후
   python3 -m duri_modules.self_awareness.integrated_self_evolution_system \
     --input var/logs/shadow.log \
     --output var/evolution/LATEST/evolution_metrics.json
   ```

3. **진화 메트릭을 EV 번들에 기록**
   ```bash
   # evolution_metrics.json을 summary.txt에 통합
   ```

### 향후 구현 (보완)

1. **진화 추세 분석 스크립트**
   - 여러 EV 번들의 진화 지표 비교
   - 시간 경과에 따른 진화 추세 그래프 생성

2. **진화 보고서 자동 생성**
   - 일/주 단위 진화 보고서
   - HTML/마크다운 형식

---

## 📈 진화 증거 수집 체크리스트

### 현재 상태

- [x] Evidence 파이프라인 존재
- [x] Shadow 훈련장 완성
- [x] 메트릭 Exporter 작동
- [x] Systemd 타이머 설정
- [ ] Shadow → Evidence 자동 연결
- [ ] 자가 진화 시스템 자동 호출
- [ ] 진화 메트릭 통합 기록

### 다음 단계

1. **즉시 구현** (5분)
   - Shadow 훈련 완료 시 EV 번들 생성 연결

2. **단기 구현** (30분)
   - 자가 진화 시스템 자동 호출
   - 진화 메트릭 기록

3. **중기 구현** (2시간)
   - 진화 추세 분석 스크립트
   - 진화 보고서 자동 생성

---

## 🎯 기대 결과

### 수집되는 진화 증거

1. **시간 경과에 따른 진화**
   - EV 번들 타임스탬프
   - 진화 점수 추이
   - 성능 개선율

2. **통계적 유의성**
   - AB 테스트 p-value
   - 유의한 변화 감지 (p < 0.05)

3. **자율 진화 증거**
   - 자가 진화 시스템의 진화 단계
   - 자율 수준 향상
   - 학습 효율 개선

4. **실전 견고성 증거**
   - Transport 방식별 성능 비교
   - 카오스 주입 회복력
   - 자동 폴백 성공률

---

**결론**: 기존 코드로 충분히 진화 증거 수집 가능. Shadow → Evidence 연결만 추가하면 자동 수집 시작됨.

