# 🚀 DuRi 백업 리팩토링 - 운영자용 스타트 가이드

> **⚠️ 중요**: 이 가이드는 백업 리팩토링 실행을 위한 것입니다. 실행 전 반드시 전체 내용을 읽어주세요.

## ✅ **첫 실행 체크리스트 (DRY-RUN→실행) - 5줄 핵심**

1. `SAFE_BACKUP` 태그 + 전체 스냅샷 생성 완료 여부 확인
2. `config.env` 환경변수(경로·브랜치·토큰) 정확히 설정  
3. DRY-RUN 모드(`export DRY_RUN=1`)로 `summary_report.sh` 실행 → summary.json/summary.md 생성 확인
4. 로그에 오류(FAIL/FATAL) 없고 README 미수정 확인
5. DRY-RUN 해제 후 재실행 → README Phase 표 ✅ 자동 반영 확인

## 🎯 **백업 리팩토링 목표**

- **실패율**: 0.1%/일 → ≤0.01%/일 (10배 개선)
- **RTO**: 50% 단축 + Silent corruption 탐지
- **운영 판단**: 10분/일 → ≤5분/일
- **안정성**: 업계 상위 5% → 엔터프라이즈급(금융기관 수준)

## 📊 **10주 Super-Safe 로드맵**

| Phase | 설명 | W0 | W1 | W2 | W3 | W4 | W5 | W6 | W7 | W8 | W9 | W10 |
|-------|------|----|----|----|----|----|----|----|----|----|----|-----|
| P0 | 안전장치 가동 (스냅샷, SAFE_BACKUP, Fail-Fast+Degrade) | [ ] |    |    |    |    |    |    |    |    |    |     |
| P1 | SOoT 확정·정책 정렬 + 검증 2중 루프(기초) |    | [ ] |    |    |    |    |    |    |    |    |     |
| P2 | 스케줄 표준화 + 검증 2중 루프(강화) |    |    | [ ] |    |    |    |    |    |    |    |     |
| P3 | 관찰성 일원화 + Runbook Drill 시작 |    |    |    | [ ] |    |    |    |    |    |    |     |
| P4 | 레거시 Freeze→Shadow |    |    |    |    | [ ] |    |    |    |    |    |     |
| P5 | Turn-off & 위험축소 |    |    |    |    |    | [ ] |    |    |    |    |     |
| P6 | USB 품질 루프 강화 |    |    |    |    |    |    | [ ] |    |    |    |     |
| P7 | 게이트-정기 교차 검증 |    |    |    |    |    |    |    | [ ] |    |    |     |
| P8 | 리스크 드릴/롤백 훈련 |    |    |    |    |    |    |    |    | [ ] |    |     |
| P9 | 문서·Runbook 최종 확정 |    |    |    |    |    |    |    |    |    | [ ] |     |
| P10| 안정화·KPI 리뷰 |    |    |    |    |    |    |    |    |    |    | [ ] |

## 🛡️ **안전장치**

- **Fail-Fast**: 치명적 문제 시 즉시 중단
- **Graceful Degrade**: INCR 실패 → FULL 승격, RETENTION 하루 지연
- **롤백 경로**: `SAFE_BACKUP` + `rollback_backup_system.sh`
- **락 파일**: 중복 실행 차단 → 경합 확률 <0.1%

## 📁 **주요 파일 위치**

- **Windows 백업 자동화**: `ops/windows_backup/`
- **19:05 자동 요약**: `ops/summary/`
- **백업 정책**: `configs/storage_policy.yml`, `configs/retention.yml`

---

# DuRiControl System

DuRi 시스템의 중앙 제어 허브 API 서버입니다. 모든 DuRi 서비스들의 상태 모니터링, 제어, 백업, 알림 등을 관리합니다.

## 🚀 주요 기능

- **서비스 모니터링**: 모든 DuRi 서비스의 상태 실시간 모니터링
- **중앙 제어**: 서비스 시작/중지/재시작 제어
- **자동 백업**: 데이터베이스 및 설정 파일 자동 백업
- **알림 시스템**: 서비스 장애 및 리소스 임계값 알림
- **API 게이트웨이**: 통합 API 엔드포인트 제공
- **로그 관리**: 중앙화된 로그 수집 및 검색
- **리소스 모니터링**: CPU, 메모리, 디스크, 네트워크 사용량 모니터링

## 📋 시스템 요구사항

- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **메모리**: 최소 4GB (권장 8GB+)
- **디스크**: 최소 10GB 여유 공간
- **네트워크**: 포트 8080-8083 사용

## 🛠️ 빠른 시작

### 1. 저장소 클론
```bash
git clone <repository-url>
cd DuRiWorkspace
```

### 2. 환경 변수 설정
```bash
cp deploy/env.prod.example .env
# .env 파일을 편집하여 필요한 설정을 변경하세요
```

### 3. 시스템 빌드 및 시작
```bash
# 전체 시스템 빌드
./deploy/build_all.sh

# 서비스 시작 (헬스 체크 포함)
./deploy/start_services.sh --wait --health-check
```

### 4. 접속 확인
- **API 문서**: http://localhost:8083/docs
- **헬스 체크**: http://localhost:8083/health/
- **서비스 상태**: http://localhost:8083/monitor/services

## 📚 API 문서

### 인증
```bash
# 로그인
curl -X POST http://localhost:8083/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "secret"}'

# 응답에서 access_token을 받아서 사용
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8083/config/services
```

### 주요 엔드포인트

#### 헬스 체크
- `GET /health/` - 기본 헬스 체크
- `GET /health/services` - 서비스 초기화 상태
- `POST /health/services/retry` - 서비스 재시도

#### 모니터링
- `GET /monitor/services` - 모든 서비스 상태
- `GET /monitor/resources` - 시스템 리소스 사용량

#### 제어
- `GET /control/status` - 제어 시스템 상태
- `POST /control/start` - 서비스 시작
- `POST /control/stop` - 서비스 중지
- `POST /control/restart` - 서비스 재시작

#### 설정 관리
- `GET /config/services` - 등록된 서비스 목록
- `POST /config/services` - 서비스 등록
- `DELETE /config/services/{service_name}` - 서비스 제거

#### 백업 관리
- `GET /backup/list` - 백업 목록
- `POST /backup/create` - 백업 생성
- `GET /backup/download/{backup_id}` - 백업 다운로드

#### 로그 관리
- `GET /logs/search?query=<검색어>` - 로그 검색
- `GET /logs/download` - 로그 다운로드

## 🔧 관리 명령어

### 서비스 관리
```bash
# 서비스 시작
./deploy/start_services.sh

# 서비스 중지
./deploy/stop_services.sh

# 서비스 재시작
docker-compose restart duri_control

# 로그 확인
docker-compose logs -f duri_control
```

### 빌드 관리
```bash
# 전체 빌드 (캐시 정리)
./deploy/build_all.sh --clean

# 프로덕션 빌드
./deploy/build_all.sh --prod
```

### 데이터베이스 관리
```bash
# PostgreSQL 접속
docker-compose exec duri-postgres psql -U duri -d duri

# 백업 생성
docker-compose exec duri-postgres pg_dump -U duri duri > backup.sql
```

## 🏗️ 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   DuRi Control  │    │   DuRi Core     │    │  DuRi Brain     │
│   (API Server)  │◄──►│   (Core Logic)  │◄──►│  (AI Engine)    │
│   Port: 8083    │    │   Port: 8080    │    │  Port: 8081     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────►│  DuRi Evolution │◄─────────────┘
                        │  (Learning)     │
                        │  Port: 8082     │
                        └─────────────────┘
                                │
         ┌──────────────────────┼──────────────────────┐
         │                      │                      │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │     Redis       │    │   Log Files     │
│   (Database)    │    │   (Cache)       │    │   (Storage)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔒 보안

### 기본 보안 설정
- JWT 기반 인증
- HTTPS 권장 (프로덕션)
- 환경 변수를 통한 민감 정보 관리
- CORS 설정으로 허용된 도메인만 접근

### 프로덕션 보안 체크리스트
- [ ] JWT_SECRET_KEY 변경
- [ ] 관리자 비밀번호 변경
- [ ] 데이터베이스 비밀번호 변경
- [ ] HTTPS 설정
- [ ] 방화벽 설정
- [ ] 로그 레벨 조정
- [ ] 백업 암호화 설정

## 📊 모니터링

### 시스템 리소스
- CPU 사용률 모니터링
- 메모리 사용량 추적
- 디스크 공간 확인
- 네트워크 트래픽 분석

### 서비스 상태
- 각 서비스의 응답 시간 측정
- 서비스 가용성 확인
- 오류율 추적
- 자동 복구 시도

### 알림 설정
- 이메일 알림
- Slack 웹훅
- 커스텀 웹훅 지원

## 🚨 문제 해결

### 일반적인 문제들

#### 서비스가 시작되지 않음
```bash
# 로그 확인
docker-compose logs duri_control

# 서비스 상태 확인
docker-compose ps

# 데이터베이스 연결 확인
docker-compose exec duri-postgres pg_isready -U duri
```

#### API 응답이 느림
```bash
# 리소스 사용량 확인
curl http://localhost:8083/monitor/resources

# 로그 레벨 조정
# .env 파일에서 LOG_LEVEL=DEBUG로 설정
```

#### 인증 오류
```bash
# JWT 토큰 확인
curl -H "Authorization: Bearer <token>" http://localhost:8083/auth/verify

# 토큰 갱신
curl -X POST http://localhost:8083/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh_token>"}'
```

## 📈 성능 최적화

### 권장 설정
- **Worker Processes**: CPU 코어 수에 맞게 설정
- **Connection Pool**: 데이터베이스 연결 풀 크기 조정
- **Cache**: Redis 캐시 활용
- **Logging**: 로그 레벨 및 로테이션 설정

### 모니터링 지표
- API 응답 시간 < 200ms
- 데이터베이스 연결 풀 사용률 < 80%
- 메모리 사용률 < 70%
- 디스크 사용률 < 80%

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 지원

- **문서**: http://localhost:8083/docs
- **이슈**: GitHub Issues
- **이메일**: support@duri.system

## 🔄 업데이트

### 버전 히스토리
- **v1.0.0** - 초기 릴리스
  - 기본 API 서버 기능
  - 서비스 모니터링
  - 백업 시스템
  - 알림 기능

### 업데이트 방법
```bash
# 최신 코드 가져오기
git pull origin main

# 시스템 재빌드
./deploy/build_all.sh --clean

# 서비스 재시작
./deploy/start_services.sh --health-check
```

---

**DuRi Control System** - 중앙 집중식 시스템 관리의 새로운 패러다임

[![Phase-2 CI](https://github.com/duri-duri/DuRiWorkspace/actions/workflows/ci-phase2.yml/badge.svg?branch=main)](https://github.com/duri-duri/DuRiWorkspace/actions/workflows/ci-phase2.yml)

# gate
