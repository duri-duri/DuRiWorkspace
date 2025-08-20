#!/usr/bin/env bash
set -Eeuo pipefail

# 백업 파일 분석 및 변경사항 추출 스크립트
# 사용법: ./backup_analyzer.sh <백업파일1> <백업파일2> [출력디렉토리]

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
OUTPUT_DIR="${3:-./backup_changes}"

# 백업 파일 존재 확인
for file in "$BACKUP1" "$BACKUP2"; do
    if [ ! -f "$file" ]; then
        log "[ERROR] 백업 파일을 찾을 수 없습니다: $file"
        exit 1
    fi
done

# 출력 디렉토리 생성
mkdir -p "$OUTPUT_DIR"

log "백업 파일 분석 시작..."
log "기준 백업: $BACKUP1"
log "비교 백업: $BACKUP2"
log "출력 디렉토리: $OUTPUT_DIR"

# 백업 파일 내용 추출 (임시 디렉토리)
TMP_DIR1="/tmp/backup_analysis_1_$$"
TMP_DIR2="/tmp/backup_analysis_2_$$"

mkdir -p "$TMP_DIR1" "$TMP_DIR2"

# 백업 파일 압축 해제
log "백업 파일 압축 해제 중..."
tar -xf "$BACKUP1" -C "$TMP_DIR1" 2>/dev/null || log "[WARN] 첫 번째 백업 압축 해제 실패"
tar -xf "$BACKUP2" -C "$TMP_DIR2" 2>/dev/null || log "[WARN] 두 번째 백업 압축 해제 실패"

# 파일 목록 생성
log "파일 목록 생성 중..."
find "$TMP_DIR1" -type f | sort > "$OUTPUT_DIR/files_backup1.txt"
find "$TMP_DIR2" -type f | sort > "$OUTPUT_DIR/files_backup2.txt"

# 변경사항 분석
log "변경사항 분석 중..."

# 추가된 파일들
comm -13 "$OUTPUT_DIR/files_backup1.txt" "$OUTPUT_DIR/files_backup2.txt" > "$OUTPUT_DIR/added_files.txt"

# 삭제된 파일들
comm -23 "$OUTPUT_DIR/files_backup1.txt" "$OUTPUT_DIR/files_backup2.txt" > "$OUTPUT_DIR/deleted_files.txt"

# 공통 파일들 (수정 여부 확인)
comm -12 "$OUTPUT_DIR/files_backup1.txt" "$OUTPUT_DIR/files_backup2.txt" > "$OUTPUT_DIR/common_files.txt"

# 수정된 파일들 식별
log "수정된 파일 식별 중..."
MODIFIED_FILES="$OUTPUT_DIR/modified_files.txt"
> "$MODIFIED_FILES"

while IFS= read -r file; do
    rel_path="${file#$TMP_DIR1/}"
    file2="$TMP_DIR2/$rel_path"
    
    if [ -f "$file2" ]; then
        # 파일 크기 비교
        size1=$(stat -c%s "$file" 2>/dev/null || echo "0")
        size2=$(stat -c%s "$file2" 2>/dev/null || echo "0")
        
        if [ "$size1" != "$size2" ]; then
            echo "$rel_path (크기: ${size1}B → ${size2}B)" >> "$MODIFIED_FILES"
        fi
    fi
done < "$OUTPUT_DIR/common_files.txt"

# 변경사항 요약 생성
log "변경사항 요약 생성 중..."
SUMMARY_FILE="$OUTPUT_DIR/CHANGES_SUMMARY.md"

{
    echo "# 백업 변경사항 분석 결과"
    echo ""
    echo "## 분석 정보"
    echo "- **기준 백업**: $(basename "$BACKUP1")"
    echo "- **비교 백업**: $(basename "$BACKUP2")"
    echo "- **분석 시간**: $(TS)"
    echo ""
    echo "## 변경사항 통계"
    echo "- **추가된 파일**: $(wc -l < "$OUTPUT_DIR/added_files.txt")개"
    echo "- **삭제된 파일**: $(wc -l < "$OUTPUT_DIR/deleted_files.txt")개"
    echo "- **수정된 파일**: $(wc -l < "$OUTPUT_DIR/modified_files.txt")개"
    echo ""
    echo "## 상세 변경사항"
    echo ""
    echo "### 추가된 파일들"
    if [ -s "$OUTPUT_DIR/added_files.txt" ]; then
        while IFS= read -r file; do
            rel_path="${file#$TMP_DIR2/}"
            echo "+ \`$rel_path\`"
        done < "$OUTPUT_DIR/added_files.txt"
    else
        echo "(없음)"
    fi
    echo ""
    echo "### 삭제된 파일들"
    if [ -s "$OUTPUT_DIR/deleted_files.txt" ]; then
        while IFS= read -r file; do
            rel_path="${file#$TMP_DIR1/}"
            echo "- \`$rel_path\`"
        done < "$OUTPUT_DIR/deleted_files.txt"
    else
        echo "(없음)"
    fi
    echo ""
    echo "### 수정된 파일들"
    if [ -s "$OUTPUT_DIR/modified_files.txt" ]; then
        cat "$OUTPUT_DIR/modified_files.txt" | sed 's/^/* /'
    else
        echo "(없음)"
    fi
    echo ""
    echo "## 롤백 방법"
    echo "```bash"
    echo "# 기준 백업 복원"
    echo "tar -xf $(basename "$BACKUP1")"
    echo ""
    echo "# 변경사항 적용 (필요시)"
    echo "# 추가된 파일 삭제"
    echo "cat $OUTPUT_DIR/added_files.txt | xargs rm -f"
    echo ""
    echo "# 삭제된 파일 복원 (백업2에서)"
    echo "tar -xf $(basename "$BACKUP2") --wildcards \$(cat $OUTPUT_DIR/deleted_files.txt | tr '\n' ' ')"
    echo "```"
} > "$SUMMARY_FILE"

# 임시 디렉토리 정리
log "임시 디렉토리 정리 중..."
rm -rf "$TMP_DIR1" "$TMP_DIR2"

log "분석 완료!"
log "결과 파일들:"
ls -la "$OUTPUT_DIR/"
log "요약 파일: $SUMMARY_FILE"


