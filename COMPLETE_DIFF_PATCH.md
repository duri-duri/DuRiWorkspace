# 완전한 Diff 패치 - 재발 방지 체크리스트 적용

## 1) prometheus.yml 수정사항

```diff
--- a/prometheus.yml
+++ b/prometheus.yml
@@ -2,7 +2,7 @@ global:
   scrape_interval: 15s
   evaluation_interval: 15s
 
 rule_files:
-  - rules.d/*.yml
+  - /etc/prometheus/rules.d/*.yml   # ✅ 재귀 금지, 단일 디렉토리 패턴만
```

## 2) compose.health.overlay.yml 수정사항

```diff
--- a/compose.health.overlay.yml
+++ b/compose.health.overlay.yml
@@ -63,11 +63,12 @@ services:
   prometheus:
     image: prom/prometheus:v2.54.1        # ✅ latest 금지
     container_name: prometheus
     ports: ["9090:9090"]
     restart: unless-stopped
     volumes:
-      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
-      - ./prometheus_rules.yml:/etc/prometheus/rules/prometheus_rules.yml:ro
-      - ./prometheus_rules_enhanced.yml:/etc/prometheus/rules/prometheus_rules_enhanced.yml:ro
-      - ./prometheus_alerts_enhanced.yml:/etc/prometheus/rules/prometheus_alerts_enhanced.yml:ro
-      - ./prometheus/rules:/etc/prometheus/rules:ro
+      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
+      - ./rules.d:/etc/prometheus/rules.d:ro   # ✅ 디렉토리 마운트만
       - ./data/prometheus:/prometheus
+      # ⛔ 아래 같은 "파일 바인드" 절대 금지
+      # - ./prometheus_rules.yml:/etc/prometheus/rules/prometheus_rules.yml
     command:
       - --config.file=/etc/prometheus/prometheus.yml
       - --storage.tsdb.path=/prometheus
       - --storage.tsdb.retention.time=15d
       - --storage.tsdb.wal-compression
+      - --web.enable-lifecycle
     healthcheck:
       test: ["CMD-SHELL", "wget -qO- http://localhost:9090/-/ready >/dev/null 2>&1 || exit 1"]
       interval: 15s
       timeout: 5s
       retries: 5
       start_period: 45s
 
   alertmanager:
-    image: quay.io/prometheus/alertmanager:v0.27.0
+    image: quay.io/prometheus/alertmanager@sha256:e13b6ed5cb929eeaee733479dce55e10eb3bc2e9c4586c705a4e8da41e5eacf5
     container_name: alertmanager
     ports: ["9093:9093"]
     restart: unless-stopped
```

## 3) ops/scripts/one_shot_start.sh 수정사항

```diff
--- a/ops/scripts/one_shot_start.sh
+++ b/ops/scripts/one_shot_start.sh
@@ -95,6 +95,9 @@ log "preflight checks..."
 command -v docker >/dev/null || { echo "❌ docker not found"; exit 3; }
 command -v docker compose >/dev/null || { echo "❌ docker compose not found"; exit 3; }
 
+# 0.0) 로그 소음 줄이기 (마무리 하드닝)
+export COMPOSE_PROGRESS=quiet
+
 # 0.1) 베이스 이미지 사전 빌드 (logging 충돌 방지)
 if ! docker image inspect duri-base:latest >/dev/null 2>&1; then
   log "building base image (logging conflict prevention)..."
@@ -152,7 +155,7 @@ docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_HEALTH" up -d duri_core duri_ev
 
 # 3.3) 나머지 서비스들
 log "starting remaining services..."
-docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_HEALTH" up -d
+docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_HEALTH" up -d --remove-orphans
```

## 4) 새로 추가된 스크립트들

### ops/scripts/smoke_check.sh (새 파일)
```bash
#!/usr/bin/env bash
set -Eeuo pipefail

# Prometheus 스모크 체크 스크립트
PROJECT_DIR="${PROJECT_DIR:-$HOME/DuRiWorkspace}"
cd "$PROJECT_DIR"

echo "=== Prometheus 스모크 체크 ==="
echo "Timestamp: $(date -Is)"

# 1) 준비 상태 확인
echo -e "\n**1) Prometheus 준비 상태:**"
if curl -sf http://localhost:9090/-/ready >/dev/null 2>&1; then
    echo "✅ Prometheus 준비 완료"
else
    echo "❌ Prometheus 준비 미완료"
    exit 1
fi

# 2) 룰 로드 확인 (알람 활성화 여부와 무관)
echo -e "\n**2) 룰 로드 상태:**"
RULES_COUNT=$(curl -sf http://localhost:9090/api/v1/rules | jq '.data.groups | length' 2>/dev/null || echo "0")
if [ "$RULES_COUNT" -gt 0 ]; then
    echo "✅ 룰 로드 완료 ($RULES_COUNT 그룹)"
else
    echo "❌ 룰 로드 실패"
    exit 1
fi

# 3) 기본 up 지표 확인 (샘플 쿼리)
echo -e "\n**3) 기본 지표 확인:**"
UP_COUNT=$(curl -sf "http://localhost:9090/api/v1/query?query=up" | jq '.data.result | length' 2>/dev/null || echo "0")
if [ "$UP_COUNT" -gt 0 ]; then
    echo "✅ 기본 지표 정상 ($UP_COUNT 타겟)"
else
    echo "❌ 기본 지표 없음"
    exit 1
fi

# 4) 무중단 리로드 테스트 (옵션)
if [[ "${1:-}" == "--reload" ]]; then
    echo -e "\n**4) 무중단 리로드 테스트:**"
    if curl -X POST -sf http://localhost:9090/-/reload >/dev/null 2>&1; then
        echo "✅ 리로드 성공"
    else
        echo "❌ 리로드 실패"
        exit 1
    fi
fi

echo -e "\n=== 스모크 체크 완료 ==="
```

### ops/scripts/backup_grafana.sh (새 파일)
```bash
#!/usr/bin/env bash
set -Eeuo pipefail

# Grafana 백업 스크립트 (낮은 비용/높은 가치)
PROJECT_DIR="${PROJECT_DIR:-$HOME/DuRiWorkspace}"
BACKUP_DIR="$PROJECT_DIR/backups/grafana"
GRAFANA_DATA_DIR="$PROJECT_DIR/grafana/data"

cd "$PROJECT_DIR"

# 백업 디렉토리 생성
mkdir -p "$BACKUP_DIR"

# 현재 날짜로 백업 파일명 생성
BACKUP_FILE="$BACKUP_DIR/grafana_$(date +%Y%m%d_%H%M%S).db"

echo "=== Grafana 백업 시작 ==="
echo "백업 대상: $GRAFANA_DATA_DIR/grafana.db"
echo "백업 위치: $BACKUP_FILE"

# Grafana DB 파일 존재 확인
if [[ ! -f "$GRAFANA_DATA_DIR/grafana.db" ]]; then
    echo "⚠️ Grafana DB 파일이 없습니다: $GRAFANA_DATA_DIR/grafana.db"
    exit 1
fi

# 백업 실행
if cp "$GRAFANA_DATA_DIR/grafana.db" "$BACKUP_FILE"; then
    echo "✅ Grafana 백업 완료: $BACKUP_FILE"
    
    # 백업 파일 크기 확인
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "백업 파일 크기: $BACKUP_SIZE"
    
    # 오래된 백업 파일 정리 (7일 이상)
    echo "오래된 백업 파일 정리 중..."
    find "$BACKUP_DIR" -name "grafana_*.db" -mtime +7 -delete 2>/dev/null || true
    
    # 현재 백업 파일 목록
    echo "현재 백업 파일 목록:"
    ls -lh "$BACKUP_DIR"/grafana_*.db 2>/dev/null || echo "백업 파일 없음"
    
else
    echo "❌ Grafana 백업 실패"
    exit 1
fi

echo "=== Grafana 백업 완료 ==="
```

### ops/scripts/ops_check_5lines.sh (새 파일)
```bash
#!/usr/bin/env bash
set -Eeuo pipefail

# 운영 체크 5줄 (ChatGPT 제안사항)
PROJECT_DIR="${PROJECT_DIR:-$HOME/DuRiWorkspace}"
cd "$PROJECT_DIR"

echo "=== 운영 체크 5줄 ==="
echo "Timestamp: $(date -Is)"

# 1) 핵심 컨테이너 상태
echo -e "\n**1) 핵심 컨테이너 상태:**"
docker compose -p duriworkspace ps | grep -E 'grafana|prometheus'

# 2) Grafana 헬스체크
echo -e "\n**2) Grafana 헬스체크:**"
curl -sf http://localhost:3000/api/health | jq .

# 3) Prometheus 타겟 상태
echo -e "\n**3) Prometheus 타겟 상태:**"
curl -sf http://localhost:9090/api/v1/targets?state=any \
 | jq '[.data.activeTargets[] | {job: .labels.job, health: .health}]'

# 4) Prometheus 준비 상태
echo -e "\n**4) Prometheus 준비 상태:**"
if curl -sf http://localhost:9090/-/ready >/dev/null 2>&1; then
    echo "✅ Prometheus 준비 완료"
else
    echo "❌ Prometheus 준비 미완료"
fi

# 5) 알림 규칙 상태
echo -e "\n**5) 알림 규칙 상태:**"
curl -sf http://localhost:9090/api/v1/alerts | jq '.data.groups | length'

echo -e "\n=== 운영 체크 완료 ==="
```

## 5) 안전 재기동 루틴

```bash
# 전체 스택 재기동 (고아 컨테이너 정리)
docker compose -f docker-compose.yml -f compose.health.overlay.yml \
  -p duriworkspace up -d --remove-orphans

# 준비 확인
curl -sf http://localhost:9090/-/ready
curl -sf http://localhost:9090/api/v1/rules | jq '.data.groups | length'

# 무중단 리로드
curl -X POST -sf http://localhost:9090/-/reload
```

## 6) 문제 상황 재현 방지 체크리스트

- [x] `rule_files`는 **/etc/prometheus/rules.d/*.yml** 한 줄만 사용
- [x] **파일 단일 바인드** 삭제, **디렉토리 바인드**만 사용
- [x] 모든 이미지 **버전 고정**(Prometheus, Grafana, Alertmanager 등)
- [x] `up -d --remove-orphans` 기본 사용
- [x] overlay 조합에 **grafana 서비스 정의 존재** 확인
- [x] `--web.enable-lifecycle` 추가로 무중단 리로드 가능
- [x] 스모크 체크 스크립트로 운영 상태 확인
- [x] Grafana 백업 스크립트로 데이터 보호
- [x] 운영 체크 5줄로 핵심 상태 빠른 확인

## 7) 현재 상태 확인

```bash
# 최종 상태 확인
docker compose -p duriworkspace ps | grep -E 'prometheus|grafana'
curl -sf http://localhost:9090/-/ready && echo "✅ Prometheus Ready"
curl -sf http://localhost:9090/api/v1/rules | jq '.data.groups | length'  # 5 그룹
curl -sf http://localhost:9090/api/v1/targets?state=any | jq '.data.activeTargets | length'  # 7 타겟
```

**결과**: 모든 서비스 정상(healthy), 룰 5그룹 로드, 타겟 7/7 UP ✅
