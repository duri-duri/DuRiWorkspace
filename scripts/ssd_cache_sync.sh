#!/usr/bin/env bash
set -Eeuo pipefail

# SSD 캐시 동기화 스크립트
# H: 드라이브의 최신 백업을 I: SSD로 빠른 복구용 캐시 생성

# 환경변수
H_ARCHIVE="/mnt/h/ARCHIVE"
I_CACHE="/mnt/i/FAST_RESTORE"
LOG_DIR="$H_ARCHIVE/_logs"
TS="$(date +%Y-%m-%d__%H%M)"

# 로그 함수
log() { echo "[$(date +'%F %T')] $*" | tee -a "$LOG_DIR/ssd_cache_$(date +%F).log"; }
err() { echo "[$(date +'%F %T')] [ERR] $*" | tee -a "$LOG_DIR/ssd_cache_$(date +%F).log" >&2; }

# 사전 체크
preflight() {
    [[ -d "$H_ARCHIVE/FULL" ]] || { err "H: FULL 디렉토리 없음: $H_ARCHIVE/FULL"; exit 1; }
    [[ -d "$I_CACHE" ]] || { err "I: 캐시 디렉토리 없음: $I_CACHE"; exit 1; }
    mkdir -p "$LOG_DIR"
}

# 최신 FULL 백업 찾기
find_latest_full() {
    local latest
    latest=$(find "$H_ARCHIVE/FULL" -name "LATEST.tar.zst" -type l 2>/dev/null | head -1)
    if [[ -n "$latest" ]]; then
        latest=$(readlink -f "$latest" 2>/dev/null || echo "$latest")
    fi
    
    if [[ -z "$latest" || ! -f "$latest" ]]; then
        latest=$(find /mnt/h/ARCHIVE/FULL /mnt/hdd/ARCHIVE/FULL \
                -maxdepth 2 -type f -name 'FULL__*.tar.zst' -printf '%T@ %p\n' 2>/dev/null \
                | sort -nr | awk 'NR==1{print $2}')
    fi
    
    [[ -n "$latest" && -f "$latest" ]] || { err "최신 FULL을 찾지 못했습니다"; exit 1; }
    echo "$latest"
}

# 최신 INCR 백업 찾기
find_latest_incr() {
    local latest
    latest=$(find "$H_ARCHIVE/INCR" -name "LATEST-INCR.tar.zst" -type l 2>/dev/null | head -1)
    if [[ -n "$latest" ]]; then
        latest=$(readlink -f "$latest" 2>/dev/null || echo "$latest")
    fi
    
    if [[ -z "$latest" || ! -f "$latest" ]]; then
        latest=$(find /mnt/h/ARCHIVE/INCR /mnt/hdd/ARCHIVE/INCR \
                -maxdepth 2 -type f -name 'INCR__*.tar.zst' -printf '%T@ %p\n' 2>/dev/null \
                | sort -nr | awk 'NR==1{print $2}')
    fi
    
    [[ -n "$latest" && -f "$latest" ]] || { log "최신 INCR을 찾지 못했습니다 (선택사항)"; return 0; }
    echo "$latest"
}

# 캐시 동기화
sync_to_cache() {
    local src="$1"
    local cache_type="$2"  # FULL 또는 INCR
    local base_name=$(basename "$src")
    local dst="$I_CACHE/$cache_type/$base_name"
    
    log "캐시 동기화 시작: $src → $dst"
    
    # rsync로 안전한 복사 (재개 가능, 권한 문제 회피)
    if rsync -avh --progress --partial --append-verify --no-perms --no-owner --no-group "$src" "$dst"; then
        log "캐시 복사 완료: $cache_type"
        
        # SHA256 파일 복사
        if [[ -f "${src}.sha256" ]]; then
            cp "${src}.sha256" "${dst}.sha256"
            log "SHA256 파일 복사 완료: $cache_type"
        fi
        
        # LATEST 포인터 생성
        echo "$base_name" > "$I_CACHE/$cache_type/LATEST.txt"
        log "LATEST 포인터 생성: $cache_type → $base_name"
        
        return 0
    else
        err "캐시 복사 실패: $cache_type"
        return 1
    fi
}

# 메인 실행
main() {
    log "=== SSD 캐시 동기화 시작 ==="
    
    preflight
    
    # FULL 백업 캐시
    local latest_full
    latest_full=$(find_latest_full)
    log "최신 FULL 발견: $latest_full"
    
    if sync_to_cache "$latest_full" "FULL"; then
        log "FULL 캐시 동기화 완료"
    else
        err "FULL 캐시 동기화 실패"
        return 1
    fi
    
    # INCR 백업 캐시 (선택사항)
    local latest_incr
    latest_incr=$(find_latest_incr)
    if [[ -n "$latest_incr" ]]; then
        log "최신 INCR 발견: $latest_incr"
        if sync_to_cache "$latest_incr" "INCR"; then
            log "INCR 캐시 동기화 완료"
        else
            log "INCR 캐시 동기화 실패 (선택사항이므로 계속)"
        fi
    fi
    
    log "=== SSD 캐시 동기화 완료 ==="
    return 0
}

# 실행
main "$@"
