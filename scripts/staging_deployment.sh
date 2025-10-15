#!/bin/bash
# DuRi 스테이징 배포 스크립트 - 배포 순서 요약

set -e

echo "🚀 DuRi 스테이징 배포 시작..."

# 배포 순서 1: Secrets/AMConfig/Rules 적용 → Prom/AM reload
echo "1️⃣ Secrets/AMConfig/Rules 적용..."
kubectl apply -f k8s/alertmanager-secrets.yaml
echo "✅ Alertmanager Secret 적용 완료"

# Prometheus reload (실제 환경에서는 Prometheus Operator 사용 시)
echo "📋 Prometheus reload 명령어:"
echo "   kubectl rollout restart deployment/prometheus -n monitoring"
echo "   또는"
echo "   curl -X POST http://prometheus:9090/-/reload"

# Alertmanager reload
echo "📋 Alertmanager reload 명령어:"
echo "   kubectl rollout restart deployment/alertmanager -n monitoring"
echo "   또는"
echo "   curl -X POST http://alertmanager:9093/-/reload"

# 배포 순서 2: 대시보드 임포트 → 스모크 알람 2건 → 라우팅 OK
echo "2️⃣ 대시보드 임포트..."
echo "📋 Grafana 대시보드 임포트:"
echo "   curl -X POST http://grafana:3000/api/dashboards/db -H 'Content-Type: application/json' -d @config/grafana_dashboard_final.json"

echo "3️⃣ 스모크 알람 발사..."
# Critical 테스트 알람
curl -XPOST http://alertmanager:9093/api/v1/alerts -H 'Content-Type: application/json' -d '[
  {
    "labels": {
      "alertname": "DuRiIntegrityTampered",
      "severity": "critical",
      "service": "duri-integrity"
    },
    "annotations": {
      "summary": "Test: Integrity tampered detected",
      "description": "This is a test alert for routing verification"
    }
  }
]' || echo "⚠️ Alertmanager 연결 실패 - 수동으로 확인 필요"

# Security 테스트 알람
curl -XPOST http://alertmanager:9093/api/v1/alerts -H 'Content-Type: application/json' -d '[
  {
    "labels": {
      "alertname": "DuRiIntegrityHmacFailure",
      "severity": "security",
      "service": "duri-integrity"
    },
    "annotations": {
      "summary": "Test: HMAC signature verification failed",
      "description": "This is a test alert for security routing verification"
    }
  }
]' || echo "⚠️ Alertmanager 연결 실패 - 수동으로 확인 필요"

echo "✅ 스모크 알람 발사 완료"

# 배포 순서 3: initContainer 게이트/사이드카 확인 → 본 배포 롤아웃
echo "4️⃣ initContainer 게이트 확인..."
echo "📋 무결성 실패 테스트:"
echo "   kubectl set image deployment/duri-app duri-app=yourimage:integrity-fail -n duri-staging"
echo "   kubectl rollout status deployment/duri-app -n duri-staging --timeout=60s"
echo "   # Pod가 Ready 상태가 되지 않아야 함"

echo "5️⃣ 본 배포 롤아웃..."
kubectl set image deployment/duri-app duri-app=yourimage:latest -n duri-staging
kubectl rollout status deployment/duri-app -n duri-staging --timeout=300s
echo "✅ 배포 롤아웃 완료"

# 배포 순서 4: 15분 관찰
echo "6️⃣ 15분 관찰 시작..."
echo "📋 관찰 항목:"
echo "   - status: verified 유지"
echo "   - 실패율 패널 0"
echo "   - Scan ms 정상 (200-500ms)"
echo "   - HMAC 상태 정상"

echo "📊 모니터링 명령어:"
echo "   # 무결성 상태 확인"
echo "   kubectl exec -it deployment/duri-app -c duri-app -n duri-staging -- python -c \""
echo "   from DuRiCore.deployment.deployment_integrity import deployment_integrity"
echo "   r = deployment_integrity.verify_integrity()"
echo "   print(f'Status: {r[\\\"status\\\"]}')"
echo "   print(f'Verified: {r[\\\"integrity_verified\\\"]}')"
echo "   \""

echo "   # 메트릭 확인"
echo "   curl -s http://duri-app-service:9101/metrics | grep duri_integrity_status_verified"

echo "   # 로그 확인"
echo "   kubectl logs -l app=duri-app -c duri-integrity-sidecar -n duri-staging --tail=50"

echo ""
echo "✅ 스테이징 배포 완료!"
echo "🎯 15분 후 프로덕션 배포 진행"
echo "📊 관찰 결과가 정상이면 프로덕션 배포 명령어:"
echo "   kubectl set image deployment/duri-app duri-app=yourimage:latest -n duri-prod"
echo "   kubectl rollout status deployment/duri-app -n duri-prod --timeout=300s"
