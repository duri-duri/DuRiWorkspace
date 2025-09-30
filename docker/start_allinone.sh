#!/bin/bash

# DuRi All-in-One Development Mode Startup Script
# 모든 DuRi 서비스를 하나의 컨테이너에서 실행

set -Eeuo pipefail

echo "🚀 DuRi All-in-One Development Mode 시작 중..."

# 환경 변수 로드
set -a; . ./.env; set +a

# 필수 환경 변수 확인
: "${POSTGRES_USER:?}"; : "${DB_HOST:?}"; : "${DB_PORT:?}"; : "${DB_NAME:?}"
[ -s secrets/db_password ] || { echo "secrets/db_password missing"; exit 1; }

# 비밀번호 URL 인코딩
DB_PASS_URL="$(python3 - <<'PY'
import sys, urllib.parse
print(urllib.parse.quote(sys.stdin.read(), safe=''))
PY
<<<"$(cat secrets/db_password)")"

# DATABASE_URL 구성
export DATABASE_URL="postgresql://${POSTGRES_USER}:${DB_PASS_URL}@${DB_HOST}:${DB_PORT}/${DB_NAME}?sslmode=disable"

# 로그 디렉토리 생성
mkdir -p /var/log/supervisor

# PostgreSQL 연결 확인
echo "📡 PostgreSQL 연결 확인 중..."
until pg_isready -h duri-postgres -p 5432 -U ${POSTGRES_USER}; do
    echo "PostgreSQL 연결 대기 중..."
    sleep 2
done
echo "✅ PostgreSQL 연결 확인됨"

# Redis 연결 확인 (Python 사용)
echo "📡 Redis 연결 확인 중..."
until python -c "import redis; r = redis.Redis(host='duri-redis', port=6379); r.ping()"; do
    echo "Redis 연결 대기 중..."
    sleep 2
done
echo "✅ Redis 연결 확인됨"

# 데이터베이스 마이그레이션 실행
echo "🗄️ 데이터베이스 마이그레이션 실행 중..."
if [ -f "/app/duri_control/database/migrations/create_analysis_tables.sql" ]; then
    PGPASSWORD="$(cat secrets/db_password)" psql -h duri-postgres -U ${POSTGRES_USER} -d ${DB_NAME} -f /app/duri_control/database/migrations/create_analysis_tables.sql
    echo "✅ 분석 테이블 마이그레이션 완료"
fi

# 환경 변수 설정
export PYTHONPATH=/app:/app/duri_common
export DURI_MODE=allinone

# Supervisor 시작
echo "🔧 Supervisor로 모든 서비스 시작 중..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf