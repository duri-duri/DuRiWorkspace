# DuRi 무결성 사고 대응 런북

## 사고 분류

### Critical (즉시 대응)
- `tampered`: HMAC 서명 위조 감지
- `corrupted`: 파일 변조/누락 감지
- `hmac_failure`: HMAC 서명 검증 실패

### Warning (모니터링)
- `policy_changed`: 정책 변경 감지
- `scan_slow`: 스캔 지연
- `files_spike`: 파일 폭증

## 표준 대응 절차

### 1. tampered 감지 시

#### 즉시 대응 (MTTA < 5분)
```bash
# 1. 트래픽 격리
kubectl scale deployment duri-app --replicas=0

# 2. 사고 확인
kubectl logs -l app=duri-app -c duri-integrity-sidecar --tail=100

# 3. 마지막 green 배포로 자동 롤백
kubectl rollout undo deployment/duri-app

# 4. 온콜 팀 알림
curl -X POST "https://hooks.slack.com/services/your/slack/webhook" \
  -H 'Content-type: application/json' \
  --data '{"text":"🚨 CRITICAL: DuRi 무결성 위조 감지 - 자동 롤백 완료"}'
```

#### Forensic 분석 (MTTR < 2시간)
```bash
# 1. 아티팩트 수집
kubectl exec -it deployment/duri-app -c duri-app -- \
  tar -czf /tmp/forensic-$(date +%Y%m%d-%H%M%S).tar.gz \
  DuRiCore/deployment/ /var/log/

# 2. 서명 검증
kubectl exec -it deployment/duri-app -c duri-app -- \
  python -c "
from DuRiCore.deployment.deployment_integrity import deployment_integrity
r = deployment_integrity.verify_integrity()
print(f'Status: {r[\"status\"]}')
print(f'HMAC: {r[\"signatures\"]}')
"

# 3. 파일 해시 비교
kubectl exec -it deployment/duri-app -c duri-app -- \
  find . -name "*.py" -exec sha256sum {} \; > /tmp/current_hashes.txt

# 4. 로그 분석
kubectl logs -l app=duri-app --since=1h | grep -E "(tampered|corrupted|policy_changed)"
```

#### 회복 절차
```bash
# 1. 새 배포 생성
kubectl set image deployment/duri-app duri-app=yourimage:new-version

# 2. 무결성 검증 통과 확인
kubectl wait --for=condition=Ready pod -l app=duri-app --timeout=300s

# 3. 트래픽 복구
kubectl scale deployment duri-app --replicas=3

# 4. 모니터링 확인
curl -s http://duri-app-service:9101/metrics | grep duri_integrity_status_verified
```

### 2. policy_changed 감지 시

#### 경고 대응 (MTTA < 15분)
```bash
# 1. 정책 변경 확인
kubectl exec -it deployment/duri-app -c duri-app -- \
  python -c "
from DuRiCore.deployment.deployment_integrity import deployment_integrity
r = deployment_integrity.verify_integrity()
print(f'Ignore Hash: {r[\"ignore_info\"]}')
print(f'Schema Version: {r[\"schema_version\"]}')
"

# 2. duriignore.json 확인
kubectl exec -it deployment/duri-app -c duri-app -- cat duriignore.json

# 3. 환경변수 확인
kubectl exec -it deployment/duri-app -c duri-app -- env | grep DURI_INTEGRITY
```

#### 정책 동기화
```bash
# 1. 정책 파일 업데이트
kubectl create configmap duri-ignore-policy --from-file=duriignore.json

# 2. 배포 업데이트
kubectl patch deployment duri-app -p '
{
  "spec": {
    "template": {
      "spec": {
        "containers": [
          {
            "name": "duri-app",
            "volumeMounts": [
              {
                "name": "ignore-policy",
                "mountPath": "/app/duriignore.json",
                "subPath": "duriignore.json"
              }
            ]
          }
        ],
        "volumes": [
          {
            "name": "ignore-policy",
            "configMap": {
              "name": "duri-ignore-policy"
            }
          }
        ]
      }
    }
  }
}'

# 3. 재시작
kubectl rollout restart deployment/duri-app
```

### 3. scan_slow 감지 시

#### 성능 최적화
```bash
# 1. 리소스 사용량 확인
kubectl top pods -l app=duri-app

# 2. 스캔 시간 분석
kubectl exec -it deployment/duri-app -c duri-app -- \
  python -c "
from DuRiCore.deployment.deployment_integrity import deployment_integrity
r = deployment_integrity.verify_integrity()
print(f'Scan Duration: {r[\"summary\"][\"scan_duration_ms\"]}ms')
print(f'Bytes Hashed: {r[\"summary\"][\"bytes_hashed\"]}')
print(f'Total Files: {r[\"summary\"][\"total_files\"]}')
"

# 3. 리소스 증가
kubectl patch deployment duri-app -p '
{
  "spec": {
    "template": {
      "spec": {
        "containers": [
          {
            "name": "duri-integrity-sidecar",
            "resources": {
              "requests": {
                "memory": "128Mi",
                "cpu": "100m"
              },
              "limits": {
                "memory": "256Mi",
                "cpu": "200m"
              }
            }
          }
        ]
      }
    }
  }
}'
```

## 역할 분담

### 온콜 (즉시 대응)
- **MTTA**: < 5분
- **담당**: 트래픽 격리, 자동 롤백, 초기 진단
- **도구**: kubectl, Slack, PagerDuty

### 플랫폼 (인프라 복구)
- **MTTR**: < 30분
- **담당**: 리소스 조정, 배포 복구, 모니터링 확인
- **도구**: Kubernetes, Prometheus, Grafana

### 보안 (Forensic 분석)
- **MTTR**: < 2시간
- **담당**: 사고 원인 분석, 보안 강화, 정책 업데이트
- **도구**: 로그 분석, 해시 검증, 정책 관리

## 예방 조치

### 정기 점검
```bash
# 주간 무결성 검증
kubectl exec -it deployment/duri-app -c duri-app -- \
  python -c "
from DuRiCore.deployment.deployment_integrity import deployment_integrity
r = deployment_integrity.verify_integrity()
assert r['integrity_verified'], f'Integrity check failed: {r[\"status\"]}'
print('✅ Weekly integrity check passed')
"
```

### HMAC 키 회전
```bash
# 90일마다 HMAC 키 회전
kubectl create secret generic duri-hmac-key-new \
  --from-literal=hmac-key=$(openssl rand -hex 32)

# 이중 서명 모드로 전환
kubectl patch deployment duri-app -p '
{
  "spec": {
    "template": {
      "spec": {
        "containers": [
          {
            "name": "duri-app",
            "env": [
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
```

## 연락처

- **온콜**: +1-555-ONCALL
- **플랫폼**: platform-team@duri.com
- **보안**: security-team@duri.com
- **Slack**: #oncall-alerts, #security-alerts
