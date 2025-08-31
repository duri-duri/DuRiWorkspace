#!/bin/bash

# DuRi Node Sleep Script
# 인자로 시간을 주면 rtcwake로 자동 기상 예약
# 인자를 안 주면 바로 suspend 진입

set -e

# 로그 함수
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 사용법 출력
show_usage() {
    echo "사용법: $0 [기상시간]"
    echo "  기상시간: 'YYYY-MM-DD HH:MM' 형식 (예: '2025-06-29 08:40')"
    echo "  인자를 안 주면 즉시 suspend 진입"
    echo ""
    echo "예시:"
    echo "  $0                    # 즉시 suspend"
    echo "  $0 '2025-06-29 08:40' # 2025년 6월 29일 오전 8시 40분에 기상"
}

# rtcwake 명령어 확인
check_rtcwake() {
    if ! command -v rtcwake &> /dev/null; then
        log "오류: rtcwake 명령어를 찾을 수 없습니다."
        log "rtcwake는 util-linux 패키지에 포함되어 있습니다."
        log "설치: sudo apt-get install util-linux"
        exit 1
    fi
}

# 권한 확인
check_permissions() {
    if [ "$EUID" -ne 0 ]; then
        log "경고: rtcwake는 root 권한이 필요할 수 있습니다."
        log "만약 권한 오류가 발생하면 'sudo $0'로 실행하세요."
    fi
}

# 시간 파싱 및 검증
parse_wake_time() {
    local wake_time="$1"
    
    # 시간 형식 검증
    if [[ ! "$wake_time" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}[[:space:]][0-9]{2}:[0-9]{2}$ ]]; then
        log "오류: 잘못된 시간 형식입니다. 'YYYY-MM-DD HH:MM' 형식을 사용하세요."
        log "예: '2025-06-29 08:40'"
        exit 1
    fi
    
    # 날짜 유효성 검증
    local date_part=$(echo "$wake_time" | cut -d' ' -f1)
    local time_part=$(echo "$wake_time" | cut -d' ' -f2)
    
    if ! date -d "$date_part $time_part" >/dev/null 2>&1; then
        log "오류: 유효하지 않은 날짜/시간입니다: $wake_time"
        exit 1
    fi
    
    # 현재 시간과 비교
    local current_time=$(date '+%s')
    local wake_timestamp=$(date -d "$wake_time" '+%s')
    
    if [ "$wake_timestamp" -le "$current_time" ]; then
        log "오류: 기상 시간이 현재 시간보다 이전입니다: $wake_time"
        exit 1
    fi
    
    # 초 단위로 변환 (rtcwake는 초 단위 사용)
    local seconds_until_wake=$((wake_timestamp - current_time))
    
    echo "$seconds_until_wake"
}

# 시스템 정보 출력
show_system_info() {
    log "=== 시스템 정보 ==="
    log "현재 시간: $(date)"
    log "시스템: $(uname -a)"
    log "호스트명: $(hostname)"
    
    # 배터리 정보 (노트북인 경우)
    if [ -f "/sys/class/power_supply/BAT0/capacity" ]; then
        local battery_level=$(cat /sys/class/power_supply/BAT0/capacity)
        log "배터리 레벨: ${battery_level}%"
    fi
    
    # 메모리 정보
    local mem_info=$(free -h | grep Mem | awk '{print "총: " $2 ", 사용: " $3 ", 여유: " $4}')
    log "메모리: $mem_info"
    echo
}

# 즉시 suspend
suspend_now() {
    log "=== 즉시 Suspend ==="
    log "시스템을 즉시 suspend 모드로 전환합니다..."
    
    # 현재 실행 중인 서비스들 확인
    log "실행 중인 Docker 컨테이너:"
    if command -v docker &> /dev/null; then
        docker ps --format "table {{.Names}}\t{{.Status}}" 2>/dev/null || log "Docker 정보를 가져올 수 없습니다."
    else
        log "Docker가 설치되지 않았습니다."
    fi
    echo
    
    # 사용자 확인
    read -p "정말로 시스템을 suspend 하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "Suspend가 취소되었습니다."
        exit 0
    fi
    
    log "5초 후 suspend를 시작합니다..."
    sleep 5
    
    # rtcwake로 suspend (0초 = 즉시)
    log "Suspend 시작..."
    if rtcwake -s 0 -m suspend; then
        log "Suspend 완료. 시스템이 깨어났습니다."
    else
        log "오류: Suspend 중 문제가 발생했습니다."
        exit 1
    fi
}

# 예약 기상
schedule_wake() {
    local wake_time="$1"
    local seconds_until_wake="$2"
    
    log "=== 예약 기상 설정 ==="
    log "기상 시간: $wake_time"
    log "대기 시간: ${seconds_until_wake}초 ($(($seconds_until_wake / 3600))시간 $((($seconds_until_wake % 3600) / 60))분)"
    
    # 현재 실행 중인 서비스들 확인
    log "실행 중인 Docker 컨테이너:"
    if command -v docker &> /dev/null; then
        docker ps --format "table {{.Names}}\t{{.Status}}" 2>/dev/null || log "Docker 정보를 가져올 수 없습니다."
    else
        log "Docker가 설치되지 않았습니다."
    fi
    echo
    
    # 사용자 확인
    read -p "정말로 $wake_time에 기상하도록 예약하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "예약 기상이 취소되었습니다."
        exit 0
    fi
    
    log "5초 후 suspend를 시작합니다..."
    sleep 5
    
    # rtcwake로 예약 기상
    log "Suspend 시작 (예약 기상: $wake_time)..."
    if rtcwake -s "$seconds_until_wake" -m suspend; then
        log "Suspend 완료. 시스템이 $wake_time에 깨어났습니다."
    else
        log "오류: Suspend 중 문제가 발생했습니다."
        exit 1
    fi
}

# 메인 함수
main() {
    log "DuRi Node Sleep Script 시작"
    echo
    
    # 도움말 확인
    if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
        show_usage
        exit 0
    fi
    
    # 시스템 정보 출력
    show_system_info
    
    # rtcwake 확인
    check_rtcwake
    
    # 권한 확인
    check_permissions
    
    # 인자 처리
    if [ $# -eq 0 ]; then
        # 인자 없음: 즉시 suspend
        suspend_now
    elif [ $# -eq 1 ]; then
        # 인자 있음: 예약 기상
        local wake_time="$1"
        local seconds_until_wake=$(parse_wake_time "$wake_time")
        schedule_wake "$wake_time" "$seconds_until_wake"
    else
        # 잘못된 인자
        log "오류: 잘못된 인자입니다."
        show_usage
        exit 1
    fi
}

# 스크립트 실행
main "$@" 