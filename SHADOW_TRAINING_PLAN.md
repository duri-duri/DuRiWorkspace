# Shadow 훈련장 완성 계획

## 현재 상태 분석

### ✅ 완료된 것
1. **Docker 17개 노드**: 모두 Healthy
2. **Shadow SSH 노드**: `~/DuRiShadow/{duri_core, duri_brain, duri_evolution, duri_control}` ✅
3. **서비스 간 통신**: Core → Brain (200), Core → Evolution (200), Core → Control (200) ✅
4. **Shadow 스크립트**: 기본 훈련 + 약점 분석 추가 ✅

### 📊 노드별 실제 모듈 구조

#### duri_core (철학/기억/정체성)
- `emotion_summary.py`, `summary_loader.py`, `summary_reporter.py`
- `logic.py`, `reflexion_file.py`
- 역할: 감정 처리, 요약, 로직 실행

#### duri_brain (학습/평가/창의성)
- `decide_action.py`, `receive_decision_input.py`
- `emotion.py`, `generate_emotion_vector.py`
- 역할: 의사결정, 감정 벡터 생성

#### duri_evolution (진화/강화학습)
- `receive_experience.py`, `api_skills.py`
- `log_emotion_change.py`
- 역할: 경험 수집, 진화 학습

#### duri_control (외부 제어)
- `user_model.py`, `gateway_model.py`
- `monitor.py`, `notify_model.py`
- 역할: 모니터링, 알림, 게이트웨이

### 🔄 상호 관계

```
Core (철학/기억/정체성)
  ↓ 감정 처리
Brain (학습/평가/창의성)
  ↓ 의사결정
Evolution (진화/강화학습)
  ↓ 경험 수집
Control (모니터링/알림)
```

## 누락 기능 및 보완 계획

### 1. 자가 진화 분석 추가
- **목표**: Shadow에서 DuRi의 자가 진화 능력 활성화
- **방법**: `integrated_self_evolution_system.py` 래퍼 작성
- **위치**: Shadow 스크립트에 안전 호출 추가

### 2. 코딩 시뮬레이션 추가
- **목표**: Shadow 코드 품질 검증
- **방법**: `shadow_parallel_validator.sh` 작성 또는 기존 검증 활용
- **위치**: Shadow 스크립트에 검증 단계 추가

### 3. Shadow → Legacy 프로모션 자동화
- **목표**: Shadow 성과를 Legacy로 안전하게 전파
- **방법**: `promote_shadow_to_legacy.sh` 활용
- **위치**: Shadow 스크립트에 프로모션 단계 추가

## 다음 단계

1. ✅ Shadow 훈련장 현재 상태 확인
2. ✅ 노드 간 상호 관계 파악
3. 🔄 자가 진화 분석 래퍼 작성
4. 🔄 코딩 시뮬레이션 검증 추가
5. 🔄 프로모션 자동화 구현

## 실행 계획

### 단계별 진행
- **1단계**: 자가 진화 분석 추가 (30분)
- **2단계**: 코딩 시뮬레이션 추가 (30분)
- **3단계**: 프로모션 자동화 구현 (30분)
- **4단계**: 전체 테스트 및 검증 (30분)

### 안전장치
- ✅ 기존 코드 덮어쓰기 금지
- ✅ 필요한 부분만 추가
- ✅ 실패 시 스킵으로 루프 보호
- ✅ 상호 관계 확인 후 구현
