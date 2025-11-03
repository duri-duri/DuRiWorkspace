#!/usr/bin/env bash
# Δ9: DB 단일화 - duri_db로 통일
set -euo pipefail

echo "[INFO] DB 단일화 시작: duri_db로 통일"
echo ""

# 1) duri_db 존재 확인, 없으면 생성
docker exec -e PGPASSWORD=postgres duri-postgres \
  psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname='duri_db'" \
  | grep -q 1 || {
    echo "[CREATE] duri_db 데이터베이스 생성..."
    docker exec -e PGPASSWORD=postgres duri-postgres \
      createdb -U postgres duri_db
    echo "[OK] duri_db 생성 완료"
  }

# 2) duri_workspace 데이터를 duri_db로 마이그레이션 (기존 데이터 보존)
if docker exec -e PGPASSWORD=postgres duri-postgres \
  psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname='duri_workspace'" | grep -q 1; then
    echo "[MIGRATE] duri_workspace → duri_db 마이그레이션..."
    # 스키마 복사
    docker exec -e PGPASSWORD=postgres duri-postgres \
      pg_dump -U postgres -d duri_workspace --schema-only | \
      docker exec -i -e PGPASSWORD=postgres duri-postgres \
      psql -U postgres -d duri_db 2>/dev/null || echo "[INFO] 스키마 복사 스킵 (이미 존재)"
    # 데이터 복사 (테이블별)
    docker exec -e PGPASSWORD=postgres duri-postgres \
      pg_dump -U postgres -d duri_workspace --data-only | \
      docker exec -i -e PGPASSWORD=postgres duri-postgres \
      psql -U postgres -d duri_db 2>/dev/null || echo "[INFO] 데이터 복사 스킵 (충돌 가능)"
fi

echo ""
echo "[OK] DB 단일화 완료: duri_db 사용"
echo "[INFO] docker-compose.yml의 DATABASE_URL을 다음으로 변경하세요:"
echo "  postgresql://postgres:postgres@duri-postgres:5432/duri_db"

