# 🗺️ DuRiWorkspace CODEMAP

> **생성일**: 2025-09-23
> **분석 범위**: 전체 프로젝트 구조 및 의존성
> **목적**: 리팩터링을 위한 프로젝트 맵핑

---

## 📊 프로젝트 개요

### 기본 통계
- **총 파일 수**: 147개 (Python: 86개, Markdown: 30개, 기타: 31개)
- **총 코드 라인**: 54,270 lines
- **총 파일 크기**: 2.5MB
- **연결성 성공률**: 77.9% (67개 호출 가능, 19개 호출 불가)

### 핵심 서비스 아키텍처
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   DuRi Core     │    │   DuRi Brain    │    │ DuRi Evolution  │
│   (Port 8080)   │◄──►│   (Port 8081)   │◄──►│   (Port 8082)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   DuRi Control  │
                    │   (Port 8083)   │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │   (Port 5432)   │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │     Redis       │
                    │   (Port 6379)   │
                    └─────────────────┘
```

---

## 🏗️ 주요 디렉토리 구조

### 서비스별 구조
| 디렉토리 | 설명 | 주요 파일 | 포트 |
|---------|------|-----------|------|
| `duri_core/` | 메인 오케스트레이션 | `main.py`, `duri_orchestrator.py` | 8080 |
| `duri_brain/` | 감정 처리 및 의사결정 | `app/main.py`, `modules/` | 8081 |
| `duri_evolution/` | 학습 및 진화 시스템 | `app/main.py`, `services/` | 8082 |
| `duri_control/` | 중앙 제어 허브 | `app/main.py`, `api/` | 8083 |
| `DuRiCore/` | 레거시 코어 시스템 | `duri_orchestrator.py`, `modules/` | - |
| `duri_common/` | 공통 유틸리티 | `config/`, `utils/` | - |

### 설정 및 배포
| 디렉토리 | 설명 | 주요 파일 |
|---------|------|-----------|
| `docker/` | Docker 설정 | `Dockerfile.*`, `docker-compose.yml` |
| `config/` | 설정 파일 | `config.py`, `app.json` |
| `ops/` | 운영 스크립트 | `scripts/`, `one_shot_start.sh` |
| `prometheus/` | 모니터링 | `prometheus.yml`, `rules.yml` |
| `grafana/` | 대시보드 | `dashboards/`, `provisioning/` |

---

## 🔗 실행 엔트리포인트

### 메인 서비스 진입점
| 서비스 | 진입점 | 설명 |
|--------|--------|------|
| **Core** | `duri_core/main.py` | FastAPI 서버, 포트 8080 |
| **Brain** | `duri_brain/app/main.py` | 감정 처리 서버, 포트 8081 |
| **Evolution** | `duri_evolution/app/main.py` | 학습 서버, 포트 8082 |
| **Control** | `duri_control/app/main.py` | 제어 허브, 포트 8083 |
| **Legacy Core** | `DuRiCore/duri_orchestrator.py` | 레거시 오케스트레이터 |

### Docker 진입점
| 파일 | 설명 | 서비스 |
|------|------|--------|
| `docker/Dockerfile.core` | Core 서비스 이미지 | duri_core |
| `docker/Dockerfile.brain` | Brain 서비스 이미지 | duri_brain |
| `docker/Dockerfile.evolution` | Evolution 서비스 이미지 | duri_evolution |
| `docker/Dockerfile.control` | Control 서비스 이미지 | duri_control |
| `docker/Dockerfile.allinone` | 통합 서비스 이미지 | duri-allinone |

### 스크립트 진입점
| 파일 | 설명 | 용도 |
|------|------|------|
| `ops/scripts/one_shot_start.sh` | 전체 시스템 시작 | 운영 |
| `ops/scripts/check_health.sh` | 헬스체크 | 모니터링 |
| `duri_cli.py` | CLI 인터페이스 | 개발 |

---

## 📦 주요 모듈 및 의존성

### 핵심 모듈 시스템
| 모듈 | 위치 | 설명 | 의존성 |
|------|------|------|--------|
| **Judgment System** | `DuRiCore/modules/judgment_system.py` | 판단 추적 및 학습 | - |
| **Thought Flow** | `DuRiCore/modules/thought_flow.py` | 사고 흐름 관리 | - |
| **Memory Manager** | `DuRiCore/modules/memory.py` | 메모리 관리 | - |
| **Evolution** | `DuRiCore/modules/evolution.py` | 자기 진화 | - |
| **Module Registry** | `DuRiCore/module_registry.py` | 모듈 등록 시스템 | - |

### 공통 유틸리티
| 모듈 | 위치 | 설명 | 사용처 |
|------|------|------|--------|
| **Config** | `duri_common/config/config.py` | 설정 관리 | 모든 서비스 |
| **Logging** | `duri_common/logging/` | 로깅 시스템 | 모든 서비스 |
| **Database** | `duri_common/database/` | DB 연결 | Core, Brain, Evolution |
| **API Client** | `duri_common/api/` | API 클라이언트 | 서비스 간 통신 |

---

## ⚙️ 설정 파일 및 환경변수

### 환경변수 파일
| 파일 | 설명 | 사용처 |
|------|------|--------|
| `.env` | 메인 환경변수 | 모든 서비스 |
| `.ops.env` | 운영 환경변수 | 스크립트 |
| `deploy/env.prod.example` | 프로덕션 템플릿 | 배포 |

### 설정 파일
| 파일 | 설명 | 서비스 |
|------|------|--------|
| `config/core/app.json` | Core 설정 | duri_core |
| `config/brain/app.json` | Brain 설정 | duri_brain |
| `config/evolution/app.json` | Evolution 설정 | duri_evolution |
| `prometheus.yml` | Prometheus 설정 | 모니터링 |
| `prometheus_rules.yml` | 알람 규칙 | 모니터링 |

---

## 🐳 Docker 및 배포

### Docker Compose 파일
| 파일 | 설명 | 서비스 |
|------|------|--------|
| `docker-compose.yml` | 메인 서비스 | Core, Brain, Evolution, Control |
| `docker-compose.allinone.yml` | 통합 서비스 | All-in-One |
| `compose.health.overlay.yml` | 헬스체크 오버레이 | 모니터링 |

### 의존성 관리
| 파일 | 설명 | 범위 |
|------|------|------|
| `requirements.txt` | Python 의존성 | 전체 |
| `pyproject.toml` | 프로젝트 설정 | 전체 |
| `Makefile` | 빌드 자동화 | 전체 |

---

## 🚨 순환참조 후보

### 의심되는 순환참조
| 모듈 A | 모듈 B | 위험도 | 설명 |
|--------|--------|--------|------|
| `DuRiCore/duri_orchestrator.py` | `DuRiCore/module_registry.py` | 🔴 높음 | 오케스트레이터 ↔ 레지스트리 |
| `duri_common/config/` | `duri_core/` | 🟡 중간 | 설정 ↔ 코어 |
| `duri_brain/modules/` | `duri_common/` | 🟡 중간 | 브레인 ↔ 공통 |

### Import 실패 모듈 (19개)
```
❌ test_core_system.py - DuRiCore import 오류
❌ DuRiCore/utils/vector_db.py - faiss 모듈 없음
❌ DuRiCore/interface/__init__.py - InputData import 오류
❌ DuRiCore/interface/main.py - InputData import 오류
❌ DuRiCore/interface/api/* - InputData import 오류 (6개 파일)
```

---

## 🔄 중복 유틸 및 Dead Code 후보

### 중복 설정 파일
| 파일 | 중복 대상 | 우선순위 |
|------|-----------|----------|
| `config/common/config.py` | `duri_common/config/config.py` | 🔴 높음 |
| `config/core/app.json` | `duri_core/config/app.json` | 🟡 중간 |
| `docker-compose.yml.backup` | `docker-compose.yml` | 🟢 낮음 |

### Dead Code 후보
| 파일/디렉토리 | 설명 | 제거 우선순위 |
|---------------|------|---------------|
| `DuRiCore_backup_*/` | 백업 디렉토리들 | 🔴 높음 |
| `backup_*/` | 백업 스크립트들 | 🟡 중간 |
| `test_*.py` | 테스트 파일들 (일부) | 🟢 낮음 |

---

## 📈 수정 제안 목록

### 🔴 높은 우선순위 (즉시 처리)

#### 1. 구조 재배치
- **문제**: `duri_common/`과 `config/` 중복
- **해결**: `duri_common/`으로 통합, import 경로 정리
- **영향**: 모든 서비스의 설정 로딩

#### 2. Import 오류 수정
- **문제**: 19개 모듈 import 실패
- **해결**: `InputData` 클래스 정의, `faiss` 설치
- **영향**: 시스템 안정성

#### 3. Docker 최적화
- **문제**: 멀티스테이지 빌드 미적용
- **해결**: 각 Dockerfile 멀티스테이지 전환
- **영향**: 빌드 속도, 이미지 크기

### 🟡 중간 우선순위 (단계적 처리)

#### 4. 설정 표준화
- **문제**: JSON, Python, ENV 혼재
- **해결**: Pydantic Settings 기반 통일
- **영향**: 설정 관리 일관성

#### 5. 로깅 표준화
- **문제**: 각 서비스별 로깅 방식 상이
- **해결**: JSON 구조화 로깅 통일
- **영향**: 로그 분석 효율성

#### 6. 메트릭 표준화
- **문제**: Prometheus 메트릭 산재
- **해결**: `duri_common/metrics.py` 헬퍼 제공
- **영향**: 모니터링 일관성

### 🟢 낮은 우선순위 (정리)

#### 7. Dead Code 제거
- **문제**: 백업 디렉토리, 미사용 파일들
- **해결**: 안전한 제거 및 정리
- **영향**: 코드베이스 크기

#### 8. 문서화 개선
- **문제**: README, API 문서 부족
- **해결**: 자동 문서 생성, 런북 작성
- **영향**: 개발자 경험

---

## 🎯 리팩터링 로드맵

### Phase 1: 구조 정리 (1-2일)
1. `duri_common/` 통합 및 import 정리
2. Import 오류 수정
3. 기본 테스트 통과 확인

### Phase 2: 설정 표준화 (2-3일)
1. Pydantic Settings 도입
2. 환경변수 통합 관리
3. 설정 검증 시스템

### Phase 3: Docker 최적화 (1-2일)
1. 멀티스테이지 빌드 적용
2. 이미지 크기 최적화
3. 빌드 캐시 최적화

### Phase 4: 모니터링 강화 (2-3일)
1. 로깅 표준화
2. 메트릭 통합
3. 알람 규칙 정리

### Phase 5: 정리 및 문서화 (1-2일)
1. Dead Code 제거
2. 문서 자동화
3. CI/CD 파이프라인

---

## 🔍 리스크 분석

### 높은 리스크
- **Import 오류**: 시스템 안정성에 직접 영향
- **순환참조**: 런타임 오류 가능성
- **설정 중복**: 운영 중 설정 불일치

### 중간 리스크
- **Docker 최적화**: 빌드 프로세스 변경
- **로깅 변경**: 기존 로그 분석 도구 영향

### 낮은 리스크
- **Dead Code 제거**: 기능에 영향 없음
- **문서화**: 개발자 경험만 영향

---

## 📋 체크리스트

### 사전 준비
- [ ] 백업 생성 (`SAFE_BACKUP` 태그)
- [ ] 브랜치 생성 (`ops/agent-refactor-duri`)
- [ ] 테스트 환경 준비

### 실행 중
- [ ] 각 단계별 diff 리뷰
- [ ] 부분 적용 및 검증
- [ ] 롤백 계획 준비

### 완료 후
- [ ] 전체 테스트 통과
- [ ] 성능 벤치마크
- [ ] 문서 업데이트

---

*이 CODEMAP은 2025-09-23 기준으로 생성되었으며, 리팩터링 진행에 따라 업데이트됩니다.*
