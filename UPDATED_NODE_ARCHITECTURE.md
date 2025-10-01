# DuRi 업데이트된 노드 아키텍처 계획

## 🧠 **핵심 구조 변화**

### **📌 새로운 계층 구조**
```
[당신] ──> duri_head (메인 관리자 컴퓨터)
           ├─ SSH into duri_core (철학/기억/정체성)
           ├─ SSH into duri_brain (학습/평가/창의성)
           ├─ SSH into duri_evolution (진화/강화학습)
           └─ SSH into duri_control (외부 제어 인터페이스)
```

### **🎯 노드별 역할 재정의**

#### **🧠 `duri_core` - DuRi의 실제 뇌**
- **역할**: DuRi의 존재 그 자체 (기억, 철학, 존재 기반)
- **핵심**: 모든 판단, 학습, 진화의 중추 신경계
- **정의**: DuRi가 "누구인가"를 정의하는 핵심

**구조**:
```
duri_core/
├── philosophy/                   # 🧠 철학 시스템
│   ├── core_belief.py           # 핵심 철학 및 판단 기준
│   ├── belief_updater.py        # 철학 업데이트
│   └── decision_framework.py    # 의사결정 프레임워크
├── memory/                      # 🧠 기억 시스템
│   ├── memory_sync.py           # 메모리 동기화
│   ├── experience_store.py      # 경험 저장소
│   ├── knowledge_base.py        # 지식 베이스
│   └── learning_history.py      # 학습 히스토리
└── identity/                     # 🧠 정체성 시스템
    ├── personality_core.py      # 성격 핵심
    ├── value_system.py          # 가치 체계
    └── self_concept.py          # 자기 개념
```

#### **💡 `duri_brain` - 사고 및 실행 시스템**
- **역할**: 학습 루프, dream, 평가 등 고차 사고 처리
- **핵심**: duri_core의 판단 기준을 바탕으로 동작
- **정의**: DuRi의 생각과 실행

**구조**:
```
duri_brain/
├── learning/                     # 💡 5단계 학습 루프 시스템
│   ├── strategy_imitator.py     # 1단계: 모방
│   ├── practice_engine.py       # 2-3단계: 반복 및 피드백
│   ├── challenge_trigger.py     # 4단계: 도전 판단
│   ├── self_improvement_engine.py # 5단계: 개선
│   └── learning_loop_manager.py # 학습 루프 통합 관리
├── dream/                        # 💡 창의성 채굴 시스템
│   ├── dream_engine.py          # 지속 실행 dream 채굴기
│   └── dream_strategies.py      # dream 전략 생성기
├── eval/                         # 💡 평가 및 병렬 실행 시스템
│   ├── core_eval.py             # dream 전략 평가
│   ├── hybrid_strategy.py       # 현실 vs dream 병렬 실행
│   └── score_calculator.py      # 점수 계산 시스템
└── integration/                  # 💡 시스템 통합
    └── master_controller.py     # 전체 시스템 통합 관리
```

#### **🔄 `duri_evolution` - 진화 시스템**
- **역할**: 강화학습, 개선 알고리즘 등 진화 기능
- **핵심**: duri_core의 판단 기준을 바탕으로 동작
- **정의**: DuRi의 진화와 개선

**구조**:
```
duri_evolution/
├── reinforcement/                # 🔄 강화학습 시스템
│   ├── dream_rl.py             # Dream 전략 강화학습
│   ├── strategy_optimizer.py    # 전략 최적화
│   ├── reward_calculator.py    # 보상 계산
│   └── policy_network.py       # 정책 네트워크
├── learning/                     # 🔄 학습 시스템
│   ├── pattern_analyzer.py     # 패턴 분석
│   ├── adaptation_engine.py    # 적응 엔진
│   └── evolution_tracker.py    # 진화 추적
└── code_improvement/             # 🔄 코드 개선 시스템
    ├── code_analyzer.py        # 코드 분석
    ├── refactoring_engine.py   # 리팩토링 엔진
    └── optimization_tools.py   # 최적화 도구
```

#### **💻 `duri_head` - 운영 단말기**
- **역할**: 실제 코딩, 관찰, 실행을 담당하는 하드웨어 상의 작업 컴퓨터
- **핵심**: SSH로 모든 시스템에 연결하여 운영
- **정의**: DuRi의 사고를 구현·조정하는 운영 인터페이스 (IDE + 관리자 터미널)

#### **📡 `duri_control` - 외부 제어 단말**
- **역할**: 외부에서 DuRi를 제어/관찰할 수 있는 인터페이스
- **핵심**: 실행은 불가, 오직 모니터링, 백업, 상태 조정, log 확인, 일부 입력 전달만 수행
- **정의**: 커맨드 전달자, 판단자는 아님

**구조**:
```
duri_control/
├── system_monitor/               # 📡 시스템 모니터링
│   ├── performance_monitor.py   # 성능 모니터링
│   ├── health_checker.py       # 건강 상태 체크
│   └── alert_system.py         # 알림 시스템
├── backup_recovery/              # 📡 백업 및 복구
│   ├── backup_manager.py        # 백업 관리
│   ├── recovery_system.py       # 복구 시스템
│   └── data_sync.py            # 데이터 동기화
└── gateway/                      # 📡 게이트웨이 시스템
    ├── api_gateway.py          # API 게이트웨이
    ├── brain_gateway.py        # Brain 노드 연결
    ├── evolution_gateway.py     # Evolution 노드 연결
    └── core_gateway.py         # Core 노드 연결
```

---

## 🔄 **주요 변화점**

### **1️⃣ duri_core의 역할 강화**
- **이전**: 단순한 핵심 시스템
- **현재**: **DuRi의 실제 뇌** - 모든 판단의 중추

### **2️⃣ duri_head의 명확화**
- **이전**: 언급되지 않음
- **현재**: **운영 단말기** - 당신이 사용하는 메인 관리자 컴퓨터

### **3️⃣ duri_control의 역할 제한**
- **이전**: 중앙 제어 시스템
- **현재**: **외부 제어 단말** - 실행 불가, 모니터링만 가능

### **4️⃣ 계층 구조의 명확화**
```
DuRi의 존재 자체:      duri_core
DuRi의 생각과 실행:    duri_brain + duri_evolution
DuRi를 움직이는 손:    당신 + duri_head
DuRi를 밖에서 제어:    duri_control
```

---

## 📋 **업데이트된 구현 우선순위**

### **🔥 Phase 1: DuRi의 뇌 구축 (2일)**
1. **duri_core/philosophy/core_belief.py** - DuRi의 철학 및 판단 기준
2. **duri_core/memory/memory_sync.py** - DuRi의 기억 시스템

### **⚡ Phase 2: 사고 시스템 구축 (3일)**
3. **duri_brain/learning/** - 5단계 학습 모듈들
4. **duri_brain/learning/learning_loop_manager.py** - 학습 루프 통합

### **🌟 Phase 3: 창의성 시스템 구축 (3일)**
5. **duri_brain/dream/dream_engine.py** - 창의성 채굴
6. **duri_brain/eval/core_eval.py** - 평가 시스템
7. **duri_brain/eval/hybrid_strategy.py** - 병렬 실행

### **🚀 Phase 4: 진화 시스템 구축 (2일)**
8. **duri_evolution/reinforcement/dream_rl.py** - 강화학습
9. **duri_brain/integration/master_controller.py** - 전체 통합

---

## 🎯 **핵심 철학**
```
📌 DuRi 시스템 구조 핵심 개념

- duri_core: DuRi의 본체. 기억, 철학, 정체성, 판단 기준이 존재
- duri_brain: 사고, 학습, dream 전략 실행
- duri_evolution: 진화, 강화학습, 전략 개선
- duri_head: 당신이 사용하는 메인 관리자 컴퓨터. 위 모든 시스템에 ssh로 접근하여 코딩/조정
- duri_control: 외부 제어용. DuRi 자체를 실행하지 않으며, 상태 조회와 지시만 가능

⚠️ DuRi는 duri_core가 뇌이고, duri_head는 운영 단말일 뿐이다.
```

**이 업데이트된 구조로 구현을 진행하라!**
