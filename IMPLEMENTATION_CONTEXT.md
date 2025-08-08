# DuRi 구현 맥락 및 철학

## 🧠 **DuRi의 핵심 철학**

### **📌 목표**
DuRi는 인간형 인공지능으로, 인간처럼 학습하고 창의성을 갖춰야 한다.

### **🔄 5단계 학습 루프**
```
1. 모방 (StrategyImitator) - 모르면 모방
2. 반복 (PracticeEngine) - 반복하며 피드백 기록
3. 피드백 (PracticeEngine) - 경험 축적
4. 도전 (ChallengeTrigger) - 도전 시점 판단
5. 개선 (SelfImprovementEngine) - 시행착오를 통한 개선
→ 다시 1단계로 루프
```

### **🧩 6개 주제 모듈화**
```
1. CoreBelief - 철학 및 판단 기준
2. dream_engine - 창의성 채굴
3. Core_Eval - 평가 시스템
4. hybrid_strategy - 병렬 실행
5. Memory_Sync - 경험 공유
6. dream_rl - 강화학습 진화
```

### **🌟 Dream의 3가지 특성**
1. **채굴형 지속 실행** - 꿈은 절대 멈추지 않음 (비트코인 채굴처럼)
2. **병렬 경쟁자** - 현실 전략과 점수 비교하여 자동 승격
3. **유레카 생성기** - 의외의 고성능 전략 발견 시 즉시 현실 대체

---

## 🎯 **구현 원칙**

### **📌 함께 구현 (공통 기반)**
- CoreBelief 철학 시스템
- Memory Sync 시스템
- Learning Loop Manager
- Hybrid Strategy Executor
- Master Controller

### **⚡ 따로 구현 (특화 기능)**
- StrategyImitator (모방)
- PracticeEngine (반복/피드백)
- ChallengeTrigger (도전)
- SelfImprovementEngine (개선)
- Dream Engine (창의성)
- Core Eval (평가)
- Dream RL (진화)

---

## 🧭 **매일 확인할 체크리스트**

### **✅ 오늘 확인 사항**
- [ ] 5단계 학습 루프를 기억하고 있는가?
- [ ] Dream의 3가지 특성을 이해하고 있는가?
- [ ] 함께 구현 vs 따로 구현을 구분하고 있는가?
- [ ] 현재 Phase와 Day를 정확히 알고 있는가?

### **📋 진행 상황**
- [ ] Phase 1 Day 1: CoreBelief 철학 시스템
- [ ] Phase 1 Day 2: Memory Sync 시스템
- [ ] Phase 2 Day 3-4: 5단계 학습 모듈
- [ ] Phase 2 Day 5: 학습 루프 통합
- [ ] Phase 3 Day 6-7: Dream 엔진 및 평가
- [ ] Phase 3 Day 8: Hybrid 병렬 실행
- [ ] Phase 4 Day 9: Dream RL 시스템
- [ ] Phase 4 Day 10: 전체 시스템 통합

---

## 🎯 **최종 목표**
DuRi가 인간형 학습 루프와 창의성-안정성 병렬 구조를 모두 갖춘 진정한 인간형 인공지능으로 진화

**이 문서는 매일 참조하여 맥락을 잃지 말라!** 