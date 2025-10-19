#!/usr/bin/env bash
set -Eeuo pipefail

# Grafana 백업 스크립트 (ChatGPT 제안사항)
# 낮은 비용/높은 가치: grafana/data/grafana.db 일 1회 스냅샷

PROJECT_DIR="${PROJECT_DIR:-$HOME/DuRiWorkspace}"
BACKUP_DIR="$PROJECT_DIR/backups/grafana"
GRAFANA_DATA_DIR="$PROJECT_DIR/grafana/data"

cd "$PROJECT_DIR"

# 백업 디렉토리 생성
mkdir -p "$BACKUP_DIR"

# 현재 날짜로 백업 파일명 생성
BACKUP_FILE="$BACKUP_DIR/grafana_$(date +%Y%m%d_%H%M%S).db"

echo "=== Grafana 백업 시작 ==="
echo "백업 대상: $GRAFANA_DATA_DIR/grafana.db"
echo "백업 위치: $BACKUP_FILE"

# Grafana DB 파일 존재 확인
if [[ ! -f "$GRAFANA_DATA_DIR/grafana.db" ]]; then
    echo "⚠️ Grafana DB 파일이 없습니다: $GRAFANA_DATA_DIR/grafana.db"
    exit 1
fi

# 백업 실행
if cp "$GRAFANA_DATA_DIR/grafana.db" "$BACKUP_FILE"; then
    echo "✅ Grafana 백업 완료: $BACKUP_FILE"
    
    # 백업 파일 크기 확인
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "백업 파일 크기: $BACKUP_SIZE"
    
    # 오래된 백업 파일 정리 (7일 이상)
    echo "오래된 백업 파일 정리 중..."
    find "$BACKUP_DIR" -name "grafana_*.db" -mtime +7 -delete 2>/dev/null || true
    
    # 현재 백업 파일 목록
    echo "현재 백업 파일 목록:"
    ls -lh "$BACKUP_DIR"/grafana_*.db 2>/dev/null || echo "백업 파일 없음"
    
else
    echo "❌ Grafana 백업 실패"
    exit 1
fi

echo "=== Grafana 백업 완료 ==="
