#!/bin/bash
# DuRi 백업 스크립트
# 사용법: 
#   ./duri-backup.sh [description]     # 일반 백업
#   ./duri-backup.sh --important [description]  # 중요 백업 (백업백업)

set -euo pipefail

# 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKUP_DIR="/mnt/c/Users/admin/Desktop/두리백업"
TIMESTAMP=$(date +'%Y-%m-%d')
VERSION=$(git describe --tags --always 2>/dev/null || echo "unknown")

# 백업 타입 확인
if [[ "${1:-}" == "--important" ]]; then
    BACKUP_TYPE="중요백업"
    DESCRIPTION="${2:-important-backup}"
    echo "🛡️  중요 백업 (백업백업) 시작..."
else
    BACKUP_TYPE="일반백업"
    DESCRIPTION="${1:-manual-backup}"
    echo "🔄 일반 백업 시작..."
fi

# 월별 폴더 생성
MONTH_DIR="$BACKUP_DIR/$(date +'%Y-%m')"
mkdir -p "$MONTH_DIR"

# 백업 파일명 생성 (백업 타입 포함)
BACKUP_FILE="DuRi_${BACKUP_TYPE}_${TIMESTAMP}_v${VERSION}_${DESCRIPTION}.tar.gz"
BACKUP_PATH="$MONTH_DIR/$BACKUP_FILE"

echo "📁 백업 위치: $BACKUP_PATH"

# 현재 디렉토리를 프로젝트 루트로 변경
cd "$PROJECT_ROOT"

# 백업 생성 (중요 파일들만 포함, 불필요한 파일 제외)
tar --exclude='.git' \
    --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='*.log' \
    --exclude='*.tmp' \
    --exclude='.DS_Store' \
    --exclude='*.tar.gz' \
    --exclude='backup/*.tar.gz' \
    --exclude='safety_backup' \
    --exclude='.vscode' \
    --exclude='*.swp' \
    --exclude='*.swo' \
    --exclude='*.zip' \
    --exclude='backup_repository' \
    --exclude='duri_snapshots' \
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
echo "✅ ${BACKUP_TYPE} 완료: $BACKUP_FILE ($BACKUP_SIZE)"

# 백업 로그 기록
LOG_FILE="$BACKUP_DIR/backup-log.txt"
echo "$(date '+%Y-%m-%d %H:%M:%S') - [${BACKUP_TYPE}] $BACKUP_FILE ($BACKUP_SIZE) - $DESCRIPTION" >> "$LOG_FILE"

echo "📋 백업 로그: $LOG_FILE"
echo "🎯 백업 위치: $BACKUP_PATH"
