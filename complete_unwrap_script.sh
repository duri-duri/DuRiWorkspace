#!/usr/bin/env bash
set -Eeuo pipefail

# === 완벽한 언팩 스크립트 (중단 방지 + 모니터링 + 복구) ===
# 사용법: ./complete_unwrap_script.sh [MAX_FILES]

ROOT="${ROOT:-/mnt/h/ARCHIVE}"
OUT="${OUT:-$ROOT/.UNWRAP}"
LOG="${LOG:-$OUT/unwrap_$(date +%Y%m%d_%H%M%S).log}"
MAX_FILES="${1:-0}"  # 0=전체, n=앞에서 n개만

mkdir -p "$OUT" "$OUT/logs" "$OUT/maps"

# 로깅 함수
log(){ printf '%s [%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$1" "$2" | tee -a "$LOG"; }
hr(){ printf '%*s\n' "${COLUMNS:-80}" '' | tr ' ' - | tee -a "$LOG"; }

# 트랩 설정 (중단 시 정리)
cleanup(){
    log "WARN" "스크립트 중단됨. 정리 중..."
    # 임시 파일들 정리
    find "$OUT" -name "*.tmp.*" -type d -exec rm -rf {} + 2>/dev/null || true
    log "INFO" "정리 완료"
}
trap cleanup EXIT INT TERM

# === 1) 1GB+ 압축 파일 인덱싱 ===
ARCHIVE_LIST="$OUT/maps/archives_1G_$(date +%Y%m%d_%H%M%S).txt"
log "INFO" "1GB+ 압축 파일 스캔 시작..."

find "$ROOT" -type f -size +1G \
    -regextype posix-extended \
    -iregex '.*\.(tar\.zst|tar\.gz|tgz|tar|zip|7z)$' \
    -not -path "$ROOT/.UNWRAP/*" \
    -not -path "$ROOT/.TRASH/*" \
    -not -path "$ROOT/.QUAR_FAIL/*" \
    -printf '%s\t%p\0' | sort -z -nr > "$ARCHIVE_LIST.tmp"

# NUL 구분자를 개행으로 변환
tr '\0' '\n' < "$ARCHIVE_LIST.tmp" > "$ARCHIVE_LIST"
rm -f "$ARCHIVE_LIST.tmp"

TOTAL=$(wc -l < "$ARCHIVE_LIST")
log "INFO" "발견된 1GB+ 압축 파일: $TOTAL 개"

if [[ "$TOTAL" -eq 0 ]]; then
    log "INFO" "처리할 1GB+ 압축 파일이 없습니다."
    exit 0
fi

# MAX_FILES 제한 적용
if (( MAX_FILES > 0 )); then
    TMP_LIST="$ARCHIVE_LIST.tmp"
    head -n "$MAX_FILES" "$ARCHIVE_LIST" > "$TMP_LIST"
    mv "$TMP_LIST" "$ARCHIVE_LIST"
    TOTAL=$(wc -l < "$ARCHIVE_LIST")
    log "INFO" "제한 적용: $TOTAL 개 파일만 처리"
fi

# === 2) 언팩 함수 (안전 + 검증) ===
unpack_archive(){
    local file="$1"
    local size="$2"
    local base="$(basename "$file")"
    local name="$base"

    # 확장자 제거
    case "$base" in
        *.tar.zst) name="${base%.tar.zst}";;
        *.tar.gz)  name="${base%.tar.gz}";;
        *.tgz)     name="${base%.tgz}";;
        *.tar)     name="${base%.tar}";;
        *.zip)     name="${base%.zip}";;
        *.7z)      name="${base%.7z}";;
    esac

    local dst="$OUT/$name"
    local tmp="$dst.tmp.$$"
    local lock="$dst.lock"

    # 이미 완료된 경우 스킵
    if [[ -d "$dst" ]] && [[ -f "$dst/.unpack_complete" ]]; then
        log "SKIP" "$base (이미 완료됨)"
        return 0
    fi

    # 락 파일로 중복 실행 방지
    if [[ -f "$lock" ]]; then
        local pid=$(cat "$lock" 2>/dev/null || echo "")
        if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
            log "SKIP" "$base (다른 프로세스가 처리 중: PID $pid)"
            return 0
        fi
    fi

    echo $$ > "$lock"
    trap "rm -f '$lock'" EXIT

    log "START" "$base (${size} bytes)"
    local start_time=$(date +%s)

    # 임시 디렉토리 생성
    rm -rf "$tmp"
    mkdir -p "$tmp"

    # 언팩 명령어 결정
    local cmd=""
    if [[ "$base" =~ \.tar\.zst$ ]]; then
        cmd="tar -I zstd -xf '$file' -C '$tmp'"
    elif [[ "$base" =~ \.(tar\.gz|tgz)$ ]]; then
        cmd="tar -xzf '$file' -C '$tmp'"
    elif [[ "$base" =~ \.tar$ ]]; then
        cmd="tar -xf '$file' -C '$tmp'"
    elif [[ "$base" =~ \.zip$ ]]; then
        cmd="unzip -q '$file' -d '$tmp'"
    elif [[ "$base" =~ \.7z$ ]]; then
        cmd="7z x -y '$file' -o'$tmp'"
    else
        log "ERROR" "$base (지원하지 않는 형식)"
        rm -rf "$tmp"
        return 1
    fi

    # 언팩 실행
    if eval "$cmd" 2>&1 | tee -a "$OUT/logs/${name}.log"; then
        # 언팩 검증
        local extracted_size=$(du -sb "$tmp" | cut -f1)
        if (( extracted_size > 0 )); then
            # 기존 디렉토리 제거 후 이동
            rm -rf "$dst"
            mv "$tmp" "$dst"
            touch "$dst/.unpack_complete"

            local end_time=$(date +%s)
            local duration=$((end_time - start_time))
            log "SUCCESS" "$base -> $dst (${duration}s)"

            # 내부 압축 파일 검사
            local inner_count=$(find "$dst" -type f \( -name "*.tar.zst" -o -name "*.tar.gz" -o -name "*.zip" \) | wc -l)
            if (( inner_count > 0 )); then
                log "INFO" "$base 내부에 $inner_count 개의 추가 압축 파일 발견"
            fi
        else
            log "ERROR" "$base (언팩 결과가 비어있음)"
            rm -rf "$tmp"
            return 1
        fi
    else
        log "ERROR" "$base (언팩 실패)"
        rm -rf "$tmp"
        return 1
    fi

    rm -f "$lock"
}

# === 3) 메인 처리 루프 ===
log "INFO" "언팩 작업 시작 (총 $TOTAL 개 파일)"
hr

success_count=0
error_count=0
idx=0

while IFS=$'\t' read -r size file; do
    idx=$((idx + 1))
    log "PROGRESS" "[$idx/$TOTAL] 처리 중..."

    if unpack_archive "$file" "$size"; then
        success_count=$((success_count + 1))
    else
        error_count=$((error_count + 1))
    fi

    # 진행상황 출력
    if (( idx % 5 == 0 )); then
        log "STATUS" "진행률: $idx/$TOTAL (성공: $success_count, 실패: $error_count)"
    fi

done < "$ARCHIVE_LIST"

# === 4) 최종 요약 ===
hr
log "COMPLETE" "작업 완료!"
log "SUMMARY" "총 파일: $TOTAL, 성공: $success_count, 실패: $error_count"
log "SUMMARY" "언팩 결과 위치: $OUT"
log "SUMMARY" "로그 파일: $LOG"

# 실패한 파일 목록 출력
if (( error_count > 0 )); then
    log "WARN" "실패한 파일들:"
    find "$OUT" -name "*.log" -exec grep -l "ERROR" {} \; | while read logfile; do
        basename "$logfile" .log
    done | tee -a "$LOG"
fi

echo "완료! 결과는 $OUT 에 있습니다."
