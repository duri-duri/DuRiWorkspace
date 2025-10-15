# DuRi 프로덕션 마무리 체크 10가지

## 1. 비밀키 운영화

### KMS/Secrets Manager 연동
```bash
# 환경변수 대신 파일 마운트 권장
DURI_HMAC_KEY_FILE=/etc/secrets/hmac-key
DURI_HMAC_KEY_ROTATION_PERIOD=90  # 90일 회전 주기
DURI_HMAC_KEY_DUAL_VERIFY=true    # 회전 중 이중 서명 허용
```

### 회전 중 이중 서명 허용
- 구키/신키 동시 검증으로 무중단 전환
- 회전 완료 후 구키 제거

## 2. 부팅 게이트 (필수)

### initContainer로 무결성 통과 후 앱 시작
```yaml
initContainers:
- name: integrity-gate
  image: yourimage:with-duri
  env:
    - name: DURI_ENV
      value: "prod"
    - name: DURI_INTEGRITY_MODE
      value: "strict"
  command: ["bash","-lc","scripts/ci_integrity_check.sh"]
```

## 3. 주기적 재검증

### 사이드카로 5~15분 간격 재검증
```yaml
containers:
- name: duri-integrity-sidecar
  image: yourimage:with-duri
  ports: [{containerPort: 9101, name: metrics}]
  command: ["bash","-lc","while true; do python -c 'from DuRiCore.deployment.deployment_integrity import deployment_integrity as d; from DuRiCore.deployment.integrity_metrics import integrity_metrics as m; r=d.verify_integrity(); m.record_integrity_scan(r); m.export_to_file(\"/metrics/integrity.prom\"); import time; time.sleep(300)' ; done"]
  volumeMounts:
  - { name: metrics, mountPath: /metrics }
```

## 4. 알람 라우팅

### Alertmanager 라우팅 규칙
```yaml
routes:
- match:
    severity: critical
  receiver: oncall-pager
  group_wait: 0s
  group_interval: 1m
  repeat_interval: 5m
- match:
    severity: warning
  receiver: oncall-slack
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 15m
```

### 알람 우선순위
- `tampered` = critical (즉시 paging)
- `policy_changed` = warning (10분 내 3회 연속 실패 시 paging)
- `corrupted` = critical (즉시 paging)

## 5. 라벨 카디널리티 가드

### 고빈도 카운터에서 deployment_id 제외
```python
# Info 성 메트릭에만 deployment_id 포함
duri_integrity_scan_info{deployment_id="...", status="verified"} 1
duri_integrity_scan_duration_ms{deployment_id="..."} 263

# 고빈도 카운터는 deployment_id 제외
duri_integrity_status_verified 1
duri_integrity_files_total{type="total"} 2262
```

## 6. 폭증 가드 운영 변수화

### 환경변수로 임계치 조절
```bash
DURI_INTEGRITY_SPIKE_THRESHOLD=0.3  # 기본 30%
DURI_ENV=prod                       # 프로덕션에서 실패 처리
```

## 7. 아티팩트 보관 정책

### 릴리스 아티팩트 180일+ 보존
```bash
# 보존 대상 파일
- checksums.json
- deployment_metadata.json
- checksums.sig
- deployment_metadata.sig
- provenance.json

# 롤백 시 해당 아티팩트 그대로 투입 → 부팅 전 검증
```

## 8. SBOM/서플라이체인 연계 (선택)

### SBOM 생성 및 provenance.json 연계
```bash
# Syft로 SBOM 생성
syft packages . -o spdx-json > sbom.json

# provenance.json에 SBOM digest 추가
{
  "sbom_digest": "sha256:abc123...",
  "sbom_format": "spdx-json"
}
```

## 9. 복구 훈련

### 표준 대응 절차
1. **tampered 감지** → 트래픽 격리
2. **마지막 green 배포로 자동 롤백**
3. **forensic 후 회복**

### 역할 분담
- **온콜**: 즉시 대응 (MTTA < 5분)
- **플랫폼**: 인프라 복구 (MTTR < 30분)
- **보안**: forensic 분석 (MTTR < 2시간)

## 10. 테스트 3개 추가

### 스키마 다운그레이드 테스트
```python
def test_schema_downgrade_detection():
    # schema_version=1.0 메타데이터로 검증 시 policy_changed 기대
    assert r["status"] == "policy_changed"
```

### 원자적 쓰기 중단 테스트
```python
def test_atomic_write_partial_file_prevention():
    # 쓰기 중단 시뮬레이션 → 파셜 파일 미생성 확인
    assert not os.path.exists("partial_file.json")
```

### symlink 루프 테스트
```python
def test_symlink_loop_prevention():
    # symlink 루프 생성 → 스캔 스킵 및 무한루프 방지 확인
    assert link_source not in checksums
```

## 대시보드 핵심 위젯

### 상태 스파크라인
```promql
max_over_time(duri_integrity_status_verified[24h])
max_over_time(duri_integrity_status_tampered[24h])
max_over_time(duri_integrity_status_policy_changed[24h])
```

### 스캔 시간/바이트 추이
```promql
duri_integrity_scan_duration_ms
duri_integrity_scan_bytes_hashed
```

### 파일 변동 추이
```promql
duri_integrity_files_modified
duri_integrity_files_missing
duri_integrity_files_new
```

## 운영 자동화 (Day 81-85)

### 다음 단계
- 대시보드/알람/런북을 릴리스 템플릿에 묶기
- "누가 배포해도 같은 안전성" 보장
- 팀 표준 템플릿 완성

