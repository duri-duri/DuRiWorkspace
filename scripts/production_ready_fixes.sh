#!/bin/bash
# 실전 통과용 수정 스니펫 - 진짜 중요 포인트 6개

set -e

echo "🔧 실전 통과용 수정 스니펫 시작..."

# 1. 합성 잡 이미지 수정 (python:3.11-alpine)
echo "1️⃣ 합성 잡 이미지 수정..."
sed -i 's/alpine:3/python:3.11-alpine/g' k8s/duri-synthetic-cronjob.yaml
echo "✅ 합성 잡 이미지를 python:3.11-alpine으로 수정 완료"

# 2. Grafana Annotation 권한 설정
echo "2️⃣ Grafana Annotation 권한 설정..."
cat > config/grafana_annotation_setup.md << 'GRAFANA_SETUP'
# Grafana Annotation 권한 설정

## 토큰 생성
1. Grafana Admin → Configuration → Service Accounts
2. 새 Service Account 생성: "deploy-annotations"
3. 권한 부여: "Editor" 또는 "Admin"
4. 토큰 생성: "deploy-token"

## 환경변수 설정
```bash
export GRAFANA_URL="http://grafana:3000"
export GRAFANA_TOKEN="glsa_your-token-here"
export DASHBOARD_ID="123"  # DuRi 대시보드 ID
```

## CD 파이프라인 통합
```bash
# 배포 시작
./scripts/deploy_annotations.sh start

# 배포 성공
./scripts/deploy_annotations.sh success

# 배포 롤백
./scripts/deploy_annotations.sh rollback
```
GRAFANA_SETUP

echo "✅ Grafana Annotation 권한 설정 완료"

# 3. Maintenance Gauge 소스 구현
echo "3️⃣ Maintenance Gauge 소스 구현..."
cat > DuRiCore/maintenance/maintenance_exporter.py << 'MAINTENANCE_EXPORTER'
#!/usr/bin/env python3
"""
DuRi Maintenance Exporter - Maintenance Gauge 소스
"""

import os
import time
from prometheus_client import Gauge, start_http_server
from DuRiCore.global_logging_manager import get_duri_logger

logger = get_duri_logger("maintenance_exporter")

def main():
    # Maintenance 모드 게이지
    maintenance_gauge = Gauge('maintenance_mode', 'Maintenance window flag (0/1)')
    
    # HTTP 서버 시작
    port = int(os.getenv("PORT", "9108"))
    start_http_server(port)
    logger.info(f"Maintenance exporter 서버 시작: 포트 {port}")
    
    while True:
        # Maintenance 모드 확인 (ConfigMap 또는 환경변수)
        maintenance = os.getenv("MAINTENANCE", "false").lower() == "true"
        maintenance_gauge.set(1 if maintenance else 0)
        
        logger.debug(f"Maintenance 모드: {maintenance}")
        time.sleep(5)

if __name__ == "__main__":
    main()
MAINTENANCE_EXPORTER

echo "✅ Maintenance Gauge 소스 구현 완료"

# 4. Canary 게이트 조건 개선
echo "4️⃣ Canary 게이트 조건 개선..."
cat > k8s/argo-rollouts-analysis-improved.yaml << 'CANARY_IMPROVED'
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: duri-integrity-gate-improved
  namespace: duri-prod
spec:
  metrics:
  - name: tampered-increase
    interval: 1m
    count: 10        # 10분
    successCondition: result == 0
    failureCondition: result > 0
    provider:
      prometheus:
        address: http://prometheus:9090
        query: increase(duri:integrity:status:tampered[5m])
  
  - name: corrupted-increase
    interval: 1m
    count: 10        # 10분
    successCondition: result == 0
    failureCondition: result > 0
    provider:
      prometheus:
        address: http://prometheus:9090
        query: increase(duri:integrity:status:corrupted[5m])
  
  - name: policy-changed-increase
    interval: 1m
    count: 10        # 10분
    successCondition: result == 0
    failureCondition: result > 0
    provider:
      prometheus:
        address: http://prometheus:9090
        query: increase(duri:integrity:status:policy_changed[5m])

---
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: duri-app-improved
  namespace: duri-prod
spec:
  replicas: 3
  strategy:
    canary:
      steps:
      - setWeight: 10
      - pause: {duration: 5m}
      - setWeight: 50
      - pause: {duration: 5m}
      - setWeight: 100
      analysis:
        templates:
        - templateName: duri-integrity-gate-improved
        args:
        - name: service-name
          value: duri-app
        # 최소 샘플 보장
        startingStep: 2
        successCondition: "all"
        failureCondition: "any"
  selector:
    matchLabels:
      app: duri-app
  template:
    metadata:
      labels:
        app: duri-app
    spec:
      containers:
      - name: duri-app
        image: yourimage:latest
        ports:
        - containerPort: 8080
CANARY_IMPROVED

echo "✅ Canary 게이트 조건 개선 완료"

# 5. SLO 식 레코딩 룰화
echo "5️⃣ SLO 식 레코딩 룰화..."
cat > config/prometheus_slo_recording_rules.yml << 'SLO_RULES'
# SLO 레코딩 룰 - 대시보드 안정화

groups:
  - name: duri-slo-recording
    interval: 5m
    rules:
      # SLO 레코딩 룰
      - record: duri:slo:integrity_verified_ratio_30d
        expr: sum_over_time(duri_integrity_status_verified[30d]) /
             (sum_over_time(duri_integrity_status_verified[30d]) +
              sum_over_time(duri_integrity_status_tampered[30d]) +
              sum_over_time(duri_integrity_status_corrupted[30d]) +
              sum_over_time(duri_integrity_status_policy_changed[30d]))
      
      - record: duri:slo:error_budget_consumed_30d
        expr: 1 - duri:slo:integrity_verified_ratio_30d
      
      - record: duri:slo:error_budget_remaining_30d
        expr: 0.9995 - duri:slo:integrity_verified_ratio_30d
      
      # 7일 SLO (단기 모니터링)
      - record: duri:slo:integrity_verified_ratio_7d
        expr: sum_over_time(duri_integrity_status_verified[7d]) /
             (sum_over_time(duri_integrity_status_verified[7d]) +
              sum_over_time(duri_integrity_status_tampered[7d]) +
              sum_over_time(duri_integrity_status_corrupted[7d]) +
              sum_over_time(duri_integrity_status_policy_changed[7d]))
      
      - record: duri:slo:error_budget_consumed_7d
        expr: 1 - duri:slo:integrity_verified_ratio_7d
SLO_RULES

echo "✅ SLO 식 레코딩 룰화 완료"

# 6. HMAC 전환 가드 설정
echo "6️⃣ HMAC 전환 가드 설정..."
cat > config/prometheus_rules_hmac_guard.yml << 'HMAC_GUARD'
# HMAC 전환 가드 - 경보 소음 방지

groups:
  - name: duri-hmac-guard
    rules:
      # 스테이징/드릴에서만 HMAC Disabled 알람 활성화
      - alert: DuRiIntegrityHmacDisabled
        expr: duri_integrity_hmac_status{enabled="false"} == 1
        for: 5m
        labels:
          severity: warning
          service: duri-integrity
        annotations:
          summary: 'HMAC signature disabled'
          description: 'HMAC signature verification is disabled.'
          runbook_url: 'https://your.runbook/url#hmac_disabled'
        # 프로덕션 네임스페이스에서는 비활성화
        # (실제 적용 시 namespace 라벨로 조건 추가)
HMAC_GUARD

echo "✅ HMAC 전환 가드 설정 완료"

echo ""
echo "🎉 실전 통과용 수정 스니펫 완료!"
echo "📋 적용 순서:"
echo "   1. kubectl apply -f k8s/duri-synthetic-cronjob.yaml"
echo "   2. kubectl apply -f k8s/argo-rollouts-analysis-improved.yaml"
echo "   3. kubectl apply -f config/prometheus_slo_recording_rules.yml"
echo "   4. Grafana 어노테이션 토큰 설정"
echo "   5. Maintenance 사이드카 배포"
echo ""
echo "🚀 실전 통과 준비 완료!"
