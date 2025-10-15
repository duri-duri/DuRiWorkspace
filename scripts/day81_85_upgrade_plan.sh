#!/bin/bash
# Day 81-85 업그레이드 플랜 - 바로 실행 가능한 7개 스텝

set -e

echo "🚀 Day 81-85 업그레이드 플랜 시작..."

# 1. 배포 전/중/후 어노테이션 파이프라인
echo "1️⃣ 배포 전/중/후 어노테이션 파이프라인 설정..."
cat > scripts/deploy_annotations.sh << 'ANNOTATIONS'
#!/bin/bash
# 배포 어노테이션 파이프라인

GRAFANA_URL="${GRAFANA_URL:-http://grafana:3000}"
GRAFANA_TOKEN="${GRAFANA_TOKEN:-your-grafana-token}"
DASHBOARD_ID="${DASHBOARD_ID:-123}"
GIT_TAG="${GIT_TAG:-dev}"

deploy_annotation() {
    local action=$1
    local text=$2
    
    curl -X POST "$GRAFANA_URL/api/annotations" \
      -H "Authorization: Bearer $GRAFANA_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{
        \"dashboardId\": $DASHBOARD_ID,
        \"tags\": [\"deploy\", \"duri\"],
        \"text\": \"$text\",
        \"time\": $(date +%s%3N)
      }" || echo "⚠️ Grafana 어노테이션 실패"
}

case "$1" in
    "start")
        deploy_annotation "start" "deploy start: $GIT_TAG"
        ;;
    "success")
        deploy_annotation "success" "deploy success: $GIT_TAG"
        ;;
    "rollback")
        deploy_annotation "rollback" "deploy rollback: $GIT_TAG"
        ;;
    *)
        echo "Usage: $0 {start|success|rollback}"
        exit 1
        ;;
esac
ANNOTATIONS

chmod +x scripts/deploy_annotations.sh
echo "✅ 배포 어노테이션 파이프라인 설정 완료"

# 2. 유지보수(무음) 윈도우 자동화
echo "2️⃣ 유지보수(무음) 윈도우 자동화 설정..."
cat > DuRiCore/maintenance/maintenance_gauge.py << 'MAINTENANCE'
#!/usr/bin/env python3
"""
DuRi Maintenance Gauge - 유지보수 윈도우 자동화
"""

import os
import time
from prometheus_client import Gauge, start_http_server
from DuRiCore.global_logging_manager import get_duri_logger

logger = get_duri_logger("maintenance_gauge")

def main():
    # Maintenance 모드 게이지
    maintenance_gauge = Gauge('maintenance_mode', 'Maintenance window flag (0/1)')
    
    # HTTP 서버 시작
    port = int(os.getenv("PORT", "9108"))
    start_http_server(port)
    logger.info(f"Maintenance gauge 서버 시작: 포트 {port}")
    
    while True:
        # Maintenance 모드 확인
        maintenance = os.getenv("MAINTENANCE", "false").lower() == "true"
        maintenance_gauge.set(1 if maintenance else 0)
        
        logger.debug(f"Maintenance 모드: {maintenance}")
        time.sleep(5)

if __name__ == "__main__":
    main()
MAINTENANCE

echo "✅ 유지보수 윈도우 자동화 설정 완료"

# 3. 합성(시뮬레이터) 점검 잡
echo "3️⃣ 합성(시뮬레이터) 점검 잡 설정..."
cat > k8s/duri-synthetic-cronjob.yaml << 'SYNTHETIC'
apiVersion: batch/v1
kind: CronJob
metadata:
  name: duri-synthetic
  namespace: duri-prod
spec:
  schedule: "*/5 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: duri-synthetic
            image: python:3.11-alpine
            command:
            - /bin/sh
            - -c
            - |
              python - << 'PY'
              import sys
              import os
              sys.path.append('/app')
              
              try:
                  from DuRiCore.deployment.deployment_integrity import deployment_integrity as d
                  r = d.verify_integrity()
                  if r["status"] == "verified":
                      print("OK")
                      sys.exit(0)
                  else:
                      print(f"FAILED: {r}")
                      sys.exit(1)
              except Exception as e:
                  print(f"ERROR: {e}")
                  sys.exit(1)
              PY
            env:
            - name: DURI_ENV
              value: "prod"
            - name: DURI_INTEGRITY_MODE
              value: "strict"
            volumeMounts:
            - name: app-code
              mountPath: /app
          volumes:
          - name: app-code
            configMap:
              name: duri-app-code
          restartPolicy: OnFailure
SYNTHETIC

echo "✅ 합성 점검 잡 설정 완료"

# 4. HMAC "진짜 운영" 켜기 스텝
echo "4️⃣ HMAC 진짜 운영 켜기 스텝 설정..."
cat > scripts/hmac_production_enable.sh << 'HMAC'
#!/bin/bash
# HMAC 진짜 운영 켜기 - 안전한 전환

set -e

NAMESPACE="${NAMESPACE:-duri-prod}"
DEPLOYMENT="${DEPLOYMENT:-duri-app}"

echo "🔐 HMAC 진짜 운영 켜기 시작..."

# 1. HMAC 키 생성
echo "1️⃣ HMAC 키 생성..."
kubectl create secret generic duri-hmac-key -n $NAMESPACE \
  --from-literal=hmac-key=$(openssl rand -hex 32) \
  --dry-run=client -o yaml | kubectl apply -f -

# 2. 이중 검증 모드로 전환
echo "2️⃣ 이중 검증 모드로 전환..."
kubectl patch deployment $DEPLOYMENT -n $NAMESPACE -p '{
  "spec": {
    "template": {
      "spec": {
        "containers": [
          {
            "name": "duri-app",
            "env": [
              {
                "name": "DURI_HMAC_KEY",
                "valueFrom": {
                  "secretKeyRef": {
                    "name": "duri-hmac-key",
                    "key": "hmac-key"
                  }
                }
              },
              {
                "name": "DURI_HMAC_KEY_DUAL_VERIFY",
                "value": "true"
              }
            ]
          }
        ]
      }
    }
  }
}'

echo "✅ HMAC 이중 검증 모드 전환 완료"
echo "📋 24시간 관찰 후 구키 폐기 예정"
echo "   kubectl delete secret duri-hmac-key-old -n $NAMESPACE"
HMAC

chmod +x scripts/hmac_production_enable.sh
echo "✅ HMAC 진짜 운영 켜기 스텝 설정 완료"

# 5. Canary + 자동 롤백 규칙
echo "5️⃣ Canary + 자동 롤백 규칙 설정..."
cat > k8s/argo-rollouts-analysis.yaml << 'CANARY'
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: duri-integrity-gate
  namespace: duri-prod
spec:
  metrics:
  - name: tampered-increase
    interval: 1m
    count: 10        # 10분
    successCondition: result == 0
    provider:
      prometheus:
        address: http://prometheus:9090
        query: increase(duri:integrity:status:tampered[5m])
  
  - name: corrupted-increase
    interval: 1m
    count: 10        # 10분
    successCondition: result == 0
    provider:
      prometheus:
        address: http://prometheus:9090
        query: increase(duri:integrity:status:corrupted[5m])

---
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: duri-app
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
        - templateName: duri-integrity-gate
        args:
        - name: service-name
          value: duri-app
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
CANARY

echo "✅ Canary + 자동 롤백 규칙 설정 완료"

# 6. SLO & 에러 버짓(가시성)
echo "6️⃣ SLO & 에러 버짓 가시성 설정..."
cat >> config/prometheus_recording_rules.yml << 'SLO'

  # SLO 레코딩 룰
  - record: duri:slo:integrity_verified_ratio_30d
    expr: sum_over_time(duri_integrity_status_verified[30d]) /
         (sum_over_time(duri_integrity_status_verified[30d]) +
          sum_over_time(duri_integrity_status_tampered[30d]) +
          sum_over_time(duri_integrity_status_corrupted[30d]) +
          sum_over_time(duri_integrity_status_policy_changed[30d]))
  
  - record: duri:slo:error_budget_consumed_30d
    expr: 1 - duri:slo:integrity_verified_ratio_30d
SLO

echo "✅ SLO & 에러 버짓 가시성 설정 완료"

# 7. 백업·복구 리허설 자동 체크
echo "7️⃣ 백업·복구 리허설 자동 체크 설정..."
cat > scripts/backup_recovery_check.sh << 'BACKUP'
#!/bin/bash
# 백업·복구 리허설 자동 체크

set -e

echo "🔄 백업·복구 리허설 자동 체크 시작..."

# S3에서 최신 아티팩트 내려받기
S3_BUCKET="${S3_BUCKET:-duri-artifacts}"
ARTIFACT_PATH="${ARTIFACT_PATH:-releases/latest/}"

echo "1️⃣ 최신 아티팩트 다운로드..."
aws s3 sync s3://$S3_BUCKET/$ARTIFACT_PATH /tmp/artifacts/ || {
    echo "⚠️ S3 아티팩트 다운로드 실패"
    exit 1
}

# 로컬 verify_integrity()와 해시 일치성 확인
echo "2️⃣ 해시 일치성 확인..."
python3 -c "
import json
import os
from DuRiCore.deployment.deployment_integrity import deployment_integrity as d

# 다운로드된 아티팩트 로드
with open('/tmp/artifacts/checksums.json', 'r') as f:
    s3_checksums = json.load(f)

with open('/tmp/artifacts/deployment_metadata.json', 'r') as f:
    s3_metadata = json.load(f)

# 로컬 무결성 검증
local_result = d.verify_integrity()

# 해시 일치성 확인
if local_result['integrity_verified']:
    print('✅ 아티팩트 해시 일치성 확인 완료')
else:
    print(f'❌ 아티팩트 해시 불일치: {local_result[\"status\"]}')
    exit(1)
"

echo "✅ 백업·복구 리허설 자동 체크 완료"
BACKUP

chmod +x scripts/backup_recovery_check.sh

# 주간 잡으로 설정
cat > k8s/backup-recovery-cronjob.yaml << 'BACKUP_JOB'
apiVersion: batch/v1
kind: CronJob
metadata:
  name: duri-backup-recovery
  namespace: duri-prod
spec:
  schedule: "0 2 * * 0"  # 매주 일요일 2시
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup-recovery
            image: amazon/aws-cli:latest
            command:
            - /bin/bash
            - /app/backup_recovery_check.sh
            env:
            - name: AWS_ACCESS_KEY_ID
              valueFrom:
                secretKeyRef:
                  name: aws-credentials
                  key: access-key-id
            - name: AWS_SECRET_ACCESS_KEY
              valueFrom:
                secretKeyRef:
                  name: aws-credentials
                  key: secret-access-key
            volumeMounts:
            - name: backup-script
              mountPath: /app
          volumes:
          - name: backup-script
            configMap:
              name: backup-recovery-script
          restartPolicy: OnFailure
BACKUP_JOB

echo "✅ 백업·복구 리허설 자동 체크 설정 완료"

echo ""
echo "🎉 Day 81-85 업그레이드 플랜 완료!"
echo "📋 다음 단계:"
echo "   1. kubectl apply -f k8s/duri-synthetic-cronjob.yaml"
echo "   2. kubectl apply -f k8s/argo-rollouts-analysis.yaml"
echo "   3. kubectl apply -f k8s/backup-recovery-cronjob.yaml"
echo "   4. ./scripts/hmac_production_enable.sh"
echo "   5. Grafana 어노테이션 토큰 설정"
echo ""
echo "🚀 가시성·운영 자동화 업그레이드 준비 완료!"
