# Shadow 훈련장 빠른 시작 가이드

## 🚀 30초 빠른 시작

```bash
cd /home/duri/DuRiWorkspace

# 1. 승인 플래그 생성 (최초 1회)
mkdir -p .shadow && touch .shadow/ALLOW_RUN

# 2. 상태 확인
bash scripts/shadow_check_health.sh

# 3. Shadow 훈련 시작 (HTTP 모드)
TRANSPORT=http bash scripts/shadow_duri_integration_final.sh
```

## 📋 체크리스트

### 사전 준비
- [ ] DuRi AI 서비스 실행 확인 (`docker ps | grep duri`)
- [ ] 승인 플래그 생성 (`.shadow/ALLOW_RUN`)
- [ ] 전송 어댑터 존재 확인 (`ls -la scripts/lib/transport.sh`)

### 실행 전 확인
```bash
# 전체 상태 확인
bash scripts/shadow_check_health.sh

# 상세 확인
bash scripts/shadow_check_health.sh --verbose
```

### 실행 모드 선택

#### 1. HTTP 모드 (기본, 권장)
```bash
TRANSPORT=http bash scripts/shadow_duri_integration_final.sh
```
- ✅ 안정적
- ✅ 관측 가능
- ✅ 문제 없음

#### 2. SSH 모드 (실험)
```bash
TRANSPORT=ssh bash scripts/shadow_duri_integration_final.sh
```
- ⚠️ 실전 변이 시뮬레이션
- ⚠️ SSH 연결 필요

#### 3. 하이브리드 모드 (카나리)
```bash
TRANSPORT=mixed SSH_CANARY=0.2 bash scripts/shadow_duri_integration_final.sh
```
- ✅ 기본 80% HTTP + 20% SSH
- ✅ 점진적 실험

## 🔍 실행 확인

### 로그 모니터링
```bash
# 실시간 로그
tail -f var/logs/shadow.log

# 최근 로그
tail -n 50 var/logs/shadow.log
```

### 메트릭 확인
```bash
# Prometheus 메트릭
curl -s http://localhost:9109/metrics | grep duri_shadow

# 전송 메트릭 파일
cat var/metrics/transport_metrics.prom
```

### EV 번들 확인
```bash
# 최신 EV 번들
ls -lt var/evolution/EV-* | head -5

# EV 메타 (transport 포함)
cat var/evolution/LATEST/summary.txt
```

## 🛠️ 문제 해결

### Shadow가 시작되지 않음
```bash
# 1. 승인 플래그 확인
ls -la .shadow/ALLOW_RUN

# 2. DuRi AI 서비스 확인
docker ps | grep duri

# 3. 포트 점유 확인
ss -tlnp | grep -E '8080|8081|8082|8083'

# 4. 상태 상세 확인
bash scripts/shadow_check_health.sh --verbose
```

### SSH 연결 실패
```bash
# SSH 포트 확인
docker ps --format "table {{.Names}}\t{{.Ports}}" | grep duri

# HTTP 모드로 폴백
TRANSPORT=http bash scripts/shadow_duri_integration_final.sh
```

## 📊 상태 확인 명령어

```bash
# 전체 상태 확인 (빠른 버전)
bash scripts/shadow_check_health.sh

# 전체 상태 확인 (상세 버전)
bash scripts/shadow_check_health.sh --verbose

# Shadow 실행 상태
ps aux | grep shadow_duri_integration_final.sh

# 메트릭 Exporter 실행 상태
ps aux | grep metrics_exporter_enhanced.py

# 최신 EV 번들
ls -lt var/evolution/EV-* | head -1
```

## 📚 더 알아보기

- [상세 가이드](./SHADOW_TRAINING_GROUND.md)
- [하이브리드 전송 시스템](./scripts/lib/transport.sh) (주석 참조)
- [메트릭 Exporter](./shadow/metrics_exporter_enhanced.py) (주석 참조)

