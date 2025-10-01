#!/bin/bash
# DuRi Docker Performance Monitoring Script

set -Eeuo pipefail

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 로그 함수
log() { echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"; }
warn() { echo -e "${YELLOW}[$(date +'%H:%M:%S')] WARNING:${NC} $1"; }
error() { echo -e "${RED}[$(date +'%H:%M:%S')] ERROR:${NC} $1"; }
info() { echo -e "${BLUE}[$(date +'%H:%M:%S')] INFO:${NC} $1"; }

# 성능 메트릭 수집
collect_metrics() {
    local service=$1
    local container_name=$2

    echo -e "\n${CYAN}=== $service Performance Metrics ===${NC}"

    # CPU 사용률
    local cpu_usage=$(docker stats --no-stream --format "table {{.CPUPerc}}" $container_name 2>/dev/null | tail -n +2 | sed 's/%//')
    if [[ -n "$cpu_usage" ]]; then
        echo "CPU Usage: ${cpu_usage}%"
    fi

    # 메모리 사용량
    local mem_usage=$(docker stats --no-stream --format "table {{.MemUsage}}" $container_name 2>/dev/null | tail -n +2)
    if [[ -n "$mem_usage" ]]; then
        echo "Memory Usage: $mem_usage"
    fi

    # 네트워크 I/O
    local net_io=$(docker stats --no-stream --format "table {{.NetIO}}" $container_name 2>/dev/null | tail -n +2)
    if [[ -n "$net_io" ]]; then
        echo "Network I/O: $net_io"
    fi

    # 블록 I/O
    local block_io=$(docker stats --no-stream --format "table {{.BlockIO}}" $container_name 2>/dev/null | tail -n +2)
    if [[ -n "$block_io" ]]; then
        echo "Block I/O: $block_io"
    fi

    # 컨테이너 상태
    local status=$(docker inspect --format='{{.State.Status}}' $container_name 2>/dev/null)
    local health=$(docker inspect --format='{{.State.Health.Status}}' $container_name 2>/dev/null || echo "no-healthcheck")
    echo "Status: $status"
    echo "Health: $health"
}

# 네트워크 성능 테스트
test_network_performance() {
    echo -e "\n${CYAN}=== Network Performance Test ===${NC}"

    # 컨테이너 간 통신 테스트
    local containers=("duri_core_container" "duri_brain_container" "duri_evolution_container" "duri_control_container")

    for container in "${containers[@]}"; do
        if docker ps --format "table {{.Names}}" | grep -q "$container"; then
            echo "Testing $container connectivity..."

            # PostgreSQL 연결 테스트
            if docker exec $container pg_isready -h duri-postgres -p 5432 -U duri >/dev/null 2>&1; then
                echo "  ✓ PostgreSQL connection: OK"
            else
                echo "  ✗ PostgreSQL connection: FAILED"
            fi

            # Redis 연결 테스트
            if docker exec $container redis-cli -h duri-redis -p 6379 ping >/dev/null 2>&1; then
                echo "  ✓ Redis connection: OK"
            else
                echo "  ✗ Redis connection: FAILED"
            fi
        fi
    done
}

# 볼륨 사용량 확인
check_volume_usage() {
    echo -e "\n${CYAN}=== Volume Usage Analysis ===${NC}"

    docker system df -v | grep -E "(duri|postgres|redis|prometheus|grafana)" || true

    echo -e "\nVolume Details:"
    docker volume ls --format "table {{.Name}}\t{{.Driver}}\t{{.Size}}" | grep duri || true
}

# 이미지 크기 분석
analyze_image_sizes() {
    echo -e "\n${CYAN}=== Image Size Analysis ===${NC}"

    docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" | grep duri || true

    echo -e "\nTotal Docker System Usage:"
    docker system df
}

# 빌드 시간 측정
measure_build_time() {
    echo -e "\n${CYAN}=== Build Time Measurement ===${NC}"

    local start_time=$(date +%s)

    log "Starting optimized build..."
    ./docker/build-optimized.sh production all

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    echo "Total build time: ${duration}s"
}

# 메인 실행 함수
main() {
    local action=${1:-all}

    echo -e "${BLUE}DuRi Docker Performance Monitor${NC}"
    echo "=================================="

    case $action in
        "metrics")
            collect_metrics "Core" "duri_core_container"
            collect_metrics "Brain" "duri_brain_container"
            collect_metrics "Evolution" "duri_evolution_container"
            collect_metrics "Control" "duri_control_container"
            collect_metrics "PostgreSQL" "duri-postgres"
            collect_metrics "Redis" "duri-redis"
            ;;
        "network")
            test_network_performance
            ;;
        "volumes")
            check_volume_usage
            ;;
        "images")
            analyze_image_sizes
            ;;
        "build")
            measure_build_time
            ;;
        "all")
            collect_metrics "Core" "duri_core_container"
            collect_metrics "Brain" "duri_brain_container"
            collect_metrics "Evolution" "duri_evolution_container"
            collect_metrics "Control" "duri_control_container"
            collect_metrics "PostgreSQL" "duri-postgres"
            collect_metrics "Redis" "duri-redis"
            test_network_performance
            check_volume_usage
            analyze_image_sizes
            ;;
        *)
            echo "Usage: $0 [metrics|network|volumes|images|build|all]"
            exit 1
            ;;
    esac

    echo -e "\n${GREEN}Performance monitoring completed!${NC}"
}

# 스크립트 실행
main "$@"
