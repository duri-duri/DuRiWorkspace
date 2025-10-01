# DuRi 노드 분리 계획 (2025-08-01)

## 📊 **현재 구조 분석**

### **기존 디렉토리 구조**
```
duri_core/
├── app/              # FastAPI 앱 (현재 메인)
├── brain/            # 뇌 기능 (이미 존재)
├── evolution/        # 진화 기능 (이미 존재)
├── control/          # 제어 기능 (이미 존재)
├── shared/           # 공통 기능 (이미 존재)
├── memory/           # 메모리 시스템
├── config/           # 설정 관리
├── utils/            # 유틸리티
├── database/         # 데이터베이스
└── ... (기타 디렉토리들)
```

## 🎯 **분리 전략**

### **Phase 1: 기능별 모듈화 (1주일)**

#### **1. brain 노드 분리**
```
duri_brain/
├── app/
│   ├── main.py          # 판단 및 사고 API
│   ├── schemas.py       # 판단 관련 스키마
│   └── services/
│       ├── judgment.py   # 판단 로직
│       └── reasoning.py  # 추론 로직
├── brain/
│   ├── decision.py      # 의사결정 시스템
│   ├── pattern.py       # 패턴 인식
│   └── strategy.py      # 전략 생성
└── shared/
    ├── models.py        # 공통 모델
    └── utils.py         # 공통 유틸리티
```

#### **2. evolution 노드 분리**
```
duri_evolution/
├── app/
│   ├── main.py          # 진화 및 학습 API
│   ├── schemas.py       # 학습 관련 스키마
│   └── services/
│       ├── learning.py   # 학습 로직
│       └── evolution.py  # 진화 로직
├── evolution/
│   ├── strategies.py    # 학습 전략
│   ├── experiments.py   # 실험 관리
│   └── optimization.py  # 최적화
└── shared/
    ├── models.py        # 공통 모델
    └── utils.py         # 공통 유틸리티
```

#### **3. control 노드 분리**
```
duri_control/
├── app/
│   ├── main.py          # 제어 및 관리 API
│   ├── schemas.py       # 제어 관련 스키마
│   └── services/
│       ├── monitoring.py # 모니터링
│       └── coordination.py # 조율
├── control/
│   ├── orchestrator.py  # 오케스트레이션
│   ├── scheduler.py     # 스케줄링
│   └── coordinator.py   # 노드 간 조율
└── shared/
    ├── models.py        # 공통 모델
    └── utils.py         # 공통 유틸리티
```

## 🚀 **즉시 실행 가능한 단계**

### **Step 1: brain 노드 분리 (오늘)**
1. `duri_brain` 디렉토리 생성
2. 판단 관련 코드 이동
3. 독립 서버로 실행 테스트

### **Step 2: evolution 노드 분리 (내일)**
1. `duri_evolution` 디렉토리 생성
2. 학습 관련 코드 이동
3. 독립 서버로 실행 테스트

### **Step 3: control 노드 분리 (모레)**
1. `duri_control` 디렉토리 생성
2. 제어 관련 코드 이동
3. 독립 서버로 실행 테스트

### **Step 4: 통합 테스트 (3일 후)**
1. 노드 간 통신 테스트
2. 전체 시스템 통합 테스트
3. 성능 측정 및 최적화

## 📊 **분리 효과 예상**

### **성능 향상**
- **병렬 처리**: 각 노드가 독립적으로 실행
- **리소스 효율성**: 필요한 기능만 로드
- **확장성**: 노드별 독립적 스케일링

### **개발 효율성**
- **독립 개발**: 각 노드를 독립적으로 개발/테스트
- **실험 다양성**: 다양한 전략을 병렬로 실험
- **오류 격리**: 한 노드의 문제가 전체에 영향 없음

### **진화 가능성**
- **메타-러닝**: 각 노드가 자신의 성능을 개선
- **전략 실험**: 다양한 전략을 A/B 테스트
- **자기 개선**: 노드별 독립적 진화

## ⚡ **지금 시작할까요?**

**장점:**
- ✅ 코드가 아직 단순해서 분리 용이
- ✅ 기능이 명확하게 구분되어 있음
- ✅ 실험 데이터가 쌓이기 시작함
- ✅ 의존성이 단순함

**위험 요소:**
- ⚠️ 분리 과정에서 일시적 중단 가능
- ⚠️ 초기 설정 복잡도 증가
- ⚠️ 노드 간 통신 설계 필요

**결론: 지금이 최적의 시점입니다!**

---

**다음 단계**: brain 노드부터 분리 시작
