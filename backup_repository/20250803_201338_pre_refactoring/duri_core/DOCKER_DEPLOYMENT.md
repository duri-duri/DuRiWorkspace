# DuRi Docker 배포 가이드

DuRi 시스템의 Docker 기반 배포 및 운영 가이드를 제공합니다.

## 📋 목차

- [시스템 요구사항](#시스템-요구사항)
- [빠른 시작](#빠른-시작)
- [서비스 구성](#서비스-구성)
- [환경변수 설정](#환경변수-설정)
- [배포 방법](#배포-방법)
- [API 엔드포인트](#api-엔드포인트)
- [모니터링 및 로그](#모니터링-및-로그)
- [문제 해결](#문제-해결)
- [유지보수](#유지보수)

## 🖥️ 시스템 요구사항

### 필수 요구사항
- Docker 20.10+
- Docker Compose 2.0+
- 최소 4GB RAM
- 최소 10GB 디스크 공간

### 권장 사항
- Docker 24.0+
- Docker Compose 2.20+
- 8GB+ RAM
- 20GB+ 디스크 공간
- Linux 또는 macOS

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone <repository-url>
cd duri_core
```

### 2. 환경변수 설정
```bash
# 환경변수 템플릿 복사
cp env.example .env

# 환경변수 편집 (필요한 값 수정)
nano .env
```

### 3. 전체 시스템 배포
```bash
# 실행 권한 부여
chmod +x deploy.sh
chmod +x test_docker_apis.sh

# 모든 서비스 배포
./deploy.sh all
```

### 4. 서비스 상태 확인
```bash
# 서비스 상태 확인
./deploy.sh status

# 헬스 체크
./deploy.sh health

# API 테스트
./test_docker_apis.sh all
```

## 🏗️ 서비스 구성

### 서비스 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   DuRi Core     │    │   DuRi Brain    │    │ DuRi Evolution  │
│   (Port 8080)   │◄──►│   (Port 8081)   │◄──►│   (Port 8082)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
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

### 서비스 상세 정보

| 서비스 | 포트 | 설명 | 주요 기능 |
|--------|------|------|-----------|
| **DuRi Core** | 8080 | 메인 오케스트레이션 서비스 | 전체 시스템 조율, API 게이트웨이 |
| **DuRi Brain** | 8081 | 감정 처리 및 의사결정 | 감정 분석, 의사결정, 패턴 인식 |
| **DuRi Evolution** | 8082 | 학습 및 진화 시스템 | 경험 학습, 패턴 분석, 추천 시스템 |
| **PostgreSQL** | 5432 | 관계형 데이터베이스 | 영구 데이터 저장, 스키마 관리 |
| **Redis** | 6379 | 인메모리 캐시 | 세션 저장, 캐싱, 임시 데이터 |

## ⚙️ 환경변수 설정

### 환경변수 파일 구조

```bash
# .env 파일 예시
VERSION=latest
NODE_ENV=production
LOG_LEVEL=INFO

# 포트 설정
CORE_PORT=8080
BRAIN_PORT=8081
EVOLUTION_PORT=8082
REDIS_PORT=6379
POSTGRES_PORT=5432

# API 키
BRAIN_API_KEY=your_secure_brain_api_key
EVOLUTION_API_KEY=your_secure_evolution_api_key

# 데이터베이스 설정
DATABASE_URL=postgresql://duri:duri@duri-postgres:5432/duri
POSTGRES_DB=duri
POSTGRES_USER=duri
POSTGRES_PASSWORD=your_secure_password

# Redis 설정
REDIS_URL=redis://:your_redis_password@duri-redis:6379/0
REDIS_PASSWORD=your_redis_password
```

### 주요 환경변수 설명

#### 기본 설정
- `VERSION`: 시스템 버전
- `NODE_ENV`: 실행 환경 (production/development)
- `LOG_LEVEL`: 로그 레벨 (DEBUG/INFO/WARNING/ERROR)

#### 포트 설정
- `CORE_PORT`: Core 서비스 포트 (기본값: 8080)
- `BRAIN_PORT`: Brain 서비스 포트 (기본값: 8081)
- `EVOLUTION_PORT`: Evolution 서비스 포트 (기본값: 8082)
- `REDIS_PORT`: Redis 포트 (기본값: 6379)
- `POSTGRES_PORT`: PostgreSQL 포트 (기본값: 5432)

#### 보안 설정
- `BRAIN_API_KEY`: Brain 서비스 API 키
- `EVOLUTION_API_KEY`: Evolution 서비스 API 키

#### 데이터베이스 설정
- `DATABASE_URL`: PostgreSQL 연결 URL
- `POSTGRES_DB`: 데이터베이스 이름
- `POSTGRES_USER`: 데이터베이스 사용자
- `POSTGRES_PASSWORD`: 데이터베이스 비밀번호

#### Redis 설정
- `REDIS_URL`: Redis 연결 URL
- `REDIS_PASSWORD`: Redis 비밀번호

## 🚀 배포 방법

### 전체 시스템 배포
```bash
# 모든 서비스 배포 (Core + Brain + Evolution + Redis + PostgreSQL)
./deploy.sh all
```

### 개별 서비스 배포
```bash
# Core 서비스만 배포
./deploy.sh core

# Brain 서비스만 배포
./deploy.sh brain

# Evolution 서비스만 배포
./deploy.sh evolution

# 데이터베이스 서비스만 배포
./deploy.sh db
```

### 서비스 관리
```bash
# 서비스 중지
./deploy.sh stop

# 서비스 재시작
./deploy.sh restart

# 로그 확인
./deploy.sh logs

# 실시간 로그 확인
./deploy.sh logs-follow

# 헬스 체크
./deploy.sh health

# 서비스 상태 확인
./deploy.sh status
```

### 정리 및 유지보수
```bash
# 컨테이너 및 이미지 정리
./deploy.sh clean
```

## 🔌 API 엔드포인트

### Core 서비스 (Port 8080)

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/health` | GET | 헬스 체크 |
| `/status` | GET | 서비스 상태 |
| `/session` | POST | 세션 생성 |
| `/session/{user_id}` | GET | 세션 조회 |
| `/process_emotion` | POST | 감정 처리 |
| `/evolution/cycle` | POST | 진화 사이클 실행 |

### Brain 서비스 (Port 8081)

| 엔드포인트 | 메서드 | 설명 | 인증 |
|-----------|--------|------|------|
| `/health` | GET | 헬스 체크 | ❌ |
| `/status` | GET | 서비스 상태 | ❌ |
| `/emotion/analyze` | POST | 감정 분석 | ✅ |
| `/decision/make` | POST | 의사결정 | ✅ |
| `/emotion/data` | GET | 감정 데이터 조회 | ✅ |
| `/decision/data` | GET | 의사결정 데이터 조회 | ✅ |

### Evolution 서비스 (Port 8082)

| 엔드포인트 | 메서드 | 설명 | 인증 |
|-----------|--------|------|------|
| `/health` | GET | 헬스 체크 | ❌ |
| `/status` | GET | 서비스 상태 | ❌ |
| `/session` | POST | 세션 생성 | ✅ |
| `/cycle` | POST | 진화 사이클 실행 | ✅ |
| `/action/execute` | POST | 액션 실행 | ✅ |
| `/patterns/analyze` | POST | 패턴 분석 | ✅ |
| `/insights/generate` | POST | 인사이트 생성 | ✅ |
| `/recommendations` | GET | 추천 조회 | ✅ |
| `/statistics` | GET | 통계 조회 | ✅ |
| `/experience/data` | GET | 경험 데이터 조회 | ✅ |

### API 인증

Brain 및 Evolution 서비스는 API 키 인증을 사용합니다:

```bash
# 헤더에 API 키 포함
Authorization: Bearer your_api_key_here
```

## 📊 모니터링 및 로그

### 로그 확인
```bash
# 모든 서비스 로그
./deploy.sh logs

# 실시간 로그
./deploy.sh logs-follow

# 개별 서비스 로그
docker-compose logs duri-core
docker-compose logs duri-brain
docker-compose logs duri-evolution
```

### 헬스 체크
```bash
# 전체 시스템 헬스 체크
./deploy.sh health

# 개별 서비스 헬스 체크
curl http://localhost:8080/health
curl http://localhost:8081/health
curl http://localhost:8082/health
```

### 서비스 상태 모니터링
```bash
# 컨테이너 상태 확인
docker-compose ps

# 리소스 사용량 확인
docker stats

# 볼륨 상태 확인
docker volume ls | grep duri

# 네트워크 상태 확인
docker network ls | grep duri
```

### 로그 파일 위치
- Core 서비스: `/app/logs/core.log`
- Brain 서비스: `/app/logs/brain.log`
- Evolution 서비스: `/app/logs/evolution.log`

## 🔧 문제 해결

### 일반적인 문제들

#### 1. 포트 충돌
```bash
# 포트 사용 확인
netstat -tulpn | grep :8080
netstat -tulpn | grep :8081
netstat -tulpn | grep :8082

# 환경변수에서 포트 변경
# .env 파일에서 CORE_PORT, BRAIN_PORT, EVOLUTION_PORT 수정
```

#### 2. 컨테이너 시작 실패
```bash
# 컨테이너 로그 확인
docker-compose logs duri-core
docker-compose logs duri-brain
docker-compose logs duri-evolution

# 컨테이너 재시작
docker-compose restart duri-core
```

#### 3. 데이터베이스 연결 실패
```bash
# PostgreSQL 연결 확인
docker-compose exec duri-postgres pg_isready -U duri -d duri

# Redis 연결 확인
docker-compose exec duri-redis redis-cli ping

# 환경변수 확인
cat .env | grep DATABASE_URL
cat .env | grep REDIS_URL
```

#### 4. 권한 문제
```bash
# 스크립트 실행 권한 확인
ls -la deploy.sh
ls -la test_docker_apis.sh

# 권한 부여
chmod +x deploy.sh
chmod +x test_docker_apis.sh
```

### 디버깅 명령어

```bash
# 컨테이너 내부 접속
docker-compose exec duri-core bash
docker-compose exec duri-brain bash
docker-compose exec duri-evolution bash

# 환경변수 확인
docker-compose exec duri-core env
docker-compose exec duri-brain env
docker-compose exec duri-evolution env

# 프로세스 확인
docker-compose exec duri-core ps aux
docker-compose exec duri-brain ps aux
docker-compose exec duri-evolution ps aux
```

## 🛠️ 유지보수

### 데이터 백업

#### PostgreSQL 백업
```bash
# 데이터베이스 백업
docker-compose exec duri-postgres pg_dump -U duri duri > backup_$(date +%Y%m%d_%H%M%S).sql

# 데이터베이스 복원
docker-compose exec -T duri-postgres psql -U duri duri < backup_file.sql
```

#### 볼륨 백업
```bash
# 볼륨 백업
docker run --rm -v duri_core-duri-core-data:/data -v $(pwd):/backup alpine tar czf /backup/core_data_backup.tar.gz -C /data .

# 볼륨 복원
docker run --rm -v duri_core-duri-core-data:/data -v $(pwd):/backup alpine tar xzf /backup/core_data_backup.tar.gz -C /data
```

### 업데이트

#### 시스템 업데이트
```bash
# 최신 코드 가져오기
git pull origin main

# 환경변수 확인
cp env.example .env.new
# .env.new 파일을 확인하고 필요한 값 수정

# 서비스 재배포
./deploy.sh stop
./deploy.sh all
```

#### 개별 서비스 업데이트
```bash
# 특정 서비스만 재빌드
docker-compose build duri-core
docker-compose up -d duri-core

# 또는 배포 스크립트 사용
./deploy.sh core
```

### 성능 최적화

#### 리소스 제한 설정
```yaml
# docker-compose.yml에 추가
services:
  duri-core:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
```

#### 로그 로테이션
```bash
# 로그 파일 크기 제한 및 로테이션 설정
# 각 서비스의 설정 파일에서 확인
cat config/app.json
cat brain/config/app.json
cat evolution/config/app.json
```

### 보안 강화

#### API 키 관리
```bash
# 강력한 API 키 생성
openssl rand -base64 32

# 환경변수 파일 보안
chmod 600 .env
```

#### 네트워크 보안
```bash
# 방화벽 설정 (Ubuntu/Debian)
sudo ufw allow 8080/tcp
sudo ufw allow 8081/tcp
sudo ufw allow 8082/tcp
```

## 📚 추가 리소스

### 유용한 명령어
```bash
# 전체 시스템 상태 확인
./deploy.sh status && ./deploy.sh health

# API 테스트 실행
./test_docker_apis.sh all

# 로그 실시간 모니터링
./deploy.sh logs-follow

# 시스템 정리
./deploy.sh clean
```

### 문제 보고
문제가 발생하면 다음 정보를 포함하여 보고해주세요:
- 운영체제 및 버전
- Docker 및 Docker Compose 버전
- 에러 로그
- 환경변수 설정 (민감한 정보 제외)
- 재현 단계

### 지원 및 문의
- GitHub Issues: [링크]
- 문서: [링크]
- 커뮤니티: [링크]

---

**DuRi Docker 배포 가이드** - 스스로 진화하는 AI 시스템의 Docker 배포 🐳 