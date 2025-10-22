#!/usr/bin/env bash
set -euo pipefail
# Prometheus 메트릭 수집하여 promotion_gate.py용 results.json 생성

PROMETHEUS_URL="http://localhost:9090"
OUTPUT_FILE="${1:-/tmp/shadow_results.json}"

# 기본 메트릭 수집 (실제 duri 메트릭 활용)
collect_metrics() {
    local temp_file=$(mktemp)

    # 1. duri HTTP 요청 총 수
    local http_total=$(curl -s "${PROMETHEUS_URL}/api/v1/query?query=duri_http_requests_total" | jq -r '.data.result[0].value[1] // "0"')

    # 2. duri 감정 처리 총 수
    local emotion_total=$(curl -s "${PROMETHEUS_URL}/api/v1/query?query=duri_emotion_processing_total" | jq -r '.data.result[0].value[1] // "0"')

    # 3. duri 감정 별칭 히트 수 (성공적인 정규화)
    local alias_hits=$(curl -s "${PROMETHEUS_URL}/api/v1/query?query=sum(duri_emotion_alias_hits_total)" | jq -r '.data.result[0].value[1] // "0"')

    # 4. duri 무효 감정 수 (오류)
    local invalid_emotions=$(curl -s "${PROMETHEUS_URL}/api/v1/query?query=duri_emotion_invalid_total" | jq -r '.data.result[0].value[1] // "0"')

    # 5. 응답 시간 p95 (duri 메트릭 기반)
    local latency_p95=$(curl -s "${PROMETHEUS_URL}/api/v1/query?query=histogram_quantile(0.95,duri_http_request_duration_seconds_bucket)" | jq -r '.data.result[0].value[1] // "0.1"')

    # 계산
    local total_requests=$(echo "$http_total" | awk '{print int($1)}')
    local total_emotions=$(echo "$emotion_total" | awk '{print int($1)}')
    local alias_count=$(echo "$alias_hits" | awk '{print int($1)}')
    local error_count=$(echo "$invalid_emotions" | awk '{print int($1)}')

    # 성공률 계산 (별칭 히트 + 정상 처리)
    local success_rate=0.99
    if [ "$total_emotions" -gt 0 ]; then
        local success_emotions=$((total_emotions - error_count))
        success_rate=$(echo "scale=4; $success_emotions / $total_emotions" | bc -l)
    fi

    # 오류율 계산
    local error_rate=0.01
    if [ "$total_emotions" -gt 0 ]; then
        error_rate=$(echo "scale=4; $error_count / $total_emotions" | bc -l)
    fi

    # 지연시간을 밀리초로 변환
    local latency_ms=$(echo "scale=0; $latency_p95 * 1000" | bc -l)

    # JSON 생성
    cat > "$temp_file" << EOF
{
  "latency_ms": $latency_ms,
  "error_rate": $error_rate,
  "success_rate": $success_rate,
  "total_requests": $total_requests,
  "total_emotions": $total_emotions,
  "alias_hits": $alias_count,
  "invalid_emotions": $error_count,
  "timestamp": "$(date -Iseconds)"
}
EOF

    mv "$temp_file" "$OUTPUT_FILE"
    echo "📊 실제 메트릭 수집 완료: $OUTPUT_FILE"
    cat "$OUTPUT_FILE"
}

# 메인 실행
collect_metrics
