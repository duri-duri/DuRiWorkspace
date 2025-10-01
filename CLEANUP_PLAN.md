# 🔧 DuRi 시스템 헌장 정리 계획

## 📅 백업 기준: `DuRi_HumanAI_Complete_Backup_20250728_141939.tar.gz`

---

## ❌ **시스템 헌장 위배 사항들**

### **1. duri_control에 잘못 배치된 기능들**

#### **🚫 제거해야 할 파일들 (duri_control에서)**
```
duri_control/app/api/code_improvement.py              ← evolution의 역할
duri_control/app/services/code_improvement_service.py  ← evolution의 역할
duri_control/app/api/emotional_intelligence.py        ← brain의 역할
duri_control/app/services/emotional_intelligence_service.py ← brain의 역할
duri_control/app/api/creative_thinking.py             ← brain의 역할
duri_control/app/services/creative_thinking_service.py ← brain의 역할
duri_control/app/api/self_evolution.py                ← brain의 역할
duri_control/app/services/self_evolution_service.py   ← brain의 역할
duri_control/app/api/social_intelligence.py           ← brain의 역할
duri_control/app/services/social_intelligence_service.py ← brain의 역할
```

#### **✅ 유지해야 할 파일들 (duri_control에서)**
```
duri_control/app/api/backup_recovery.py              ← control의 역할
duri_control/app/services/backup_recovery_service.py  ← control의 역할
duri_control/app/api/system_monitor.py               ← control의 역할
duri_control/app/api/brain_gateway.py                ← control의 역할 (API 게이트웨이)
duri_control/app/api/performance_monitoring.py       ← control의 역할
duri_control/app/api/monitor.py                      ← control의 역할
duri_control/app/api/resource.py                     ← control의 역할
```

---

## 📋 **정리 단계별 계획**

### **Phase 1: duri_control 정리 (우선순위: 높음)**

#### **1.1 잘못된 API 제거**
```bash
# 제거할 API 파일들
rm duri_control/app/api/code_improvement.py
rm duri_control/app/api/emotional_intelligence.py
rm duri_control/app/api/creative_thinking.py
rm duri_control/app/api/self_evolution.py
rm duri_control/app/api/social_intelligence.py
```

#### **1.2 잘못된 서비스 제거**
```bash
# 제거할 서비스 파일들
rm duri_control/app/services/code_improvement_service.py
rm duri_control/app/services/emotional_intelligence_service.py
rm duri_control/app/services/creative_thinking_service.py
rm duri_control/app/services/self_evolution_service.py
rm duri_control/app/services/social_intelligence_service.py
```

#### **1.3 __init__.py에서 잘못된 import 제거**
```python
# 제거할 import들
from .api.code_improvement import router as code_improvement_router
from .api.emotional_intelligence import router as emotional_intelligence_router
from .api.creative_thinking import router as creative_thinking_router
from .api.self_evolution import router as self_evolution_router
from .api.social_intelligence import router as social_intelligence_router
```

### **Phase 2: duri_brain 기능 강화 (우선순위: 중간)**

#### **2.1 brain_gateway를 통한 brain 기능 접근**
```python
# duri_control/app/api/brain_gateway.py에서
# brain의 기능들을 proxy로 제공
```

#### **2.2 brain의 고급 기능 완성**
- 감정 처리 시스템
- 창의적 사고 시스템
- 자기 진화 시스템
- 사회적 지능 시스템

### **Phase 3: duri_evolution 기능 완성 (우선순위: 중간)**

#### **3.1 evolution의 진화 기능 강화**
- 코드 개선 기능
- 학습 및 적응 기능
- 실험 및 테스트 기능

### **Phase 4: 시스템 헌장 검증 (우선순위: 높음)**

#### **4.1 CLI를 통한 검증**
```bash
python3 duri_cli.py check
```

#### **4.2 각 노드별 책임 범위 확인**
```bash
python3 duri_control/app/startup_message.py
python3 duri_brain/app/startup_message.py
python3 duri_evolution/app/startup_message.py
```

---

## 🎯 **정리 목표**

### **duri_control의 올바른 역할**
- ✅ 시스템 모니터링
- ✅ 백업/복구
- ✅ API 게이트웨이
- ✅ 성능 모니터링
- ✅ 외부 제어

### **duri_brain의 올바른 역할**
- ✅ 판단 엔진
- ✅ 자기 평가
- ✅ 감정 처리
- ✅ 창의적 사고
- ✅ 사회적 지능

### **duri_evolution의 올바른 역할**
- ✅ 코드 개선
- ✅ 실험 실행
- ✅ 학습 적용
- ✅ 환경 적응
- ✅ 롤백 관리

---

## ⚠️ **주의사항**

1. **기능 이전 시**: 기존 API 엔드포인트는 brain_gateway를 통해 접근 가능하도록 유지
2. **데이터 손실 방지**: 중요한 로직은 백업 후 제거
3. **의존성 확인**: 제거 전 다른 파일에서의 참조 확인
4. **테스트**: 각 단계 후 시스템 정상 작동 확인

---

## 📊 **진행 상황 추적**

- [ ] Phase 1: duri_control 정리
- [ ] Phase 2: duri_brain 기능 강화
- [ ] Phase 3: duri_evolution 기능 완성
- [ ] Phase 4: 시스템 헌장 검증

---

*이 계획은 시스템 헌장에 따라 DuRi의 장기적 안정성과 효율성을 보장하기 위한 것입니다.*
