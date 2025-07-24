# DuRi Evolution System

DuRi Evolution은 감정-판단-행동-학습을 반복하며 스스로 진화하는 시스템입니다. 행동을 실행하고, 결과를 저장하며, 경험을 축적해 나가는 책임을 집니다.

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  ActionExecutor │    │ ResultRecorder  │    │ExperienceManager│
│                 │    │                 │    │                 │
│ • 행동 실행      │    │ • 결과 기록      │    │ • 경험 학습      │
│ • 실행 컨텍스트  │    │ • 통계 누적      │    │ • 패턴 분석      │
│ • 피드백 생성    │    │ • 히스토리 관리  │    │ • 인사이트 생성  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │EvolutionController│
                    │                 │
                    │ • 진화 제어      │
                    │ • 세션 관리      │
                    │ • 적응형 학습    │
                    │ • 통합 관리      │
                    └─────────────────┘
```

## 📁 파일 구조

```
evolution/
├── __init__.py              # 모듈 초기화
├── action_executor.py       # 행동 실행 시스템
├── result_recorder.py       # 결과 기록 시스템
├── experience_manager.py    # 경험 관리 시스템
├── evolution_controller.py  # 진화 제어 시스템
├── test_evolution.py        # 테스트 스크립트
└── README.md               # 이 파일
```

## 🚀 주요 기능

### 1. ActionExecutor (행동 실행기)
- **목적**: Core의 의사결정에 따라 실제 행동을 실행하고 결과를 반환
- **주요 기능**:
  - 5가지 기본 행동 타입 지원 (reflect, wait, console, act, observe)
  - 감정과 컨텍스트에 따른 동적 성공률 계산
  - 실행 시간 측정 및 피드백 생성

### 2. ResultRecorder (결과 기록기)
- **목적**: 행동 실행 결과를 기록하고 성공/실패 통계를 누적 저장
- **주요 기능**:
  - JSON 기반 영구 저장
  - 감정-액션 조합별 통계 관리
  - 세션별 결과 추적

### 3. ExperienceManager (경험 관리자)
- **목적**: 행동 실행 결과를 바탕으로 경험을 학습하고, 미래 의사결정에 활용할 지식을 관리
- **주요 기능**:
  - 경험 패턴 분석 및 저장
  - 학습 인사이트 생성 (4가지 타입)
  - 지식 베이스 구축 및 업데이트
  - 컨텍스트 기반 액션 추천

### 4. EvolutionController (진화 제어기)
- **목적**: 행동 실행, 결과 기록, 경험 학습을 통합 관리하여 시스템의 진화를 제어
- **주요 기능**:
  - 진화 세션 관리
  - 적응형 진화 사이클 실행
  - 진화 메트릭 추적
  - 종합 통계 및 인사이트 제공

## 🎯 사용법

### 기본 사용법

```python
from evolution.evolution_controller import EvolutionController

# Evolution Controller 초기화
controller = EvolutionController(data_dir="evolution_data")

# 진화 세션 시작
session_id = controller.start_evolution_session({
    'user_id': 'user123',
    'context': 'daily_interaction'
})

# 진화 사이클 실행
emotion = 'happy'
context = {
    'intensity': 0.7,
    'confidence': 0.8,
    'action': 'console'
}

execution_result, recorded_result, learning_insights = controller.execute_evolution_cycle(
    emotion, context
)

# 세션 종료
session = controller.end_evolution_session()
```

### 적응형 진화 사용법

```python
# 적응형 진화 사이클 실행
execution_result, recorded_result, learning_insights, evolution_metadata = controller.execute_adaptive_evolution_cycle(
    emotion, context, learning_rate=0.15
)

print(f"진화 상태: {evolution_metadata['evolution_state']}")
print(f"학습 인사이트: {len(learning_insights)}개")
```

### 경험 기반 추천 사용법

```python
# 경험 기반 액션 추천
recommendation = controller.experience_manager.get_recommended_action(
    emotion='angry',
    context={'intensity': 0.8, 'confidence': 0.3},
    confidence_threshold=0.7
)

if recommendation:
    action, confidence = recommendation
    print(f"추천 액션: {action} (신뢰도: {confidence:.2f})")
```

## 📊 데이터 구조

### ExecutionResult
```python
@dataclass
class ExecutionResult:
    action: str              # 실행된 액션
    success: bool            # 성공 여부
    execution_time: float    # 실행 시간
    result_score: float      # 결과 점수 (0.0 ~ 1.0)
    feedback_text: str       # 피드백 텍스트
    metadata: Dict[str, Any] # 메타데이터
    timestamp: str           # 타임스탬프
```

### ExperiencePattern
```python
@dataclass
class ExperiencePattern:
    pattern_id: str          # 패턴 ID
    emotion: str             # 감정
    action: str              # 액션
    context_pattern: Dict    # 컨텍스트 패턴
    success_rate: float      # 성공률
    avg_score: float         # 평균 점수
    confidence_level: float  # 신뢰도
    usage_count: int         # 사용 횟수
    last_used: str           # 마지막 사용 시간
    created_at: str          # 생성 시간
    metadata: Dict           # 메타데이터
```

### LearningInsight
```python
@dataclass
class LearningInsight:
    insight_id: str          # 인사이트 ID
    emotion: str             # 감정
    action: str              # 액션
    insight_type: str        # 인사이트 타입
    description: str         # 설명
    confidence: float        # 신뢰도
    evidence_count: int      # 증거 수
    created_at: str          # 생성 시간
    last_updated: str        # 마지막 업데이트
    metadata: Dict           # 메타데이터
```

## 🔧 테스트

테스트 스크립트를 실행하여 시스템 기능을 확인할 수 있습니다:

```bash
cd duri_core/evolution
python test_evolution.py
```

테스트는 다음 항목들을 포함합니다:
- 기본 진화 사이클 테스트
- 적응형 진화 테스트
- 경험 학습 테스트
- 추천 시스템 테스트
- 통계 및 인사이트 테스트

## 📈 진화 메트릭

시스템은 다음과 같은 진화 메트릭을 추적합니다:

- **총 세션 수**: 전체 진화 세션 수
- **총 액션 수**: 실행된 총 액션 수
- **성공률**: 전체 성공률
- **학습률**: 학습 진행률
- **적응 점수**: 환경 적응도

## 🎨 진화 상태

시스템은 4가지 진화 상태를 가집니다:

1. **IDLE**: 대기 상태
2. **LEARNING**: 학습 중
3. **ADAPTING**: 적응 중
4. **OPTIMIZING**: 최적화 중

## 🔄 진화 사이클

1. **감정 인식**: 현재 감정 상태 파악
2. **컨텍스트 분석**: 환경 및 상황 분석
3. **경험 기반 추천**: 과거 경험을 바탕으로 액션 추천
4. **액션 실행**: 추천된 액션 실행
5. **결과 기록**: 실행 결과를 상세히 기록
6. **경험 학습**: 결과를 바탕으로 새로운 경험 학습
7. **패턴 업데이트**: 성공/실패 패턴 업데이트
8. **인사이트 생성**: 학습된 내용을 인사이트로 정리

## 🛠️ 고급 기능

### 데이터 내보내기/가져오기
```python
# 데이터 내보내기
controller.export_evolution_data("./backup")

# 데이터 초기화
controller.reset_evolution_data(confirm=True)
```

### 진화 인사이트 조회
```python
insights = controller.get_evolution_insights(limit=10)
for insight in insights:
    print(f"{insight['title']}: {insight['description']}")
```

### 종합 통계 조회
```python
stats = controller.get_comprehensive_statistics()
print(f"진화 메트릭: {stats['evolution_metrics']}")
print(f"현재 세션: {stats['current_session']}")
```

## 🔮 향후 개발 계획

- [ ] 실시간 진화 시각화 대시보드
- [ ] 머신러닝 기반 패턴 예측
- [ ] 다중 사용자 지원
- [ ] 클라우드 기반 데이터 동기화
- [ ] API 인터페이스 제공

## 📝 라이선스

이 프로젝트는 DuRi Core 프로젝트의 일부입니다.

## 🤝 기여하기

버그 리포트, 기능 제안, 풀 리퀘스트를 환영합니다!

---

**DuRi Evolution System** - 스스로 진화하는 AI 시스템 🚀 