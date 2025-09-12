#!/bin/bash

# 완전 자동 압축 해제 스크립트
# 모든 폴더의 압축 파일을 빠짐없이 압축 해제

set -euo pipefail

# 설정
ARCHIVE_DIR="/mnt/h/ARCHIVE"
UNWRAP_DIR="/mnt/h/ARCHIVE/.UNWRAP"
LOG_FILE="$UNWRAP_DIR/unwrap_all_$(date +%Y%m%d_%H%M%S).log"
ERROR_LOG="$UNWRAP_DIR/errors_$(date +%Y%m%d_%H%M%S).log"
VERIFICATION_LOG="$UNWRAP_DIR/verification_$(date +%Y%m%d_%H%M%S).log"

# 폴더별 언팩 디렉토리
declare -A UNPACK_DIRS=(
    ["FULL"]="FULL_UNPACKED"
    ["CORE"]="CORE_UNPACKED"
    ["INCR"]="INCR_UNPACKED"
    ["DEV"]="DEV_UNPACKED"
    ["EXTENDED"]="EXTENDED_UNPACKED"
    ["MISC"]="MISC_UNPACKED"
)

# 압축 파일 패턴
COMPRESSION_PATTERNS=("*.tar.zst" "*.tar.gz" "*.tar.bz2" "*.tar.xz" "*.zip" "*.rar" "*.7z" "*.tar")

# 로깅 함수
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error_log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" | tee -a "$ERROR_LOG" "$LOG_FILE"
}

# 압축 해제 함수
extract_archive() {
    local archive_file="$1"
    local extract_dir="$2"
    local archive_name=$(basename "$archive_file")
    
    log "압축 해제 시작: $archive_name -> $extract_dir"
    
    # 임시 디렉토리 생성
    local temp_dir=$(mktemp -d "$extract_dir/temp_${archive_name%.*}_XXXXXX")
    
    case "${archive_file,,}" in
        *.tar.zst)
            tar -xzf "$archive_file" -C "$temp_dir" 2>&1 || {
                error_log "tar.zst 압축 해제 실패: $archive_file"
                return 1
            }
            ;;
        *.tar.gz|*.tgz)
            tar -xzf "$archive_file" -C "$temp_dir" 2>&1 || {
                error_log "tar.gz 압축 해제 실패: $archive_file"
                return 1
            }
            ;;
        *.tar.bz2)
            tar -xjf "$archive_file" -C "$temp_dir" 2>&1 || {
                error_log "tar.bz2 압축 해제 실패: $archive_file"
                return 1
            }
            ;;
        *.tar.xz)
            tar -xJf "$archive_file" -C "$temp_dir" 2>&1 || {
                error_log "tar.xz 압축 해제 실패: $archive_file"
                return 1
            }
            ;;
        *.tar)
            tar -xf "$archive_file" -C "$temp_dir" 2>&1 || {
                error_log "tar 압축 해제 실패: $archive_file"
                return 1
            }
            ;;
        *.zip)
            unzip -q "$archive_file" -d "$temp_dir" 2>&1 || {
                error_log "zip 압축 해제 실패: $archive_file"
                return 1
            }
            ;;
        *.rar)
            unrar x -y "$archive_file" "$temp_dir/" 2>&1 || {
                error_log "rar 압축 해제 실패: $archive_file"
                return 1
            }
            ;;
        *.7z)
            7z x -y "$archive_file" -o"$temp_dir" 2>&1 || {
                error_log "7z 압축 해제 실패: $archive_file"
                return 1
            }
            ;;
        *)
            error_log "지원하지 않는 압축 형식: $archive_file"
            return 1
            ;;
    esac
    
    # 성공적으로 압축 해제된 경우 최종 디렉토리로 이동
    local final_dir="$extract_dir/${archive_name%.*}"
    if [ -d "$final_dir" ]; then
        rm -rf "$final_dir"
    fi
    mv "$temp_dir" "$final_dir"
    
    log "압축 해제 완료: $archive_name -> $final_dir"
    return 0
}

# 검증 함수
verify_extraction() {
    local archive_file="$1"
    local extract_dir="$2"
    local archive_name=$(basename "$archive_file")
    local expected_dir="$extract_dir/${archive_name%.*}"
    
    if [ -d "$expected_dir" ]; then
        local file_count=$(find "$expected_dir" -type f | wc -l)
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 검증 성공: $archive_name -> $expected_dir ($file_count개 파일)" >> "$VERIFICATION_LOG"
        return 0
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 검증 실패: $archive_name -> $expected_dir (디렉토리 없음)" >> "$VERIFICATION_LOG"
        return 1
    fi
}

# 메인 실행
main() {
    log "=== 완전 자동 압축 해제 시작 ==="
    log "아카이브 디렉토리: $ARCHIVE_DIR"
    log "언팩 디렉토리: $UNWRAP_DIR"
    
    # 필요한 도구 확인
    command -v tar >/dev/null 2>&1 || { error_log "tar 명령어가 없습니다"; exit 1; }
    command -v unzip >/dev/null 2>&1 || { error_log "unzip 명령어가 없습니다"; exit 1; }
    
    # 언팩 디렉토리 생성
    for dir in "${UNPACK_DIRS[@]}"; do
        mkdir -p "$UNWRAP_DIR/$dir"
        log "언팩 디렉토리 생성: $UNWRAP_DIR/$dir"
    done
    
    # 각 폴더별 처리
    for source_folder in "${!UNPACK_DIRS[@]}"; do
        local unpack_dir="${UNPACK_DIRS[$source_folder]}"
        local source_path="$ARCHIVE_DIR/$source_folder"
        
        if [ ! -d "$source_path" ]; then
            log "소스 폴더가 없습니다: $source_path"
            continue
        fi
        
        log "=== $source_folder 폴더 처리 시작 ==="
        
        # 압축 파일 찾기
        local archive_files=()
        for pattern in "${COMPRESSION_PATTERNS[@]}"; do
            while IFS= read -r -d '' file; do
                archive_files+=("$file")
            done < <(find "$source_path" -type f -name "$pattern" -print0 2>/dev/null)
        done
        
        log "$source_folder 폴더에서 ${#archive_files[@]}개의 압축 파일 발견"
        
        # 각 압축 파일 처리
        local success_count=0
        local fail_count=0
        
        for archive_file in "${archive_files[@]}"; do
            if extract_archive "$archive_file" "$UNWRAP_DIR/$unpack_dir"; then
                ((success_count++))
                verify_extraction "$archive_file" "$UNWRAP_DIR/$unpack_dir"
            else
                ((fail_count++))
            fi
        done
        
        log "$source_folder 폴더 처리 완료: 성공 $success_count개, 실패 $fail_count개"
    done
    
    # 최종 검증
    log "=== 최종 검증 시작 ==="
    local total_archives=0
    local total_extracted=0
    
    for source_folder in "${!UNPACK_DIRS[@]}"; do
        local unpack_dir="${UNPACK_DIRS[$source_folder]}"
        local source_path="$ARCHIVE_DIR/$source_folder"
        
        # 원본 압축 파일 개수
        local archive_count=0
        for pattern in "${COMPRESSION_PATTERNS[@]}"; do
            archive_count=$((archive_count + $(find "$source_path" -type f -name "$pattern" 2>/dev/null | wc -l)))
        done
        
        # 압축 해제된 디렉토리 개수
        local extracted_count=$(find "$UNWRAP_DIR/$unpack_dir" -maxdepth 1 -type d | wc -l)
        extracted_count=$((extracted_count - 1))  # 자기 자신 제외
        
        total_archives=$((total_archives + archive_count))
        total_extracted=$((total_extracted + extracted_count))
        
        log "$source_folder: 원본 $archive_count개, 압축 해제 $extracted_count개"
    done
    
    log "=== 최종 결과 ==="
    log "총 압축 파일: $total_archives개"
    log "총 압축 해제: $total_extracted개"
    
    if [ $total_archives -eq $total_extracted ]; then
        log "🎉 모든 압축 파일이 성공적으로 압축 해제되었습니다!"
    else
        log "⚠️  일부 압축 파일 압축 해제에 실패했습니다. $ERROR_LOG를 확인하세요."
    fi
    
    log "=== 완전 자동 압축 해제 완료 ==="
}

# 스크립트 실행
main "$@"







