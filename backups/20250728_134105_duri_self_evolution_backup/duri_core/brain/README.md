# DuRi Brain - 감정-판단-반응 루프 관리 시스템

DuRi Brain은 감정 입력의 발생 시점과 내용을 기록하고, Core가 내린 판단 이후 외부 반응(결과, 피드백)을 수집하여 다시 Core에게 전달하는 역할을 담당합니다.

## 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Emotion       │    │   Core          │    │   External      │
│   Input         │───▶│   Decision      │───▶│   Feedback      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DuRi Brain                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ Emotion     │  │ Loop        │  │ Feedback    │            │
│  │ Recorder    │  │ Manager     │  │ Collector   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                Brain Controller                             │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 주요 컴포넌트

### 1. EmotionRecorder
감정 입력의 발생 시점과 내용을 기록합니다.

**주요 기능:**
- 감정 입력 기록 (`record_emotion_input`)
- 의사결정 기록 (`record_decision`)
- 감정 히스토리 조회 (`get_emotion_history`)
- 의사결정 히스토리 조회 (`get_decision_history`)

**데이터 구조:**
```python
@dataclass
class EmotionInput:
    emotion: str
    intensity: float
    timestamp: str
    context: Optional[Dict[str, Any]] = None
    source: Optional[str] = None
    session_id: Optional[str] = None
```

### 2. FeedbackCollector
외부 반응(결과, 피드백)을 수집합니다.

**주요 기능:**
- 외부 피드백 수집 (`collect_feedback`)
- 자동 피드백 생성 (`collect_automatic_feedback`)
- 완전한 루프 결과 생성 (`create_complete_loop`)
- 피드백 히스토리 조회 (`get_feedback_history`)

**데이터 구조:**
```python
@dataclass
class ExternalFeedback:
    loop_id: str
    feedback_type: FeedbackType
    feedback_score: float
    feedback_text: Optional[str] = None
    timestamp: Optional[str] = None
    source: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
```

### 3. LoopManager
감정-판단-반응 루프를 관리하고 Core에게 학습 데이터를 제공합니다.

**주요 기능:**
- 완전한 루프 처리 (`process_emotion_loop`)
- 학습 데이터 조회 (`get_learning_data`)
- 감정-액션 통계 조회 (`get_emotion_action_statistics`)
- 성능 인사이트 조회 (`get_performance_insights`)

### 4. BrainController
Brain 시스템의 전체적인 제어를 담당합니다.

**주요 기능:**
- 세션 관리 (`start_session`, `end_session`)
- 감정 처리 (`process_emotion`)
- 외부 피드백 수집 (`collect_external_feedback`)
- 시스템 통계 조회 (`get_system_overview`)
- 학습 데이터 내보내기 (`export_learning_data`)

## 사용 예제

### 기본 사용법

```python
from brain import BrainController, BrainConfig

# Brain 시스템 초기화
config = BrainConfig(
    data_dir="brain_data",
    auto_feedback=True,
    enable_learning=True
)
brain = BrainController(config)

# 세션 시작
session_id = "my_session"
brain.start_session(session_id, user_id="user123")

# 감정 처리 (완전한 루프)
emotion_input, decision, feedback, loop_result = brain.process_emotion(
    emotion="happy",
    intensity=0.8,
    session_id=session_id,
    context={"description": "긍정적인 상황"}
)

# 세션 종료
brain.end_session(session_id)
```

### 외부 피드백 수집

```python
# 외부 시스템에서 피드백 수집
external_feedback = brain.collect_external_feedback(
    loop_id="loop_happy_20231201_143022",
    feedback_type="success",
    feedback_score=0.85,
    feedback_text="사용자가 만족함",
    source="user_interface"
)
```

### 학습 데이터 활용

```python
# Core 학습용 데이터 조회
learning_data = brain.loop_manager.get_learning_data(
    emotion="happy",
    min_success_rate=0.7,
    limit=100
)

# 성능 인사이트 조회
insights = brain.loop_manager.get_performance_insights()
print(f"평균 성공률: {insights['overall']['avg_success_rate']:.2f}")

# 학습 데이터 내보내기
brain.export_learning_data("training_data.json")
```

## 데이터 구조

### 감정-판단-반응 루프

```
EmotionInput → Decision → ExternalFeedback → LoopResult
     ↓            ↓            ↓                ↓
  감정 입력    Core 의사결정   외부 피드백    완전한 루프
```

### 저장되는 데이터

- **감정 입력**: `brain_data/emotions/`
- **의사결정**: `brain_data/decisions/`
- **피드백**: `brain_data/feedback/`
- **루프 결과**: `brain_data/loops/`
- **세션 정보**: `brain_data/sessions/`
- **백업**: `brain_data/backups/`

## 설정 옵션

```python
@dataclass
class BrainConfig:
    data_dir: str = "brain_data"           # 데이터 저장 디렉토리
    auto_feedback: bool = True             # 자동 피드백 생성 여부
    enable_learning: bool = True           # 학습 기능 활성화 여부
    max_loops_per_session: int = 1000     # 세션당 최대 루프 수
    backup_interval: int = 100             # 백업 간격 (루프 수)
```

## 피드백 타입

```python
class FeedbackType(Enum):
    SUCCESS = "success"    # 성공
    FAILURE = "failure"    # 실패
    PARTIAL = "partial"    # 부분적 성공
    NEUTRAL = "neutral"    # 중립
    UNKNOWN = "unknown"    # 알 수 없음
```

## 통계 및 분석

### 세션 통계
- 총 루프 수
- 평균 성공률
- 감정 분포
- 액션 분포

### 성능 인사이트
- 전체 평균 성공률
- 감정별 성능
- 액션별 성능
- 루프 지속시간 분석

### 학습 데이터
- 감정-액션 조합별 성공률
- 신뢰도 분석
- 피드백 점수 분포

## 백업 및 복구

```python
# 시스템 백업
brain.backup_system("backup_directory")

# 오래된 데이터 정리
brain.cleanup_old_data(days_to_keep=30)
```

## 확장 가능성

### 외부 시스템 연동
- 사용자 인터페이스와의 연동
- 다른 AI 시스템과의 연동
- 실시간 피드백 수집

### 고급 분석
- 머신러닝 모델 통합
- 예측 분석
- 패턴 인식

### 실시간 처리
- 스트리밍 데이터 처리
- 실시간 의사결정
- 동적 학습

## 실행 예제

```bash
# Brain 시스템 예제 실행
python examples/brain_example.py
```

이 예제는 감정-판단-반응 루프의 완전한 생명주기를 시연합니다. 