#!/usr/bin/env bash
set -Eeuo pipefail

# H: → E: LATEST 미러링 스크립트
# 효율적인 운영방안: 기존 베이스라인 유지 + 최신본만 미러링

# 환경변수
H_ARCHIVE="/mnt/h/ARCHIVE"
E_VAULT="/mnt/e/DuRiSafe_HOSP"
LOG_DIR="$H_ARCHIVE/_logs"
TS="$(date +%Y-%m-%d__%H%M)"

# 로그 함수
log() { echo "[$(date +'%F %T')] $*" | tee -a "$LOG_DIR/latest_mirror_$(date +%F).log"; }
err() { echo "[$(date +'%F %T')] [ERR] $*" | tee -a "$LOG_DIR/latest_mirror_$(date +%F).log" >&2; }

# 사전 체크
preflight() {
    [[ -d "$H_ARCHIVE/FULL" ]] || { err "H: FULL 디렉토리 없음: $H_ARCHIVE/FULL"; exit 1; }
    [[ -d "$E_VAULT/FULL" ]] || { err "E: FULL 디렉토리 없음: $E_VAULT/FULL"; exit 1; }
    mkdir -p "$LOG_DIR"
}

# LATEST 파일 찾기 (내결함성)
find_latest() {
    local latest
    latest=$(find "$H_ARCHIVE/FULL" -name "LATEST.tar.zst" -type l 2>/dev/null | head -1)
    if [[ -n "$latest" ]]; then
        # 심링크인 경우 실제 파일 경로 확인
        latest=$(readlink -f "$latest" 2>/dev/null || echo "$latest")
    fi

    # 심링크가 깨졌거나 파일이 없으면 최신 파일 재탐색
    if [[ -z "$latest" || ! -f "$latest" ]]; then
        latest=$(find /mnt/h/ARCHIVE/FULL /mnt/hdd/ARCHIVE/FULL \
                -maxdepth 2 -type f -name '*.tar.zst' -printf '%T@ %p\n' 2>/dev/null \
                | sort -nr | awk 'NR==1{print $2}')
    fi

    [[ -n "$latest" && -f "$latest" ]] || { err "최신 FULL을 찾지 못했습니다"; exit 1; }
    echo "$latest"
}

# 미러링 실행
mirror_latest() {
    local src="$1"
    local base_name=$(basename "$src")
    local dst="$E_VAULT/FULL/${base_name}"
    local dst_sha="${dst}.sha256"

    log "미러링 시작: $src → $dst"

    # 소스 파일 무결성 확인
    if [[ -f "${src}.sha256" ]]; then
        log "소스 무결성 검증 중..."
        if ! sha256sum -c "${src}.sha256" >/dev/null 2>&1; then
            err "소스 파일 무결성 검증 실패: $src"
            return 1
        fi
        log "소스 무결성 검증 통과"
    fi

    # rsync로 안전한 복사 (재개 가능, 권한 문제 회피)
    log "파일 복사 중... (크기: $(du -h "$src" | awk '{print $1}'))"
    if rsync -avh --progress --partial --append-verify --no-perms --no-owner --no-group "$src" "$dst"; then
        log "파일 복사 완료"
    else
        err "파일 복사 실패"
        return 1
    fi

    # SHA256 파일 복사
    if [[ -f "${src}.sha256" ]]; then
        cp "${src}.sha256" "$dst_sha"
        log "SHA256 파일 복사 완료"
    else
        # SHA256 파일이 없으면 새로 생성
        log "SHA256 해시 생성 중..."
        sha256sum "$dst" > "$dst_sha"
        log "SHA256 해시 생성 완료"
    fi

    # 복사된 파일 무결성 검증
    log "복사된 파일 무결성 검증 중..."
    if sha256sum -c "$dst_sha" >/dev/null 2>&1; then
        log "복사된 파일 무결성 검증 통과"
    else
        err "복사된 파일 무결성 검증 실패: $dst"
        return 1
    fi

    # LATEST.txt 포인터 파일 생성 (심링크 대신)
    local file_name=$(basename "$dst")
    echo "$file_name" > "$(dirname "$dst")/LATEST.txt"
    log "LATEST.txt 포인터 생성: $file_name"

    log "미러링 완료: $dst"
    return 0
}

# META 인덱스 업데이트
update_meta() {
    local file="$1"
    local meta_file="$H_ARCHIVE/META/sha256_index.tsv"

    [[ -f "$meta_file" ]] || { log "META 파일 없음, 생성: $meta_file"; mkdir -p "$(dirname "$meta_file")"; touch "$meta_file"; }

    local sha=$(awk '{print $1}' "${file}.sha256" 2>/dev/null || sha256sum "$file" | awk '{print $1}')
    local size=$(stat -c%s "$file" 2>/dev/null || echo 0)
    local path="$file"

    # 중복 확인 후 추가
    if ! grep -Fq "$path" "$meta_file"; then
        printf "%s\t%s\t%s\n" "$sha" "$size" "$path" >> "$meta_file"
        log "META 인덱스 업데이트: $path"
    else
        log "META 인덱스에 이미 존재: $path"
    fi
}

# 메인 실행
main() {
    log "=== LATEST 미러링 시작 ==="

    preflight

    local latest_file
    latest_file=$(find_latest)
    log "최신 파일 발견: $latest_file"

    if mirror_latest "$latest_file"; then
        update_meta "$latest_file"
        log "=== LATEST 미러링 완료 ==="
        return 0
    else
        err "=== LATEST 미러링 실패 ==="
        return 1
    fi
}

# 실행
main "$@"
