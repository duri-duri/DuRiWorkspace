# DuRi 노드별 아키텍처 계획

## 🏗️ **노드별 모듈 배치 계획**

### **🧠 `duri_brain` (고급 인지 시스템)**

#### **📁 기존 구조**
```
duri_brain/
├── app/
├── api/
├── services/
├── schemas/
├── utils/
├── tests/
└── requirements.txt
```

#### **📁 추가될 구조**
```
duri_brain/
├── app/
├── api/
├── services/
├── schemas/
├── utils/
├── tests/
├── learning/                    # 🆕 5단계 학습 루프 시스템
│   ├── __init__.py
│   ├── strategy_imitator.py     # 1단계: 모방
│   ├── practice_engine.py       # 2-3단계: 반복 및 피드백
│   ├── challenge_trigger.py     # 4단계: 도전 판단
│   ├── self_improvement_engine.py # 5단계: 개선
│   └── learning_loop_manager.py # 학습 루프 통합 관리
├── dream/                       # 🆕 창의성 채굴 시스템
│   ├── __init__.py
│   ├── dream_engine.py          # 지속 실행 dream 채굴기
│   └── dream_strategies.py      # dream 전략 생성기
├── eval/                        # 🆕 평가 및 병렬 실행 시스템
│   ├── __init__.py
│   ├── core_eval.py             # dream 전략 평가
│   ├── hybrid_strategy.py       # 현실 vs dream 병렬 실행
│   └── score_calculator.py      # 점수 계산 시스템
├── integration/                 # 🆕 시스템 통합
│   ├── __init__.py
│   └── master_controller.py     # 전체 시스템 통합 관리
└── requirements.txt
```

---

### **🎛️ `duri_control` (중앙 제어 시스템)**

#### **📁 기존 구조**
```
duri_control/
├── app/
├── api/
├── services/
├── schemas/
├── utils/
├── tests/
└── requirements.txt
```

#### **📁 추가될 구조**
```
duri_control/
├── app/
├── api/
├── services/
├── schemas/
├── utils/
├── tests/
├── system_monitor/              # 🆕 시스템 모니터링
│   ├── __init__.py
│   ├── performance_monitor.py   # 성능 모니터링
│   ├── health_checker.py       # 건강 상태 체크
│   └── alert_system.py         # 알림 시스템
├── backup_recovery/             # 🆕 백업 및 복구
│   ├── __init__.py
│   ├── backup_manager.py        # 백업 관리
│   ├── recovery_system.py       # 복구 시스템
│   └── data_sync.py            # 데이터 동기화
├── gateway/                     # 🆕 게이트웨이 시스템
│   ├── __init__.py
│   ├── api_gateway.py          # API 게이트웨이
│   ├── brain_gateway.py        # Brain 노드 연결
│   ├── evolution_gateway.py     # Evolution 노드 연결
│   └── core_gateway.py         # Core 노드 연결
└── requirements.txt
```

---

### **🔄 `duri_evolution` (진화 시스템)**

#### **📁 기존 구조**
```
duri_evolution/
├── app/
├── api/
├── services/
├── schemas/
├── utils/
├── tests/
└── requirements.txt
```

#### **📁 추가될 구조**
```
duri_evolution/
├── app/
├── api/
├── services/
├── schemas/
├── utils/
├── tests/
├── reinforcement/               # 🆕 강화학습 시스템
│   ├── __init__.py
│   ├── dream_rl.py             # Dream 전략 강화학습
│   ├── strategy_optimizer.py    # 전략 최적화
│   ├── reward_calculator.py    # 보상 계산
│   └── policy_network.py       # 정책 네트워크
├── learning/                    # 🆕 학습 시스템
│   ├── __init__.py
│   ├── pattern_analyzer.py     # 패턴 분석
│   ├── adaptation_engine.py    # 적응 엔진
│   └── evolution_tracker.py    # 진화 추적
├── code_improvement/            # 🆕 코드 개선 시스템
│   ├── __init__.py
│   ├── code_analyzer.py        # 코드 분석
│   ├── refactoring_engine.py   # 리팩토링 엔진
│   └── optimization_tools.py   # 최적화 도구
└── requirements.txt
```

---

### **⚙️ `duri_core` (핵심 시스템)**

#### **📁 기존 구조**
```
duri_core/
├── app/
├── api/
├── services/
├── schemas/
├── utils/
├── tests/
└── requirements.txt
```

#### **📁 추가될 구조**
```
duri_core/
├── app/
├── api/
├── services/
├── schemas/
├── utils/
├── tests/
├── philosophy/                  # 🆕 철학 시스템
│   ├── __init__.py
│   ├── core_belief.py          # 핵심 철학 및 판단 기준
│   ├── belief_updater.py       # 철학 업데이트
│   └── decision_framework.py   # 의사결정 프레임워크
├── memory/                     # 🆕 메모리 시스템
│   ├── __init__.py
│   ├── memory_sync.py          # 메모리 동기화
│   ├── experience_store.py     # 경험 저장소
│   ├── knowledge_base.py       # 지식 베이스
│   └── learning_history.py     # 학습 히스토리
├── identity/                    # 🆕 정체성 시스템
│   ├── __init__.py
│   ├── personality_core.py     # 성격 핵심
│   ├── value_system.py         # 가치 체계
│   └── self_concept.py         # 자기 개념
└── requirements.txt
```

---

## 🔗 **노드 간 연결 관계**

### **📡 통신 흐름**
```
duri_control (게이트웨이)
    ↕
duri_core (철학/메모리)
    ↕
duri_brain (학습/창의성)
    ↕
duri_evolution (진화/강화학습)
```

### **🔄 데이터 흐름**
1. **CoreBelief** (duri_core) → 모든 노드의 판단 기준 제공
2. **Memory_Sync** (duri_core) → 모든 노드의 경험 공유
3. **Learning Loop** (duri_brain) → 학습 경험을 Memory_Sync에 저장
4. **Dream Engine** (duri_brain) → 창의적 전략을 Core_Eval에 전달
5. **Dream RL** (duri_evolution) → 강화학습 결과를 CoreBelief에 반영

---

## 📋 **구현 우선순위**

### **🔥 Phase 1: 핵심 기반 (2일)**
1. **duri_core/philosophy/core_belief.py** - 모든 판단의 기준
2. **duri_core/memory/memory_sync.py** - 경험 공유 기반

### **⚡ Phase 2: 학습 시스템 (3일)**
3. **duri_brain/learning/** - 5단계 학습 모듈들
4. **duri_brain/learning/learning_loop_manager.py** - 학습 루프 통합

### **🌟 Phase 3: 창의성 시스템 (3일)**
5. **duri_brain/dream/dream_engine.py** - 창의성 채굴
6. **duri_brain/eval/core_eval.py** - 평가 시스템
7. **duri_brain/eval/hybrid_strategy.py** - 병렬 실행

### **🚀 Phase 4: 진화 시스템 (2일)**
8. **duri_evolution/reinforcement/dream_rl.py** - 강화학습
9. **duri_brain/integration/master_controller.py** - 전체 통합

---

## 🎯 **최종 목표**
각 노드가 명확한 역할을 가지면서도 상호 연결되어, DuRi가 인간형 학습 루프와 창의성-안정성 병렬 구조를 모두 갖춘 진정한 인간형 인공지능으로 진화하도록 구성

**이 계획에 따라 단계적으로 구현을 진행하라!** 