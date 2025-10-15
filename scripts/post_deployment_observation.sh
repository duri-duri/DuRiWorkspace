#!/bin/bash
# 포스트 배포 5줄 관측 - 대시보드와 동일 쿼리

set -e

echo "📊 포스트 배포 5줄 관측 시작..."

# 환경변수 설정
export PROMETHEUS_URL="${PROMETHEUS_URL:-http://prometheus:9090}"

# 관측 함수
observe_query() {
    local name=$1
    local query=$2
    
    echo "🔍 $name 관측..."
    result=$(curl -s "$PROMETHEUS_URL/api/v1/query?query=$query" | jq -r '.data.result[0].value[1]' 2>/dev/null || echo "null")
    echo "   결과: $result"
}

# 1. 무결성 관련 모든 메트릭
echo "1️⃣ 무결성 관련 모든 메트릭 관측..."
observe_query "무결성 메트릭" "{__name__=~\"duri:integrity:.*\"}[5m]"

# 2. 실패율
echo "2️⃣ 실패율 관측..."
observe_query "실패율" "duri:integrity:failure_rate"

# 3. HMAC 상태
echo "3️⃣ HMAC 상태 관측..."
observe_query "HMAC 비활성화" "duri:integrity:hmac:status{enabled=\"false\"}"

# 4. SLO 무결성 비율
echo "4️⃣ SLO 무결성 비율 관측..."
observe_query "SLO 무결성 비율" "duri:slo:integrity_verified_ratio_30d"

# 5. Tampered 증가
echo "5️⃣ Tampered 증가 관측..."
observe_query "Tampered 증가" "increase(duri:integrity:status:tampered[5m]) > 0"

echo ""
echo "✅ 포스트 배포 5줄 관측 완료!"
echo "📊 대시보드에서 동일한 쿼리로 확인하세요"
