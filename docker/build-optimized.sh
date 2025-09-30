#!/bin/bash
# DuRi Docker Build Optimization Script

set -Eeuo pipefail

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

# 환경 변수 설정
DOCKER_BUILDKIT=${DOCKER_BUILDKIT:-1}
COMPOSE_DOCKER_CLI_BUILD=${COMPOSE_DOCKER_CLI_BUILD:-1}

# 빌드 모드 설정
BUILD_MODE=${1:-production}
SERVICES=${2:-all}

log "Starting DuRi Docker build optimization..."
log "Build mode: $BUILD_MODE"
log "Services: $SERVICES"

# 공통 의존성 파일 생성
log "Creating unified requirements.txt..."
cat > requirements.txt << EOF
# Core dependencies
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
sqlalchemy>=2.0.0
alembic>=1.12.0
psycopg2-binary>=2.9.0
redis>=5.0.0
celery>=5.3.0
prometheus-client>=0.19.0
python-multipart>=0.0.6
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-dotenv>=1.0.0
httpx>=0.25.0
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.6.0
EOF

# 베이스 이미지 빌드
log "Building optimized base image..."
docker build \
    --target $BUILD_MODE \
    --tag duri-base:latest \
    --file docker/Dockerfile.base.optimized \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    .

# 서비스별 이미지 빌드
if [[ "$SERVICES" == "all" || "$SERVICES" == "core" ]]; then
    log "Building Core service..."
    docker build \
        --target production \
        --tag duri-core:latest \
        --file docker/Dockerfile.core.optimized \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        .
fi

if [[ "$SERVICES" == "all" || "$SERVICES" == "brain" ]]; then
    log "Building Brain service..."
    docker build \
        --target production \
        --tag duri-brain:latest \
        --file docker/Dockerfile.brain.optimized \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        .
fi

if [[ "$SERVICES" == "all" || "$SERVICES" == "evolution" ]]; then
    log "Building Evolution service..."
    docker build \
        --target production \
        --tag duri-evolution:latest \
        --file docker/Dockerfile.evolution.optimized \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        .
fi

if [[ "$SERVICES" == "all" || "$SERVICES" == "control" ]]; then
    log "Building Control service..."
    docker build \
        --target production \
        --tag duri-control:latest \
        --file docker/Dockerfile.control.optimized \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        .
fi

# 이미지 크기 최적화
log "Optimizing image sizes..."
docker image prune -f

# 빌드 완료
log "Docker build optimization completed!"
log "Built images:"
docker images | grep duri

# 사용법 안내
echo -e "\n${BLUE}Usage:${NC}"
echo "  ./docker/build-optimized.sh [production|development] [all|core|brain|evolution|control]"
echo ""
echo "Examples:"
echo "  ./docker/build-optimized.sh production all"
echo "  ./docker/build-optimized.sh development core"
