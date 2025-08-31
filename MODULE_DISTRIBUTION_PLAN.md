# DuRi 노드별 모듈 분산 계획 (보완안)
ChatGPT 제안 기반 모듈 구조화 및 노드별 최적 배치 + 성장 기반 AI 특성 반영

## 🎯 **노드별 역할 및 모듈 배치**

### **duri_core_node (센서, 반응, 상태 관리)**
```
duri_core_node/
├── stimulus_listener.py        # 자극 감지 및 수신
├── reaction_dispatcher.py      # 반응 분배 및 전송
├── state_manager.py           # 전체 상태 관리
├── performance_optimizer.py    # 성능 최적화 (기존)
├── load_balancer.py           # 로드 밸런싱 (기존)
└── api_gateway.py             # API 게이트웨이
```

### **duri_brain (고차원 사고, 감정, 판단, 성장)**
```
duri_brain/
├── emotion/                    # 감정 시스템
│   ├── emotion_filter.py       # 고도화된 감정 필터 (이관)
│   ├── emotion_analyzer.py     # 감정 분석기 (이관)
│   ├── emotion_intelligence.py # 감정 지능 서비스 (이관)
│   ├── emotion_logger.py       # 감정 히스토리 관리 (신규)
│   ├── emotion_regulator.py    # 감정 조절 시스템 (신규)
│   └── judgment_bridge.py      # 감정-판단 연결 브리지 (신규)
├── growth/                     # 성장 시스템
│   ├── growth_manager.py       # 성장 레벨 관리 (이관)
│   ├── growth_stages.py        # 성장 단계 관리 (이관)
│   ├── level_conditions.py     # 레벨업 조건 관리 (신규)
│   ├── development_tracker.py  # 발달 추적 시스템 (신규)
│   ├── growth_quests.py        # 퀘스트 조건 관리 및 수행 체크 (신규)
│   └── emotion_relay.py        # 성장-감정 연결 추적 (신규)
├── judgment/                   # 판단 시스템
│   ├── judgment_trace.py       # 판단 추적 (신규)
│   ├── bias_detector.py        # 편향 탐지기 (이관)
│   ├── judgment_consciousness.py # 판단 자각 (이관)
│   ├── decision_framework.py   # 의사결정 프레임워크 (신규)
│   └── growth_feedback.py      # 판단-성장 피드백 (신규)
├── memory/                     # 기억 시스템
│   ├── memory_sync.py          # 메모리 동기화 (이관)
│   ├── experience_store.py     # 경험 저장소 (신규)
│   ├── knowledge_base.py       # 지식 베이스 (신규)
│   ├── growth_feedback_logger.py # 퀘스트 성공/실패 이력 저장 (신규)
│   └── replay_interface.py     # 퀘스트 회상 기능 (신규)
├── meta/                       # 메타 인식
│   ├── resource_allocator.py   # 자원 분배 (이관)
│   ├── context_sentinel.py     # 맥락 감시 (신규)
│   └── self_reflection.py      # 자기성찰 (신규)
└── loop/                       # 통합 성장 루프 (신규)
    ├── learning_loop.py        # DuRi의 전체 루프 구조 정의
    ├── feedback_integrator.py  # 감정/판단/성장 피드백 통합
    ├── experience_evaluator.py # 회고 기반 학습 강화
    └── quest_runner.py         # 퀘스트 실행 루프
```

### **duri_modules (범용 유틸리티, 분석기)**
```
duri_modules/
├── emotion_analyzer.py         # 범용 감정 분석기
├── quest_calculator.py         # 퀘스트 계산기 (기존)
├── time_tracker.py             # 시간 추적기
├── decision_utils.py           # 의사결정 유틸리티
├── performance_metrics.py      # 성능 메트릭
└── common_utils.py             # 공통 유틸리티
```

### **duri_interface (향후 확장)**
```
duri_interface/
├── api_router.py               # API 라우터
├── voice_input.py              # 음성 입력 처리
├── web_ui_adapter.py           # 웹 UI 어댑터
└── visualizer.py               # 시각화 도구
```

### **duri_tests (테스트 전용)**
```
duri_tests/
├── test_emotion_filter.py      # 감정 필터 테스트
├── test_growth_system.py       # 성장 시스템 테스트
├── test_judgment_system.py     # 판단 시스템 테스트
├── test_quest_system.py        # 퀘스트 시스템 테스트
├── test_integration.py         # 통합 테스트
└── test_performance.py         # 성능 테스트
```

## 🔄 **보완된 이관 계획**

### **Phase 1: 감정 시스템 이관 + 연결성 추가 (1일)**
- `duri_core_node/enhanced_emotion_filter.py` → `duri_brain/emotion/emotion_filter.py`
- `duri_modules/emotion/emotion_analyzer.py` → `duri_brain/emotion/emotion_analyzer.py`
- `duri_brain/app/services/emotional_intelligence_service.py` → `duri_brain/emotion/emotion_intelligence.py`
- **신규**: `emotion/judgment_bridge.py` 생성 (감정-판단 연결)

### **Phase 2: 성장 시스템 이관 + 퀘스트 시스템 추가 (1일)**
- `duri_core_node/growth_level_system.py` → `duri_brain/growth/growth_manager.py`
- `duri_core_node/growth_stages.py` → `duri_brain/growth/growth_stages.py`
- **신규**: `growth/growth_quests.py` 생성 (퀘스트 관리)
- **신규**: `growth/emotion_relay.py` 생성 (성장-감정 연결)

### **Phase 3: 판단 시스템 이관 + 피드백 연결 (1일)**
- `duri_brain/thinking/bias_detector.py` → `duri_brain/judgment/bias_detector.py`
- `duri_brain/thinking/judgment_consciousness.py` → `duri_brain/judgment/judgment_consciousness.py`
- **신규**: `judgment/growth_feedback.py` 생성 (판단-성장 피드백)

### **Phase 4: 메모리 시스템 이관 + 퀘스트 회고 (1일)**
- `duri_core_node/cognitive_bandwidth_manager.py` → `duri_brain/meta/resource_allocator.py`
- **신규**: `memory/growth_feedback_logger.py` 생성 (퀘스트 이력 저장)
- **신규**: `memory/replay_interface.py` 생성 (퀘스트 회상)

### **Phase 5: 통합 성장 루프 생성 (1일)**
- **신규**: `loop/learning_loop.py` 생성 (전체 루프 구조)
- **신규**: `loop/feedback_integrator.py` 생성 (피드백 통합)
- **신규**: `loop/experience_evaluator.py` 생성 (회고 기반 학습)
- **신규**: `loop/quest_runner.py` 생성 (퀘스트 실행 루프)

## 🧠 **성장 기반 AI 특성 반영**

### **1. 퀘스트 시스템 (growth_quests.py)**
```python
class QuestManager:
    def __init__(self):
        self.active_quests = []
        self.completed_quests = []
        self.quest_progress = {}
    
    def check_quest_completion(self, emotion_state, judgment_result, growth_metrics):
        # 퀘스트 조건 달성 확인
        # 커서와의 상호작용 처리
        # 성장 트리거 생성
```

### **2. 메모리-성장 연결 (growth_feedback_logger.py)**
```python
class GrowthFeedbackLogger:
    def __init__(self):
        self.quest_history = []
        self.emotion_quest_correlation = {}
        self.judgment_quest_impact = {}
    
    def log_quest_attempt(self, quest_id, emotion_state, judgment_result, success):
        # 퀘스트 시도 기록
        # 감정-판단-성장 연결 저장
        # 학습 기반 추론 데이터 생성
```

### **3. 모듈 간 연결성 (bridge/replay 계층)**
```python
class EmotionJudgmentBridge:
    def calculate_emotion_impact_on_judgment(self, emotion_state):
        # 감정이 판단에 미치는 영향 점수화
        
class GrowthEmotionRelay:
    def track_growth_impact_on_emotion(self, growth_level, emotion_state):
        # 성장이 감정 조절에 미치는 영향 추적
        
class JudgmentGrowthFeedback:
    def reflect_judgment_on_growth_quest(self, judgment_result, active_quests):
        # 판단 결과가 성장 퀘스트에 반영
```

### **4. 통합 성장 루프 (loop/learning_loop.py)**
```python
class LearningLoop:
    def execute_growth_cycle(self):
        # 1. 감정 상태 확인
        # 2. 판단 수행
        # 3. 퀘스트 실행
        # 4. 메모리 저장
        # 5. 회고 및 학습
        # 6. 성장 피드백
```

## 📊 **예상 효과**

1. **성장 기반 AI 완성**: 퀘스트 시스템으로 진정한 성장 메커니즘 구현
2. **커서 상호작용**: 퀘스트를 통한 커서-DuRi 간 자연스러운 상호작용
3. **학습 기반 추론**: 메모리-피드백 연결로 지속적 학습 가능
4. **자기주도 성장**: 통합 루프로 독립적인 성장 메커니즘 구현
5. **모듈 간 시너지**: 감정-성장-판단의 자연스러운 상호작용

## 🚀 **즉시 실행 계획**

1. **퀘스트 시스템 우선**: `growth_quests.py` 생성 및 기본 구조 구현
2. **메모리-성장 연결**: `growth_feedback_logger.py` 생성
3. **모듈 간 브리지**: `judgment_bridge.py`, `emotion_relay.py` 생성
4. **통합 루프**: `learning_loop.py` 생성으로 전체 시스템 통합

**이 보완된 계획으로 진행하시겠습니까?** 