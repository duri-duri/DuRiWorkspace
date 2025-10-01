# 📋 DuRi 평가 기준 통합 가이드

## 🎯 개요

DuRi 시스템의 평가 기준들을 명확하게 분리하고 명명 규칙을 통일하여 유지보수성을 향상시켰습니다.

## 📊 평가 기준 분류

### 1️⃣ **SurvivalCriteria** (duri_core/philosophy/survival_criteria.py)
**목적**: 전략 생존 판단 (지속/수정/폐기)
```python
@dataclass
class SurvivalCriteria:
    judgment_period: int = 3          # 판단 주기 (일)
    min_improvement: float = 0.01     # 최소 개선률 (1%)
    failure_threshold: float = 0.5    # 실패율 임계값 (50%)
    emotion_weight: float = 0.3       # 감정 가중치 (30%)
    performance_weight: float = 0.7   # 성과 가중치 (70%)
```

### 2️⃣ **DreamEvaluationCriteria** (duri_brain/eval/core_eval.py)
**목적**: Dream 전략 평가 (채택/거부/유레카)
```python
@dataclass
class DreamEvaluationCriteria:
    performance_weight: float = 0.4   # 성과 가중치 (40%)
    novelty_weight: float = 0.3       # 새로움 가중치 (30%)
    stability_weight: float = 0.2     # 안정성 가중치 (20%)
    efficiency_weight: float = 0.1     # 효율성 가중치 (10%)
    eureka_threshold: float = 0.85    # 유레카 임계값 (85%)
    adoption_threshold: float = 0.7   # 채택 임계값 (70%)
    rejection_threshold: float = 0.3  # 거부 임계값 (30%)
```

### 3️⃣ **LearningEvaluationCriteria** (duri_brain/learning/self_improvement_engine.py)
**목적**: 학습 개선 평가 (성능/효율성/신뢰성/적응성/창의성)
```python
@dataclass
class LearningEvaluationCriteria:
    criteria_name: str                 # 기준 이름
    weight: float                      # 가중치
    current_value: float              # 현재 값
    target_value: float               # 목표 값
    improvement_potential: float      # 개선 잠재력
```

## 🔄 변경 사항

### ✅ **명명 규칙 통일**
- `EvaluationCriteria` → `DreamEvaluationCriteria` (Dream 평가용)
- `EvaluationCriteria` → `LearningEvaluationCriteria` (학습 개선용)
- `SurvivalCriteria` 유지 (생존 판단용)

### ✅ **중복 제거**
- 동일한 이름의 다른 클래스 제거
- 각 평가 기준의 목적 명확화
- 의존성 정리

### ✅ **문서화**
- 각 평가 기준의 목적과 사용법 명확화
- 향후 개발자를 위한 가이드 제공

## 📈 사용 패턴

### **1. 전략 생존 판단**
```python
from duri_core.philosophy.survival_criteria import get_survival_criteria_manager

survival_manager = get_survival_criteria_manager()
# 3일간 1% 미만 개선 시 전략 수정/폐기 판단
```

### **2. Dream 전략 평가**
```python
from duri_brain.eval.core_eval import get_core_eval

eval_system = get_core_eval()
# Dream 전략의 채택/거부/유레카 판단
```

### **3. 학습 개선 평가**
```python
from duri_brain.learning.self_improvement_engine import get_self_improvement_engine

improvement_engine = get_self_improvement_engine()
# 학습 개선 시 성능/효율성/신뢰성 등 평가
```

## 🎯 장점

### **1. 명확한 분리**
- 각 평가 기준이 명확한 목적을 가짐
- 혼동 가능성 제거
- 유지보수성 향상

### **2. 확장성**
- 새로운 평가 기준 추가 시 일관된 명명 규칙
- 각 모듈의 독립성 유지
- 향후 통합 시 유연성 확보

### **3. 문서화**
- 각 평가 기준의 목적과 사용법 명확화
- 개발자 온보딩 시간 단축
- 코드 이해도 향상

## 🚀 향후 계획

### **Phase 1: 완료 ✅**
- 명명 규칙 통일
- 중복 제거
- 기본 문서화

### **Phase 2: 고려사항**
- 필요시 공통 인터페이스 도입
- 중앙 관리 시스템 구축
- 고급 통합 기능 추가

## 📝 결론

평가 기준 통합 작업을 통해 DuRi 시스템의 명확성과 유지보수성이 크게 향상되었습니다. 각 평가 기준이 명확한 목적을 가지고 독립적으로 작동하면서도, 일관된 명명 규칙을 통해 시스템의 통일성을 확보했습니다.
