#!/bin/bash
# DuRi 백업백업 스크립트 (중요 백업)
# 사용법: ./duri-backup-backup.sh [description]

set -euo pipefail

# 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKUP_DIR="/mnt/c/Users/admin/Desktop/두리백업"
TIMESTAMP=$(date +'%Y-%m-%d')
VERSION=$(git describe --tags --always 2>/dev/null || echo "unknown")
DESCRIPTION="${1:-important-backup}"

# 월별 폴더 생성
MONTH_DIR="$BACKUP_DIR/$(date +'%Y-%m')"
mkdir -p "$MONTH_DIR"

# 백업 파일명 생성 (중요백업으로 표시)
BACKUP_FILE="DuRi_중요백업_${TIMESTAMP}_v${VERSION}_${DESCRIPTION}.tar.gz"
BACKUP_PATH="$MONTH_DIR/$BACKUP_FILE"

echo "🛡️  중요 백업 (백업백업) 시작..."
echo "📁 백업 위치: $BACKUP_PATH"

# 현재 디렉토리를 프로젝트 루트로 변경
cd "$PROJECT_ROOT"

# 중요 백업 생성 (더 많은 파일 포함)
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
echo "✅ 중요 백업 완료: $BACKUP_FILE ($BACKUP_SIZE)"

# 백업 로그 기록
LOG_FILE="$BACKUP_DIR/backup-log.txt"
echo "$(date '+%Y-%m-%d %H:%M:%S') - [중요백업] $BACKUP_FILE ($BACKUP_SIZE) - $DESCRIPTION" >> "$LOG_FILE"

echo "📋 백업 로그: $LOG_FILE"
echo "🎯 백업 위치: $BACKUP_PATH"
echo "🛡️  중요 백업이 완료되었습니다!"




