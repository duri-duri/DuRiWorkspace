#!/bin/bash
# DuRi 백업백업백업 스크립트 (완전한 DuRi2 복제)
# 사용법: ./duri-backup-backup-backup.sh [description]

set -euo pipefail

# 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKUP_DIR="/mnt/c/Users/admin/Desktop/두리백업"
TIMESTAMP=$(date +'%Y-%m-%d')
VERSION=$(git describe --tags --always 2>/dev/null || echo "unknown")
DESCRIPTION="${1:-complete-clone}"

# 월별 폴더 생성
MONTH_DIR="$BACKUP_DIR/$(date +'%Y-%m')"
mkdir -p "$MONTH_DIR"

# 백업 파일명 생성 (완전복제로 표시)
BACKUP_FILE="DuRi_완전복제_${TIMESTAMP}_v${VERSION}_${DESCRIPTION}.tar.gz"
BACKUP_PATH="$MONTH_DIR/$BACKUP_FILE"

echo "🔄 완전한 DuRi2 복제 (백업백업백업) 시작..."
echo "📁 백업 위치: $BACKUP_PATH"

# 현재 디렉토리를 프로젝트 루트로 변경
cd "$PROJECT_ROOT"

# 완전한 복제 백업 생성 (모든 중요 파일 포함)
tar --exclude='.git' \
    --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='*.log' \
    --exclude='*.tmp' \
    --exclude='.DS_Store' \
    --exclude='*.tar.gz' \
    --exclude='backup/*.tar.gz' \
    --exclude='.vscode' \
    --exclude='*.swp' \
    --exclude='*.swo' \
    --exclude='*.zip' \
    --exclude='logs' \
    --exclude='.cache' \
    --exclude='.pytest_cache' \
    --exclude='*.egg-info' \
    --exclude='dist' \
    --exclude='build' \
    --exclude='.coverage' \
    --exclude='htmlcov' \
    -czf "$BACKUP_PATH" .

# 백업 파일 크기 확인
BACKUP_SIZE=$(du -h "$BACKUP_PATH" | cut -f1)
echo "✅ 완전한 DuRi2 복제 완료: $BACKUP_FILE ($BACKUP_SIZE)"

# 복제 가이드 생성
CLONE_GUIDE="$MONTH_DIR/DuRi2_복제_가이드_${TIMESTAMP}.md"
cat > "$CLONE_GUIDE" << EOF
# DuRi2 완전 복제 가이드

## 📋 복제 정보
- **복제 시간**: $(date '+%Y-%m-%d %H:%M:%S')
- **버전**: $VERSION
- **설명**: $DESCRIPTION
- **백업 파일**: $BACKUP_FILE
- **백업 크기**: $BACKUP_SIZE

## 🚀 DuRi2 복제 방법

### 1. 백업 파일 다운로드
\`\`\`bash
# 백업 파일을 새 컴퓨터로 복사
cp "$BACKUP_FILE" /path/to/new/computer/
\`\`\`

### 2. 압축 해제
\`\`\`bash
# 새 컴퓨터에서 압축 해제
tar -xzf $BACKUP_FILE
cd DuRiWorkspace
\`\`\`

### 3. 의존성 설치
\`\`\`bash
# Python 의존성 설치
pip install -r requirements.txt

# Docker 설치 (필요시)
sudo apt-get update
sudo apt-get install docker.io docker-compose
\`\`\`

### 4. 환경 설정
\`\`\`bash
# 환경변수 설정
cp .env.example .env
# .env 파일 편집 (필요한 값 수정)
nano .env
\`\`\`

### 5. Docker 서비스 시작
\`\`\`bash
# Docker 서비스 시작
docker-compose up -d

# 또는 All-in-One 서비스 시작
docker-compose -f docker-compose.allinone.yml up -d
\`\`\`

### 6. 서비스 확인
\`\`\`bash
# 서비스 상태 확인
docker-compose ps

# API 테스트
curl http://localhost:8080/health
curl http://localhost:8081/health
curl http://localhost:8082/health
curl http://localhost:8083/health
\`\`\`

## 📊 포함된 구성요소

### ✅ 핵심 시스템
- DuRiCore (핵심 시스템)
- duri_brain (뇌 시스템)
- duri_control (제어 시스템)
- duri_evolution (진화 시스템)

### ✅ Docker 구성
- docker/ (Docker 설정 파일들)
- docker-compose.yml (기본 Docker Compose)
- docker-compose.allinone.yml (All-in-One Docker Compose)

### ✅ 설정 및 문서
- .env.example (환경변수 템플릿)
- README.md (시스템 설명서)
- CHANGELOG.md (변경 이력)
- scripts/ (유틸리티 스크립트)

### ✅ 데이터베이스
- duri_memory.db (메모리 데이터베이스)

## 🎯 복제 완료 확인

복제가 성공적으로 완료되면 다음 서비스들이 정상 작동해야 합니다:

1. **DuRi Core** (Port 8080)
2. **DuRi Brain** (Port 8081)
3. **DuRi Evolution** (Port 8082)
4. **DuRi Control** (Port 8083)

## 🔧 문제 해결

### Docker 관련 문제
\`\`\`bash
# Docker 권한 문제
sudo usermod -aG docker \$USER
newgrp docker

# Docker 서비스 재시작
sudo systemctl restart docker
\`\`\`

### 데이터베이스 연결 문제
\`\`\`bash
# PostgreSQL 컨테이너 상태 확인
docker-compose logs duri-postgres

# Redis 컨테이너 상태 확인
docker-compose logs duri-redis
\`\`\`

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. Docker 및 Docker Compose 버전
2. 시스템 리소스 (RAM, 디스크 공간)
3. 포트 충돌 여부
4. 환경변수 설정

---
**DuRi2 복제 완료! 새로운 환경에서 DuRi를 시작하세요! 🚀**
EOF

# 백업 로그 기록
LOG_FILE="$BACKUP_DIR/backup-log.txt"
echo "$(date '+%Y-%m-%d %H:%M:%S') - [완전복제] $BACKUP_FILE ($BACKUP_SIZE) - $DESCRIPTION" >> "$LOG_FILE"

echo "📋 백업 로그: $LOG_FILE"
echo "🎯 백업 위치: $BACKUP_PATH"
echo "📖 복제 가이드: $CLONE_GUIDE"
echo "🔄 완전한 DuRi2 복제가 완료되었습니다!"
echo "🚀 이제 다른 컴퓨터에서 바로 DuRi2를 시작할 수 있습니다!"




