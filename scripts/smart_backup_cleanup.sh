#!/usr/bin/env bash
set -Eeuo pipefail

# ===================== 설정 =====================
ARCHIVE_DIR="/mnt/hdd/ARCHIVE"
TEMP_DIR="/tmp/smart_cleanup_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="$TEMP_DIR/cleanup.log"
TRASH_DIR="$ARCHIVE_DIR/.TRASH/smart_cleanup_$(date +%Y%m%d_%H%M%S)"

# 백업 그룹 정의 (같은 날짜 + 같은 용량) - 기존 압축 해제된 파일들 활용
BACKUP_GROUPS=(
    "2025-08-17:14G:extract_14G,extract_14G_2113"
)

# 내부 중복 파일 처리 (14G 파일 내부)
INTERNAL_DUPLICATES=(
    "/tmp/extract_14G:DuRi_Backup*20250810*.tar.gz"
    "/tmp/extract_14G:DuRi_Phase*20250806*.tar.gz"
    "/tmp/extract_14G:DuRi_Phase*20250805*.tar.gz"
)

mkdir -p "$TEMP_DIR" "$TRASH_DIR"

# ===================== 유틸리티 함수 =====================
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

get_file_size() {
    local file="$1"
    du -h "$file" | awk '{print $1}'
}

extract_archive() {
    local file="$1"
    local dest="$2"
    local filename=$(basename "$file")

    log "압축 해제: $filename → $dest"

    # 대상 디렉토리 생성
    mkdir -p "$dest"

    case "${file,,}" in
        *.tar.zst)
            zstd -dc "$file" | tar -xf - -C "$dest" || return 1
            ;;
        *.tar.gz)
            tar -xzf "$file" -C "$dest" || return 1
            ;;
        *.tar)
            tar -xf "$file" -C "$dest" || return 1
            ;;
        *)
            log "지원하지 않는 형식: $filename"
            return 1
            ;;
    esac

    return 0
}

find_differences() {
    local base_dir="$1"
    local compare_dir="$2"
    local diff_dir="$3"

    log "차이점 분석: $base_dir vs $compare_dir"

    # rsync로 차이점만 추출
    rsync -av --delete --compare-dest="$base_dir/" "$compare_dir/" "$diff_dir/" 2>/dev/null || true

    # 차이점이 있는지 확인
    local diff_count=$(find "$diff_dir" -type f 2>/dev/null | wc -l)
    echo "$diff_count"
}

create_smart_backup() {
    local diff_dir="$1"
    local output_file="$2"
    local original_hash="$3"

    log "스마트 백업 생성: $output_file"

    # 차이점만 압축
    tar -czf "$output_file" -C "$diff_dir" . || return 1

    # 원본 해시값을 메타데이터로 저장
    echo "$original_hash" > "${output_file}.meta"

    return 0
}

# ===================== 메인 처리 =====================
process_group() {
    local group="$1"
    IFS=':' read -r date size_range files <<< "$group"

    log "=== 그룹 처리 시작: $date ($size_range) ==="

    # 파일 목록 파싱
    IFS=',' read -ra file_list <<< "$files"
    local group_dir="$TEMP_DIR/group_${date}_${size_range//./_}"
    mkdir -p "$group_dir"

    # 첫 번째 파일을 기준으로 설정
    local base_path="/tmp/${file_list[0]}"
    local base_file="${base_path}"
    local base_dir="$group_dir/base"

    # 압축 파일인지 디렉토리인지 확인
    if [[ -f "$base_file" ]]; then
        local base_hash=$(sha256sum "$base_file" | awk '{print $1}')
        log "기준 파일: $(basename "$base_file") (해시: ${base_hash:0:12})"

        # 압축 파일 압축 해제
        if ! extract_archive "$base_file" "$base_dir"; then
            log "기준 파일 압축 해제 실패"
            return 1
        fi
    elif [[ -d "$base_path" ]]; then
        log "기준 디렉토리: $(basename "$base_path")"

        # 디렉토리 복사
        if ! cp -r "$base_path" "$base_dir"; then
            log "기준 디렉토리 복사 실패"
            return 1
        fi
    else
        log "기준 파일/디렉토리를 찾을 수 없음: $base_path"
        return 1
    fi

    local total_saved=0
    local processed_count=0

    # 나머지 파일들과 비교
    for ((i=1; i<${#file_list[@]}; i++)); do
        local compare_path="/tmp/${file_list[i]}"
        local compare_file="${compare_path}"
        local compare_dir="$group_dir/compare_$i"
        local diff_dir="$group_dir/diff_$i"

        # 압축 파일인지 디렉토리인지 확인
        if [[ -f "$compare_file" ]]; then
            log "비교 파일: $(basename "$compare_file")"

            # 압축 파일 압축 해제
            if ! extract_archive "$compare_file" "$compare_dir"; then
                log "비교 파일 압축 해제 실패: $(basename "$compare_file")"
                continue
            fi
        elif [[ -d "$compare_path" ]]; then
            log "비교 디렉토리: $(basename "$compare_path")"

            # 디렉토리 복사
            if ! cp -r "$compare_path" "$compare_dir"; then
                log "비교 디렉토리 복사 실패: $(basename "$compare_path")"
                continue
            fi
        else
            log "비교 파일/디렉토리를 찾을 수 없음: $compare_path"
            continue
        fi

        # 차이점 분석
        local diff_count=$(find_differences "$base_dir" "$compare_dir" "$diff_dir")

        if [ "$diff_count" -eq 0 ]; then
            log "완전 중복 발견: $(basename "$compare_file") → TRASH로 이동"
            mv "$compare_file" "$TRASH_DIR/"
            local file_size=$(stat -c %s "$compare_file")
            total_saved=$((total_saved + file_size))
        else
            log "차이점 발견: $diff_count 개 파일 → 스마트 백업 생성"
            local smart_file="$group_dir/smart_${file_list[i]}.tar.gz"
            local compare_hash=$(sha256sum "$compare_file" | awk '{print $1}')

            if create_smart_backup "$diff_dir" "$smart_file" "$compare_hash"; then
                mv "$compare_file" "$TRASH_DIR/"
                mv "$smart_file" "$ARCHIVE_DIR/FULL/$date/"
                mv "${smart_file}.meta" "$ARCHIVE_DIR/FULL/$date/"
                log "스마트 백업 완료: $(basename "$smart_file")"
            fi
        fi

        processed_count=$((processed_count + 1))
    done

    log "그룹 처리 완료: $processed_count 개 파일 처리, $(du -h "$TRASH_DIR" | awk '{print $1}') 절약"
}

# ===================== 내부 중복 처리 =====================
process_internal_duplicates() {
    local dir_pattern="$1"
    IFS=':' read -r dir pattern <<< "$dir_pattern"

    log "=== 내부 중복 처리: $dir/$pattern ==="

    # 해당 패턴의 파일들 찾기
    local files=($(find "$dir" -name "$pattern" -type f))

    if [ ${#files[@]} -le 1 ]; then
        log "비교할 파일이 없음: ${#files[@]}개"
        return 0
    fi

    # 첫 번째 파일을 기준으로 설정
    local base_file="${files[0]}"
    local base_hash=$(sha256sum "$base_file" | awk '{print $1}')

    log "기준 파일: $(basename "$base_file") (해시: ${base_hash:0:12})"

    local duplicates=()
    for file in "${files[@]}"; do
        if [[ "$file" != "$base_file" ]]; then
            local file_hash=$(sha256sum "$file" | awk '{print $1}')
            if [[ "$file_hash" == "$base_hash" ]]; then
                duplicates+=("$file")
                log "중복 발견: $(basename "$file")"
            fi
        fi
    done

    # 중복 파일들을 TRASH로 이동
    for dup_file in "${duplicates[@]}"; do
        local filename=$(basename "$dup_file")
        mv "$dup_file" "$TRASH_DIR/"
        log "중복 제거: $filename → TRASH"
    done

    log "내부 중복 처리 완료: ${#duplicates[@]}개 파일 제거"
}

# ===================== 실행 =====================
log "스마트 백업 정리 시작"
log "임시 디렉토리: $TEMP_DIR"
log "TRASH 디렉토리: $TRASH_DIR"

for group in "${BACKUP_GROUPS[@]}"; do
    process_group "$group"
done

for internal_dup in "${INTERNAL_DUPLICATES[@]}"; do
    process_internal_duplicates "$internal_dup"
done

log "스마트 백업 정리 완료"
log "로그 파일: $LOG_FILE"
log "TRASH 위치: $TRASH_DIR"

echo ""
echo "=== 요약 ==="
echo "처리된 그룹: ${#BACKUP_GROUPS[@]}"
echo "절약된 공간: $(du -sh "$TRASH_DIR" | awk '{print $1}')"
echo "로그: $LOG_FILE"
