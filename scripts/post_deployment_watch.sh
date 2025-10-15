#!/bin/bash
# 배포 직후 30분 워치 포인트

set -e

echo "📊 배포 직후 30분 워치 포인트 시작..."

# 환경변수 설정
export PROMETHEUS_URL="${PROMETHEUS_URL:-http://prometheus:9090}"
export NAMESPACE="${NAMESPACE:-duri-prod}"

# 워치 포인트 함수
watch_point() {
    local name=$1
    local query=$2
    local expected=$3
    
    echo "🔍 $name 확인..."
    result=$(curl -s "$PROMETHEUS_URL/api/v1/query?query=$query" | jq -r '.data.result[0].value[1]' 2>/dev/null || echo "null")
    
    if [ "$result" = "$expected" ]; then
        echo "✅ $name: $result (예상값: $expected)"
    else
        echo "⚠️ $name: $result (예상값: $expected)"
    fi
}

# 1. 실패 신호가 "0" 유지
echo "1️⃣ 실패 신호가 \"0\" 유지 확인..."
watch_point "Tampered 증가" "increase(duri:integrity:status:tampered[10m])" "0"
watch_point "Corrupted 증가" "increase(duri:integrity:status:corrupted[10m])" "0"

# 2. 합성 잡 성공 여부
echo "2️⃣ 합성 잡 성공 여부 확인..."
watch_point "합성 잡 스캔 시간" "last_over_time(duri_integrity_scan_duration_ms{job=\"duri-synthetic\"}[15m])" "0"

# 3. HMAC 상태
echo "3️⃣ HMAC 상태 확인..."
watch_point "HMAC 비활성화" "max_over_time(duri_integrity_hmac_status{enabled=\"false\"}[10m])" "0"

# 4. SLO 레코딩 룰
echo "4️⃣ SLO 레코딩 룰 확인..."
watch_point "SLO 무결성 비율" "duri:slo:integrity_verified_ratio_30d" "1"

# 5. 데드맨/No-Data (옵션)
echo "5️⃣ 데드맨/No-Data 확인..."
watch_point "데드맨 체크" "absent(duri_integrity_scan_duration_ms)" "0"

# 6. Pod 상태 확인
echo "6️⃣ Pod 상태 확인..."
kubectl get pods -l app=duri-app -n $NAMESPACE -o wide

# 7. 로그 확인
echo "7️⃣ 로그 확인..."
kubectl logs -l app=duri-app -c duri-integrity-sidecar -n $NAMESPACE --tail=10

# 8. 메트릭 확인
echo "8️⃣ 메트릭 확인..."
kubectl exec -it deployment/duri-app -c duri-app -n $NAMESPACE -- curl -s http://localhost:9101/metrics | grep duri_integrity_status_verified

echo ""
echo "✅ 배포 직후 30분 워치 포인트 완료!"
echo "📊 30분 후 재확인 예정"
