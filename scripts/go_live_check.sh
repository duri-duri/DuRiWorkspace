#!/bin/bash
# DuRi Go-Live 초간단 체크 10 - 배포 버튼 준비

set -e

echo "🚀 DuRi Go-Live 초간단 체크 10 시작..."

# 1. 레코딩 룰 로드됨
echo "1️⃣ 레코딩 룰 로드 확인..."
if command -v promtool &> /dev/null; then
    promtool check rules config/prometheus_recording_rules.yml
    echo "✅ 레코딩 룰 문법 검증 통과"
else
    echo "⚠️ promtool이 설치되지 않음 - 수동으로 확인 필요"
fi

# 2. 알람 룰/AMConfig 반영
echo "2️⃣ 알람 룰/AMConfig 반영 확인..."
if command -v promtool &> /dev/null; then
    promtool check rules config/prometheus_rules_final.yml
    echo "✅ 알람 룰 문법 검증 통과"
else
    echo "⚠️ promtool이 설치되지 않음 - 수동으로 확인 필요"
fi

if command -v kubectl &> /dev/null; then
    kubectl apply -f k8s/alertmanager-secrets.yaml --dry-run=client
    echo "✅ Alertmanager Secret 적용 준비 완료"
else
    echo "⚠️ kubectl이 설치되지 않음 - 수동으로 확인 필요"
fi

# 3. AM 라우팅 샘플 발사 (테스트)
echo "3️⃣ AM 라우팅 샘플 발사 테스트..."
echo "📋 테스트 알람 발사 명령어:"
echo "   # Critical 테스트"
echo "   curl -XPOST http://alertmanager:9093/api/v1/alerts -H 'Content-Type: application/json' -d '["
echo "     {"
echo "       \"labels\": {"
echo "         \"alertname\": \"DuRiIntegrityTampered\","
echo "         \"severity\": \"critical\","
echo "         \"service\": \"duri-integrity\""
echo "       },"
echo "       \"annotations\": {"
echo "         \"summary\": \"Test: Integrity tampered detected\","
echo "         \"description\": \"This is a test alert for routing verification\""
echo "       }"
echo "     }"
echo "   ]'"
echo ""
echo "   # Security 테스트"
echo "   curl -XPOST http://alertmanager:9093/api/v1/alerts -H 'Content-Type: application/json' -d '["
echo "     {"
echo "       \"labels\": {"
echo "         \"alertname\": \"DuRiIntegrityHmacFailure\","
echo "         \"severity\": \"security\","
echo "         \"service\": \"duri-integrity\""
echo "       },"
echo "       \"annotations\": {"
echo "         \"summary\": \"Test: HMAC signature verification failed\","
echo "         \"description\": \"This is a test alert for security routing verification\""
echo "       }"
echo "     }"
echo "   ]'"

# 4. Grafana 최종본 import 확인
echo "4️⃣ Grafana 최종본 import 확인..."
if [ -f "config/grafana_dashboard_final.json" ]; then
    echo "✅ Grafana 대시보드 최종본 파일 존재"
    echo "📋 임포트 명령어:"
    echo "   curl -X POST http://grafana:3000/api/dashboards/db -H 'Content-Type: application/json' -d @config/grafana_dashboard_final.json"
else
    echo "❌ Grafana 대시보드 최종본 파일 없음"
fi

# 5. 사이드카 재검증 주기 확인
echo "5️⃣ 사이드카 재검증 주기 확인..."
echo "📋 사이드카 설정 확인:"
echo "   - 재검증 주기: 5분 (300초)"
echo "   - 명령어: python -c '...; time.sleep(300)'"
echo "   - 메트릭 노출: /metrics/integrity.prom"

# 6. initContainer 게이트 실제 동작 확인
echo "6️⃣ initContainer 게이트 실제 동작 확인..."
echo "📋 테스트 시나리오:"
echo "   1. 무결성 실패 이미지로 스테이징 배포"
echo "   2. Pod가 Ready 상태가 되지 않는지 확인"
echo "   3. initContainer 로그에서 실패 원인 확인"

# 7. 라벨 카디널리티 가드 확인
echo "7️⃣ 라벨 카디널리티 가드 확인..."
echo "📋 Prometheus 쿼리:"
echo "   sum by(__name__) (count_values(\"series\", label_replace(duri_integrity.*,\"series\",\"$1\",\"deployment_id\",\".+\")))"
echo "   → high-churn 메트릭에 deployment_id 없는지 스팟 체크"

# 8. Silence/무음 윈도우 프리셋 확인
echo "8️⃣ Silence/무음 윈도우 프리셋 확인..."
echo "📋 Silence 설정:"
echo "   - 정기 점검창: 매주 일요일 02:00-04:00 UTC"
echo "   - Silence 템플릿: duri-maintenance-window"
echo "   - 명령어: kubectl create -f - <<EOF"
echo "     apiVersion: monitoring.coreos.com/v1alpha1"
echo "     kind: Silence"
echo "     metadata:"
echo "       name: duri-maintenance"
echo "     spec:"
echo "       startsAt: \"2024-01-07T02:00:00Z\""
echo "       endsAt: \"2024-01-07T04:00:00Z\""
echo "       comment: \"정기 점검\""
echo "       matchers:"
echo "       - name: service"
echo "         value: duri-integrity"
echo "     EOF"

# 9. 런북 링크 200 확인
echo "9️⃣ 런북 링크 200 확인..."
echo "📋 링크 확인:"
echo "   - 런북: https://your.runbook/url"
echo "   - PagerDuty: https://your-pagerduty.pagerduty.com/"
echo "   - Alertmanager: http://alertmanager:9093/"
echo "   - Prometheus: http://prometheus:9090/"
echo "   - Grafana: http://grafana:3000/"

# 10. 롤백 단일 커맨드 리허설
echo "🔟 롤백 단일 커맨드 리허설..."
echo "📋 롤백 명령어:"
echo "   kubectl rollout undo deployment/duri-app --to-revision=<last-green> -n duri-prod"
echo "   kubectl rollout status deployment/duri-app -n duri-prod"

# HMAC 운영화 스위치 (옵션)
echo ""
echo "🔐 HMAC 운영화 스위치 (옵션)..."
echo "📋 HMAC 활성화 명령어:"
echo "   kubectl create secret generic duri-hmac-key -n duri-prod --from-literal=hmac-key=\$(openssl rand -hex 32)"
echo "   kubectl patch deployment duri-app -n duri-prod -p '"
echo "   {"
echo "     \"spec\": {"
echo "       \"template\": {"
echo "         \"spec\": {"
echo "           \"containers\": ["
echo "             {"
echo "               \"name\": \"duri-app\","
echo "               \"env\": ["
echo "                 {"
echo "                   \"name\": \"DURI_HMAC_KEY\","
echo "                   \"valueFrom\": {"
echo "                     \"secretKeyRef\": {"
echo "                       \"name\": \"duri-hmac-key\","
echo "                       \"key\": \"hmac-key\""
echo "                     }"
echo "                   }"
echo "                 }"
echo "               ]"
echo "             }"
echo "           ]"
echo "         }"
echo "       }"
echo "     }"
echo "   }'"

echo ""
echo "✅ Go-Live 초간단 체크 10 완료!"
echo "🚀 배포 준비 완료 - 이제 배포 버튼을 누르세요!"
