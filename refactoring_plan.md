# DuRi 리팩터링 + 분산 병행 계획

## 🎯 **목표: 3계층 분산 구조 구축**

### **Node 분리 구조**
```
duri-core (포트 8080)     → API 입구 / 사용자 요청 처리
duri-brain (포트 8081)     → 판단/기억/철학 시스템
duri-evolution (포트 8082) → 자가 학습, 평가, 개선 시스템
```

## 📋 **1단계: 모듈 분류 및 역할 정의**

### **Core (8080) - API Gateway**
- 사용자 요청 수신
- 라우팅 및 로드 밸런싱
- 응답 통합 및 반환
- 헬스체크 및 모니터링

### **Brain (8081) - 판단 시스템**
- `duri_brain/learning/` - 학습 루프 관리
- `duri_brain/goals/` - 목표 설정
- `duri_brain/ethics/` - 윤리 판단
- `duri_brain/creativity/` - 창의성 시스템
- `duri_core/memory/` - 메모리 관리

### **Evolution (8082) - 진화 시스템**
- `duri_modules/autonomous/` - 자율 학습
- `duri_modules/evaluation/` - 평가 시스템
- `duri_modules/reflection/` - 성찰 시스템
- `duri_modules/discussion/` - 논의 시스템

## 🔧 **2단계: 리팩터링 우선순위**

### **🔥 즉시 해결 (1-2일)**
1. **중복 초기화 제거** - 모듈 중복 로드 문제
2. **포트 충돌 해결** - 8080, 8081, 8082 포트 할당
3. **에러 핸들링 강화** - 타입 불일치, NoneType 예외

### **⚡ 단기 목표 (1주)**
1. **모듈 정리** - EvolutionAnalyzer, DataEvaluator 등 역할별 분리
2. **중복 코드 제거** - 진화 점수 계산, 로그 파싱 통합
3. **명확한 입력/출력 명세화** - 각 모듈 간 contract 정의

### **🎯 중기 목표 (2주)**
1. **테스트 프레임워크 재정비** - 단위 테스트 및 리그레션 테스트
2. **설정 통합** - config/system.yaml 등으로 하드코딩 제거
3. **Docker 컨테이너화** - 각 노드별 Dockerfile 생성

## 🚀 **3단계: 구현 순서**

### **Phase 1: Core 노드 분리 (1-2일)**
```bash
# Core 노드 생성
mkdir -p duri_core_node
# API Gateway 기능 구현
# 포트 8080에서 서비스 시작
```

### **Phase 2: Brain 노드 분리 (2-3일)**
```bash
# Brain 노드 생성
mkdir -p duri_brain_node
# 판단 시스템 이전
# 포트 8081에서 서비스 시작
```

### **Phase 3: Evolution 노드 분리 (3-4일)**
```bash
# Evolution 노드 생성
mkdir -p duri_evolution_node
# 진화 시스템 이전
# 포트 8082에서 서비스 시작
```

### **Phase 4: 통합 테스트 (1일)**
```bash
# 전체 시스템 연동 테스트
# 성능 및 안정성 검증
```

## 📊 **예상 효과**

### **✅ 개선 효과**
- **구조 안정성**: 모듈별 독립성 확보
- **확장성**: API 기반 자연스러운 확장
- **유지보수성**: 명확한 책임 분리
- **성능**: 병렬 처리 가능

### **⚠️ 주의사항**
- **초기 복잡도**: 통신 오버헤드 발생 가능
- **테스트 복잡도**: 통신, 동기화 테스트 필요
- **디버깅**: 분산 환경에서 문제 추적 어려움

## 🎯 **결론**
리팩터링과 분산을 병행하여 **"지금이 골든타임"**에 DuRi를 더욱 강력하고 확장 가능한 시스템으로 진화시킵니다.
