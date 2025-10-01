#!/usr/bin/env bash
set -Eeuo pipefail

# USB 백업 파일 안전 분석 스크립트 (읽기 전용)
# 사용법: ./backup_analyzer_safe.sh <백업파일1> <백업파일2> [출력디렉토리]

TS() { date '+%F %T'; }
log(){ echo "[$(TS)] $*"; }

# 입력 검증
if [ $# -lt 2 ]; then
    echo "사용법: $0 <백업파일1> <백업파일2> [출력디렉토리]"
    echo "예시: $0 FULL_2025-08-19_1459.tar.zst INCR_2025-08-19_1354.tar.zst"
    exit 1
fi

BACKUP1="$1"
BACKUP2="$2"
OUTPUT_DIR="${3:-./backup_analysis_safe}"

# 백업 파일 존재 확인
for file in "$BACKUP1" "$BACKUP2"; do
    if [ ! -f "$file" ]; then
        log "[ERROR] 백업 파일을 찾을 수 없습니다: $file"
        exit 1
    fi
done

# 출력 디렉토리 생성
mkdir -p "$OUTPUT_DIR"

log "=== USB 백업 파일 안전 분석 시작 ==="
log "⚠️  주의: 읽기 전용 분석만 수행합니다"
log "기준 백업: $BACKUP1"
log "비교 백업: $BACKUP2"
log "출력 디렉토리: $OUTPUT_DIR"

# 1. 백업 파일 메타데이터 분석 (tar -t 사용)
log "1단계: 백업 파일 메타데이터 분석 중..."

# 파일 목록 추출 (압축 해제 없이)
log "기준 백업 파일 목록 추출 중..."
tar -tf "$BACKUP1" 2>/dev/null | sort > "$OUTPUT_DIR/files_backup1.txt" || log "[WARN] 첫 번째 백업 파일 목록 추출 실패"

log "비교 백업 파일 목록 추출 중..."
tar -tf "$BACKUP2" 2>/dev/null | sort > "$OUTPUT_DIR/files_backup2.txt" || log "[WARN] 두 번째 백업 파일 목록 추출 실패"

# 2. 파일 개수 및 크기 통계
log "2단계: 파일 통계 분석 중..."

COUNT1=$(wc -l < "$OUTPUT_DIR/files_backup1.txt" 2>/dev/null || echo "0")
COUNT2=$(wc -l < "$OUTPUT_DIR/files_backup2.txt" 2>/dev/null || echo "0")

SIZE1=$(du -h "$BACKUP1" | awk '{print $1}')
SIZE2=$(du -h "$BACKUP2" | awk '{print $1}')

# 3. 변경사항 분석 (파일 목록 기반)
log "3단계: 변경사항 분석 중..."

# 추가된 파일들
comm -13 "$OUTPUT_DIR/files_backup1.txt" "$OUTPUT_DIR/files_backup2.txt" > "$OUTPUT_DIR/added_files.txt" 2>/dev/null || > "$OUTPUT_DIR/added_files.txt"

# 삭제된 파일들
comm -23 "$OUTPUT_DIR/files_backup1.txt" "$OUTPUT_DIR/files_backup2.txt" > "$OUTPUT_DIR/deleted_files.txt" 2>/dev/null || > "$OUTPUT_DIR/deleted_files.txt"

# 공통 파일들
comm -12 "$OUTPUT_DIR/files_backup1.txt" "$OUTPUT_DIR/files_backup2.txt" > "$OUTPUT_DIR/common_files.txt" 2>/dev/null || > "$OUTPUT_DIR/common_files.txt"

# 4. 변경사항 요약 생성
log "4단계: 변경사항 요약 생성 중..."
SUMMARY_FILE="$OUTPUT_DIR/SAFE_ANALYSIS_SUMMARY.md"

{
    echo "# USB 백업 파일 안전 분석 결과"
    echo ""
    echo "## ⚠️  중요 주의사항"
    echo "이 분석은 **읽기 전용**으로 수행되었습니다."
    echo "USB 백업 파일은 절대 수정하거나 삭제하지 마세요!"
    echo ""
    echo "## 분석 정보"
    echo "- **기준 백업**: $(basename "$BACKUP1")"
    echo "- **비교 백업**: $(basename "$BACKUP2")"
    echo "- **분석 시간**: $(TS)"
    echo "- **분석 방식**: 읽기 전용 메타데이터 분석"
    echo ""
    echo "## 백업 파일 정보"
    echo "- **기준 백업 크기**: $SIZE1"
    echo "- **비교 백업 크기**: $SIZE2"
    echo "- **기준 백업 파일 수**: $COUNT1개"
    echo "- **비교 백업 파일 수**: $COUNT2개"
    echo ""
    echo "## 변경사항 통계"
    echo "- **추가된 파일**: $(wc -l < "$OUTPUT_DIR/added_files.txt")개"
    echo "- **삭제된 파일**: $(wc -l < "$OUTPUT_DIR/deleted_files.txt")개"
    echo "- **공통 파일**: $(wc -l < "$OUTPUT_DIR/common_files.txt")개"
    echo ""
    echo "## 상세 변경사항"
    echo ""
    echo "### 추가된 파일들"
    if [ -s "$OUTPUT_DIR/added_files.txt" ]; then
        head -20 "$OUTPUT_DIR/added_files.txt" | sed 's/^/+ /'
        if [ $(wc -l < "$OUTPUT_DIR/added_files.txt") -gt 20 ]; then
            echo "... (총 $(wc -l < "$OUTPUT_DIR/added_files.txt")개)"
        fi
    else
        echo "(없음)"
    fi
    echo ""
    echo "### 삭제된 파일들"
    if [ -s "$OUTPUT_DIR/deleted_files.txt" ]; then
        head -20 "$OUTPUT_DIR/deleted_files.txt" | sed 's/^/- /'
        if [ $(wc -l < "$OUTPUT_DIR/deleted_files.txt") -gt 20 ]; then
            echo "... (총 $(wc -l < "$OUTPUT_DIR/deleted_files.txt")개)"
        fi
    else
        echo "(없음)"
    fi
    echo ""
    echo "## 📋 분석 파일 목록"
    echo "생성된 분석 파일들:"
    echo "- \`files_backup1.txt\`: 기준 백업 파일 목록"
    echo "- \`files_backup2.txt\`: 비교 백업 파일 목록"
    echo "- \`added_files.txt\`: 추가된 파일 목록"
    echo "- \`deleted_files.txt\`: 삭제된 파일 목록"
    echo "- \`common_files.txt\`: 공통 파일 목록"
    echo ""
    echo "## 🔒 안전성 보장"
    echo "- ✅ 백업 파일 압축 해제 없음"
    echo "- ✅ 파일 내용 수정 없음"
    echo "- ✅ 읽기 전용 분석만 수행"
    echo "- ✅ USB 백업 무결성 보존"
} > "$SUMMARY_FILE"

log "✅ 안전 분석 완료!"
log "⚠️  USB 백업 파일은 절대 수정하지 마세요!"
log "결과 파일들:"
ls -la "$OUTPUT_DIR/"
log "요약 파일: $SUMMARY_FILE"
