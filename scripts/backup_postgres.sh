#!/bin/bash
set -euo pipefail

# Postgres 백업 스크립트
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%F_%H%M)
BACKUP_FILE="$BACKUP_DIR/duri_$TIMESTAMP.sql.gz"

echo "🔄 PostgreSQL 백업 시작..."
docker exec duriworkspace-duri-postgres-1 pg_dump -U duri -d duri | gzip > "$BACKUP_FILE"

echo "✅ 백업 완료: $BACKUP_FILE"
echo "📊 백업 크기: $(du -h "$BACKUP_FILE" | cut -f1)"

# 7일 이상 된 백업 파일 정리
find "$BACKUP_DIR" -name "duri_*.sql.gz" -mtime +7 -delete 2>/dev/null || true

echo "🧹 오래된 백업 파일 정리 완료"
