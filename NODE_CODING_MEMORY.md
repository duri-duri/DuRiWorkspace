# DuRi 노드별 코딩 메모리 - 절대 혼동 금지

## 🧠 **duri_core - DuRi의 실제 뇌 (절대 다른 곳에 넣지 말 것)**

### **📁 구조**
```
duri_core/
├── philosophy/                   # 🧠 철학 시스템 (DuRi의 판단 기준)
│   ├── __init__.py
│   ├── core_belief.py           # 핵심 철학 및 판단 기준
│   ├── belief_updater.py        # 철학 업데이트
│   └── decision_framework.py    # 의사결정 프레임워크
├── memory/                      # 🧠 기억 시스템 (DuRi의 경험 저장)
│   ├── __init__.py
│   ├── memory_sync.py           # 메모리 동기화
│   ├── experience_store.py      # 경험 저장소
│   ├── knowledge_base.py        # 지식 베이스
│   └── learning_history.py      # 학습 히스토리
└── identity/                     # 🧠 정체성 시스템 (DuRi의 존재 정의)
    ├── __init__.py
    ├── personality_core.py      # 성격 핵심
    ├── value_system.py          # 가치 체계
    └── self_concept.py          # 자기 개념
```

### **⚠️ 절대 다른 노드에 넣지 말 것**
- **철학 시스템**: 오직 duri_core에만
- **기억 시스템**: 오직 duri_core에만  
- **정체성 시스템**: 오직 duri_core에만

---

## 💡 **duri_brain - 사고 및 실행 시스템**

### **📁 구조**
```
duri_brain/
├── learning/                     # 💡 5단계 학습 루프 시스템
│   ├── __init__.py
│   ├── strategy_imitator.py     # 1단계: 모방
│   ├── practice_engine.py       # 2-3단계: 반복 및 피드백
│   ├── challenge_trigger.py     # 4단계: 도전 판단
│   ├── self_improvement_engine.py # 5단계: 개선
│   └── learning_loop_manager.py # 학습 루프 통합 관리
├── dream/                        # 💡 창의성 채굴 시스템
│   ├── __init__.py
│   ├── dream_engine.py          # 지속 실행 dream 채굴기
│   └── dream_strategies.py      # dream 전략 생성기
├── eval/                         # 💡 평가 및 병렬 실행 시스템
│   ├── __init__.py
│   ├── core_eval.py             # dream 전략 평가
│   ├── hybrid_strategy.py       # 현실 vs dream 병렬 실행
│   └── score_calculator.py      # 점수 계산 시스템
└── integration/                  # 💡 시스템 통합
    ├── __init__.py
    └── master_controller.py     # 전체 시스템 통합 관리
```

### **⚠️ 절대 다른 노드에 넣지 말 것**
- **학습 루프**: 오직 duri_brain에만
- **창의성 채굴**: 오직 duri_brain에만
- **평가 시스템**: 오직 duri_brain에만
- **시스템 통합**: 오직 duri_brain에만

---

## 🔄 **duri_evolution - 진화 시스템**

### **📁 구조**
```
duri_evolution/
├── reinforcement/                # 🔄 강화학습 시스템
│   ├── __init__.py
│   ├── dream_rl.py             # Dream 전략 강화학습
│   ├── strategy_optimizer.py    # 전략 최적화
│   ├── reward_calculator.py    # 보상 계산
│   └── policy_network.py       # 정책 네트워크
├── learning/                     # 🔄 학습 시스템
│   ├── __init__.py
│   ├── pattern_analyzer.py     # 패턴 분석
│   ├── adaptation_engine.py    # 적응 엔진
│   └── evolution_tracker.py    # 진화 추적
└── code_improvement/             # 🔄 코드 개선 시스템
    ├── __init__.py
    ├── code_analyzer.py        # 코드 분석
    ├── refactoring_engine.py   # 리팩토링 엔진
    └── optimization_tools.py   # 최적화 도구
```

### **⚠️ 절대 다른 노드에 넣지 말 것**
- **강화학습**: 오직 duri_evolution에만
- **진화 학습**: 오직 duri_evolution에만
- **코드 개선**: 오직 duri_evolution에만

---

## 📡 **duri_control - 외부 제어 단말**

### **📁 구조**
```
duri_control/
├── system_monitor/               # 📡 시스템 모니터링
│   ├── __init__.py
│   ├── performance_monitor.py   # 성능 모니터링
│   ├── health_checker.py       # 건강 상태 체크
│   └── alert_system.py         # 알림 시스템
├── backup_recovery/              # 📡 백업 및 복구
│   ├── __init__.py
│   ├── backup_manager.py        # 백업 관리
│   ├── recovery_system.py       # 복구 시스템
│   └── data_sync.py            # 데이터 동기화
└── gateway/                      # 📡 게이트웨이 시스템
    ├── __init__.py
    ├── api_gateway.py          # API 게이트웨이
    ├── brain_gateway.py        # Brain 노드 연결
    ├── evolution_gateway.py     # Evolution 노드 연결
    └── core_gateway.py         # Core 노드 연결
```

### **⚠️ 절대 다른 노드에 넣지 말 것**
- **모니터링**: 오직 duri_control에만
- **백업/복구**: 오직 duri_control에만
- **게이트웨이**: 오직 duri_control에만

---

## 🚫 **절대 혼동 금지 규칙**

### **❌ duri_core에 절대 넣지 말 것**
- 학습 루프 (duri_brain에만)
- 창의성 채굴 (duri_brain에만)
- 강화학습 (duri_evolution에만)
- 모니터링 (duri_control에만)

### **❌ duri_brain에 절대 넣지 말 것**
- 철학 시스템 (duri_core에만)
- 기억 시스템 (duri_core에만)
- 강화학습 (duri_evolution에만)
- 모니터링 (duri_control에만)

### **❌ duri_evolution에 절대 넣지 말 것**
- 철학 시스템 (duri_core에만)
- 기억 시스템 (duri_core에만)
- 학습 루프 (duri_brain에만)
- 모니터링 (duri_control에만)

### **❌ duri_control에 절대 넣지 말 것**
- 철학 시스템 (duri_core에만)
- 기억 시스템 (duri_core에만)
- 학습 루프 (duri_brain에만)
- 강화학습 (duri_evolution에만)

---

## 📋 **구현 순서 (노드별 정확한 위치)**

### **🔥 Phase 1: DuRi의 뇌 구축 (2일)**
1. **duri_core/philosophy/core_belief.py** - DuRi의 철학 및 판단 기준
2. **duri_core/memory/memory_sync.py** - DuRi의 기억 시스템

### **⚡ Phase 2: 사고 시스템 구축 (3일)**
3. **duri_brain/learning/strategy_imitator.py** - 1단계: 모방
4. **duri_brain/learning/practice_engine.py** - 2-3단계: 반복 및 피드백
5. **duri_brain/learning/challenge_trigger.py** - 4단계: 도전 판단
6. **duri_brain/learning/self_improvement_engine.py** - 5단계: 개선
7. **duri_brain/learning/learning_loop_manager.py** - 학습 루프 통합

### **🌟 Phase 3: 창의성 시스템 구축 (3일)**
8. **duri_brain/dream/dream_engine.py** - 창의성 채굴
9. **duri_brain/eval/core_eval.py** - 평가 시스템
10. **duri_brain/eval/hybrid_strategy.py** - 병렬 실행

### **🚀 Phase 4: 진화 시스템 구축 (2일)**
11. **duri_evolution/reinforcement/dream_rl.py** - 강화학습
12. **duri_brain/integration/master_controller.py** - 전체 통합

---

## 🎯 **핵심 기억 사항**
- **duri_core**: DuRi의 뇌 (철학, 기억, 정체성)
- **duri_brain**: DuRi의 사고 (학습, 창의성, 평가)
- **duri_evolution**: DuRi의 진화 (강화학습, 개선)
- **duri_control**: 외부 제어 (모니터링, 백업, 게이트웨이)

**이 문서를 매일 참조하여 노드별 코딩을 정확히 구분하라!** 