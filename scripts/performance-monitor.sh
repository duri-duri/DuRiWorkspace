#!/bin/bash
set -Eeuo pipefail
# DuRi Performance Monitoring Script - Phase 4
# 성능 모니터링 및 튜닝 도구

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
collect_performance_metrics() {
    local service=$1
    local endpoint=$2

    echo -e "\n${CYAN}=== $service Performance Metrics ===${NC}"

    # 응답 시간 측정
    local response_time=$(curl -w "%{time_total}" -s -o /dev/null "$endpoint" 2>/dev/null || echo "N/A")
    if [[ "$response_time" != "N/A" ]]; then
        echo "Response Time: ${response_time}s"

        # 응답 시간 임계값 체크
        if (( $(echo "$response_time > 0.5" | bc -l 2>/dev/null || echo "0") )); then
            warn "Response time exceeds 500ms threshold"
        fi
    else
        error "Failed to measure response time for $service"
    fi

    # HTTP 상태 코드 확인
    local status_code=$(curl -s -o /dev/null -w "%{http_code}" "$endpoint" 2>/dev/null || echo "000")
    echo "HTTP Status: $status_code"

    if [[ "$status_code" != "200" ]]; then
        warn "Non-200 status code: $status_code"
    fi

    # 처리량 측정 (간단한 부하 테스트)
    local throughput=$(measure_throughput "$endpoint")
    echo "Throughput: ${throughput} RPS"

    if (( throughput < 50 )); then
        warn "Low throughput: ${throughput} RPS"
    fi
}

# 처리량 측정
measure_throughput() {
    local endpoint=$1
    local start_time=$(date +%s.%N)
    local success_count=0

    # 10초 동안 요청 전송
    for i in {1..10}; do
        if curl -s -o /dev/null "$endpoint" 2>/dev/null; then
            ((success_count++))
        fi
        sleep 1
    done

    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc -l)
    local throughput=$(echo "scale=2; $success_count / $duration" | bc -l)

    echo "$throughput"
}

# 리소스 사용률 모니터링
monitor_resource_usage() {
    echo -e "\n${CYAN}=== Resource Usage Monitoring ===${NC}"

    # CPU 사용률
    local cpu_usage=$(docker stats --no-stream --format "{{.CPUPerc}}" duri_core_container 2>/dev/null | sed 's/%//' || echo "N/A")
    if [[ "$cpu_usage" != "N/A" ]]; then
        echo "CPU Usage: ${cpu_usage}%"

        if (( $(echo "$cpu_usage > 80" | bc -l 2>/dev/null || echo "0") )); then
            warn "High CPU usage: ${cpu_usage}%"
        fi
    fi

    # 메모리 사용률
    local memory_usage=$(docker stats --no-stream --format "{{.MemUsage}}" duri_core_container 2>/dev/null || echo "N/A")
    echo "Memory Usage: $memory_usage"

    # 디스크 사용률
    local disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    echo "Disk Usage: ${disk_usage}%"

    if (( disk_usage > 80 )); then
        warn "High disk usage: ${disk_usage}%"
    fi
}

# 데이터베이스 성능 모니터링
monitor_database_performance() {
    echo -e "\n${CYAN}=== Database Performance Monitoring ===${NC}"

    # PostgreSQL 연결 수
    local pg_connections=$(docker exec duri-postgres psql -U duri -d duri -t -c "SELECT count(*) FROM pg_stat_activity;" 2>/dev/null | tr -d ' ' || echo "N/A")
    if [[ "$pg_connections" != "N/A" ]]; then
        echo "PostgreSQL Connections: $pg_connections"

        if (( pg_connections > 80 )); then
            warn "High PostgreSQL connection count: $pg_connections"
        fi
    fi

    # Redis 메모리 사용률
    local redis_memory=$(docker exec duri-redis redis-cli info memory | grep used_memory_human | cut -d: -f2 | tr -d '\r' || echo "N/A")
    if [[ "$redis_memory" != "N/A" ]]; then
        echo "Redis Memory Usage: $redis_memory"
    fi

    # Redis 연결 수
    local redis_connections=$(docker exec duri-redis redis-cli info clients | grep connected_clients | cut -d: -f2 | tr -d '\r' || echo "N/A")
    if [[ "$redis_connections" != "N/A" ]]; then
        echo "Redis Connections: $redis_connections"

        if (( redis_connections > 100 )); then
            warn "High Redis connection count: $redis_connections"
        fi
    fi
}

# SLO 상태 확인
check_slo_status() {
    echo -e "\n${CYAN}=== SLO Status Check ===${NC}"

    # Prometheus에서 SLO 메트릭 조회
    local prometheus_url="http://localhost:9090"

    # Core 서비스 가용성
    local core_availability=$(curl -s "$prometheus_url/api/v1/query?query=slo:core:availability:1h" | jq -r '.data.result[0].value[1]' 2>/dev/null || echo "N/A")
    if [[ "$core_availability" != "N/A" ]]; then
        local core_percentage=$(echo "$core_availability * 100" | bc -l)
        echo "Core Availability (1h): ${core_percentage}%"

        if (( $(echo "$core_percentage < 99.9" | bc -l 2>/dev/null || echo "0") )); then
            warn "Core availability below SLO target (99.9%)"
        fi
    fi

    # 응답 시간 SLO
    local response_time_slo=$(curl -s "$prometheus_url/api/v1/query?query=slo:response_time:5m" | jq -r '.data.result[0].value[1]' 2>/dev/null || echo "N/A")
    if [[ "$response_time_slo" != "N/A" ]]; then
        echo "Response Time SLO (5m): ${response_time_slo}s"

        if (( $(echo "$response_time_slo > 0.5" | bc -l 2>/dev/null || echo "0") )); then
            warn "Response time exceeds SLO target (500ms)"
        fi
    fi
}

# 성능 최적화 제안
suggest_optimizations() {
    echo -e "\n${CYAN}=== Performance Optimization Suggestions ===${NC}"

    # CPU 사용률 기반 제안
    local cpu_usage=$(docker stats --no-stream --format "{{.CPUPerc}}" duri_core_container 2>/dev/null | sed 's/%//' || echo "0")
    if (( $(echo "$cpu_usage > 70" | bc -l 2>/dev/null || echo "0") )); then
        echo "• Consider scaling up CPU resources or optimizing CPU-intensive operations"
    fi

    # 메모리 사용률 기반 제안
    local memory_percent=$(docker stats --no-stream --format "{{.MemPerc}}" duri_core_container 2>/dev/null | sed 's/%//' || echo "0")
    if (( $(echo "$memory_percent > 70" | bc -l 2>/dev/null || echo "0") )); then
        echo "• Consider increasing memory limits or optimizing memory usage"
    fi

    # 응답 시간 기반 제안
    local response_time=$(curl -w "%{time_total}" -s -o /dev/null http://localhost:8080/health 2>/dev/null || echo "0")
    if (( $(echo "$response_time > 0.3" | bc -l 2>/dev/null || echo "0") )); then
        echo "• Consider implementing caching or optimizing database queries"
    fi

    # 일반적인 최적화 제안
    echo "• Enable connection pooling for database connections"
    echo "• Implement Redis caching for frequently accessed data"
    echo "• Use async/await for I/O operations"
    echo "• Optimize Docker container resource limits"
    echo "• Consider implementing horizontal scaling"
}

# 성능 리포트 생성
generate_performance_report() {
    local report_file="performance_report_$(date +%Y%m%d_%H%M%S).txt"

    echo "DuRi Performance Report - $(date)" > "$report_file"
    echo "=================================" >> "$report_file"
    echo "" >> "$report_file"

    # 서비스별 성능 메트릭
    collect_performance_metrics "Core Service" "http://localhost:8080/health" >> "$report_file"
    collect_performance_metrics "Brain Service" "http://localhost:8081/health" >> "$report_file"
    collect_performance_metrics "Evolution Service" "http://localhost:8082/health" >> "$report_file"
    collect_performance_metrics "Control Service" "http://localhost:8083/health" >> "$report_file"

    # 리소스 사용률
    monitor_resource_usage >> "$report_file"

    # 데이터베이스 성능
    monitor_database_performance >> "$report_file"

    # SLO 상태
    check_slo_status >> "$report_file"

    log "Performance report generated: $report_file"
}

# 메인 실행 함수
main() {
    local action=${1:-all}

    echo -e "${BLUE}DuRi Performance Monitor - Phase 4${NC}"
    echo "======================================"

    case $action in
        "metrics")
            collect_performance_metrics "Core Service" "http://localhost:8080/health"
            collect_performance_metrics "Brain Service" "http://localhost:8081/health"
            collect_performance_metrics "Evolution Service" "http://localhost:8082/health"
            collect_performance_metrics "Control Service" "http://localhost:8083/health"
            ;;
        "resources")
            monitor_resource_usage
            ;;
        "database")
            monitor_database_performance
            ;;
        "slo")
            check_slo_status
            ;;
        "suggestions")
            suggest_optimizations
            ;;
        "report")
            generate_performance_report
            ;;
        "all")
            collect_performance_metrics "Core Service" "http://localhost:8080/health"
            collect_performance_metrics "Brain Service" "http://localhost:8081/health"
            collect_performance_metrics "Evolution Service" "http://localhost:8082/health"
            collect_performance_metrics "Control Service" "http://localhost:8083/health"
            monitor_resource_usage
            monitor_database_performance
            check_slo_status
            suggest_optimizations
            ;;
        *)
            echo "Usage: $0 [metrics|resources|database|slo|suggestions|report|all]"
            exit 1
            ;;
    esac

    echo -e "\n${GREEN}Performance monitoring completed!${NC}"
}

# 스크립트 실행
main "$@"
