# Shadow 훈련장 완성 가이드

## 📋 목차
1. [시스템 개요](#시스템-개요)
2. [파일 구조](#파일-구조)
3. [하이브리드 전송 시스템](#하이브리드-전송-시스템)
4. [작동 확인 방법](#작동-확인-방법)
5. [사용 방법](#사용-방법)

---

## 시스템 개요

Shadow 훈련장은 DuRi AI 시스템의 **실전 훈련 및 진화 테스트 환경**입니다.

### 핵심 구성 요소

```
┌─────────────────────────────────────────────────────────────┐
│                    Shadow 훈련장 시스템                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │  Shadow 스크립트 │───▶│  전송 어댑터    │                │
│  │  (메인 루프)     │    │  (HTTP/SSH)     │                │
│  └─────────────────┘    └─────────────────┘                │
│          │                         │                          │
│          │                         ▼                          │
│          │              ┌───────────────────┐                │
│          │              │  DuRi AI 서비스   │                │
│          │              │  (Core/Brain/    │                │
│          │              │   Evolution/      │                │
│          │              │   Control)        │                │
│          │              └───────────────────┘                │
│          │                         │                          │
│          ▼                         ▼                          │
│  ┌─────────────────┐    ┌───────────────────┐              │
│  │  메트릭 수집      │◀───│  메트릭 Exporter  │              │
│  │  (Prometheus)    │    │  (포트 9109)      │              │
│  └─────────────────┘    └───────────────────┘              │
│          │                                                  │
│          ▼                                                  │
│  ┌─────────────────┐                                       │
│  │  EV 메타 기록    │                                       │
│  │  (진화 증거)     │                                       │
│  └─────────────────┘                                       │
└─────────────────────────────────────────────────────────────┘
```

### 전송 방식 (하이브리드)

- **HTTP 모드** (기본): 안정적이고 관측 가능한 통신
- **SSH 모드**: 실전 변이 시뮬레이션 (지연, 장애, 키 교환)
- **MIXED 모드**: 카나리 배포 (기본 80% HTTP, 20% SSH)

---

## 파일 구조

### 핵심 파일

```
DuRiWorkspace/
├── scripts/
│   ├── shadow_duri_integration_final.sh    # 메인 훈련 스크립트
│   └── lib/
│       └── transport.sh                    # 하이브리드 전송 어댑터
├── shadow/
│   ├── metrics_exporter_enhanced.py         # Prometheus 메트릭 수집
│   └── metrics_exporter.py                 # 기본 메트릭 (레거시)
├── scripts/evolution/
│   ├── evidence_bundle.sh                  # EV 메타 기록 (transport 포함)
│   └── evidence_score.sh                   # EV 점수 계산
└── var/
    ├── metrics/
    │   ├── transport_metrics.prom          # 전송 메트릭 (자동 생성)
    │   └── ab_eval.prom                    # AB 테스트 p-value
    ├── logs/
    │   └── shadow.log                      # Shadow 훈련 로그
    └── evolution/
        └── EV-YYYYMMDD-HHMMSS-XX/          # 진화 증거 번들
            ├── summary.txt                  # 메타 (transport 포함)
            └── ...
```

### 파일 역할

| 파일 | 역할 | 의존성 |
|------|------|--------|
| `scripts/shadow_duri_integration_final.sh` | Shadow 훈련 메인 루프 | `transport.sh` |
| `scripts/lib/transport.sh` | 하이브리드 전송 어댑터 (HTTP/SSH/MIXED) | 없음 |
| `shadow/metrics_exporter_enhanced.py` | Prometheus 메트릭 수집 및 노출 | `transport_metrics.prom` |
| `scripts/evolution/evidence_bundle.sh` | 진화 증거 번들 생성 (transport 메타 포함) | 없음 |

---

## 하이브리드 전송 시스템

### 전송 어댑터 (`scripts/lib/transport.sh`)

**기능:**
- HTTP/SSH/MIXED 모드 지원
- 카나리 배포 (확률 기반 SSH 선택)
- 메트릭 자동 기록
- SSH 실패 시 HTTP 폴백

**함수:**
```bash
# 서비스 호출 (자동 선택)
call_service <service> <path> <method> [data]

# 편의 함수
call_core <path> <method> [data]      # duri-core 전용
```

**환경 변수:**
```bash
TRANSPORT=http|ssh|mixed              # 전송 방식 (기본: http)
SSH_CANARY=0.2                        # SSH 카나리 확률 (기본: 20%)
SSH_TIMEOUT=8                         # SSH 타임아웃 (초)
SSH_RETRY=2                           # SSH 재시도 횟수

# SSH 타겟 (Docker 컨테이너)
CORE_SSH=root@localhost:2220
BRAIN_SSH=root@localhost:2221
EVOLUTION_SSH=root@localhost:2222
CONTROL_SSH=root@localhost:2223
```

### 메트릭 수집 (`shadow/metrics_exporter_enhanced.py`)

**메트릭:**
- `duri_shadow_transport_total{mode,service,status}`: 전송 호출 카운터
- `duri_shadow_ssh_failures_total{service}`: SSH 실패 카운터
- `duri_shadow_ssh_latency_ms{service}`: SSH 지연 시간 (미래 구현)

**노출:**
- HTTP: `http://localhost:9109/metrics`

---

## 작동 확인 방법

### 빠른 확인 (원라이너)

```bash
# 전체 상태 확인
bash scripts/shadow_check_health.sh

# 상세 확인
bash scripts/shadow_check_health.sh --verbose
```

### 수동 확인 절차

#### 1. 전송 어댑터 확인
```bash
cd /home/duri/DuRiWorkspace

# 전송 어댑터 로드 테스트
source scripts/lib/transport.sh
call_service "core" "/health" "GET"
# 예상 출력: HTTP 200 응답 또는 JSON
```

#### 2. DuRi AI 서비스 확인
```bash
# Docker 컨테이너 상태
docker ps | grep -E "duri-core|duri-brain|duri-evolution|duri-control"

# 헬스 체크 (HTTP)
curl -s http://localhost:8080/health | jq .
curl -s http://localhost:8081/health | jq .
curl -s http://localhost:8082/health | jq .
curl -s http://localhost:8083/health | jq .

# SSH 연결 테스트 (포트 확인)
ssh -p 2220 root@localhost -o ConnectTimeout=2 -o StrictHostKeyChecking=no "echo OK" || echo "SSH 실패"
ssh -p 2221 root@localhost -o ConnectTimeout=2 -o StrictHostKeyChecking=no "echo OK" || echo "SSH 실패"
```

#### 3. 메트릭 Exporter 확인
```bash
# Exporter 실행 확인
ps aux | grep metrics_exporter_enhanced.py

# 메트릭 노출 확인
curl -s http://localhost:9109/metrics | grep duri_shadow_transport
```

#### 4. Shadow 훈련 실행 확인
```bash
# PID 확인
cat var/run/shadow.pid 2>/dev/null && echo "Shadow 실행 중" || echo "Shadow 미실행"

# 로그 확인
tail -f var/logs/shadow.log

# 최근 EV 번들 확인
ls -lt var/evolution/EV-* | head -5
```

---

## 사용 방법

### 기본 실행 (HTTP 모드)

```bash
cd /home/duri/DuRiWorkspace

# 승인 플래그 생성 (최초 1회)
mkdir -p .shadow
touch .shadow/ALLOW_RUN

# Shadow 훈련 시작
TRANSPORT=http bash scripts/shadow_duri_integration_final.sh
```

### SSH 모드 실행

```bash
# SSH 타겟 설정 확인
export CORE_SSH=root@localhost:2220
export BRAIN_SSH=root@localhost:2221
export EVOLUTION_SSH=root@localhost:2222
export CONTROL_SSH=root@localhost:2223

# SSH 모드 실행
TRANSPORT=ssh bash scripts/shadow_duri_integration_final.sh
```

### 하이브리드 모드 실행 (카나리)

```bash
# 카나리 확률 설정 (20% SSH)
export TRANSPORT=mixed
export SSH_CANARY=0.2

# 실행
bash scripts/shadow_duri_integration_final.sh
```

### Makefile 사용

```bash
# Shadow 시작
make shadow-start

# Shadow 중지
make shadow-stop

# Shadow 상태 확인
make shadow-status
```

### 시스템 서비스 (systemd) 사용

```bash
# 서비스 시작
systemctl --user start duri-shadow-exporter.service
systemctl --user start duri-evidence.timer

# 서비스 상태 확인
systemctl --user status duri-shadow-exporter.service
systemctl --user list-timers --user duri-*
```

---

## 문제 해결

### 문제: Shadow가 시작되지 않음

**확인 사항:**
1. 승인 플래그 존재: `ls -la .shadow/ALLOW_RUN`
2. DuRi AI 서비스 실행: `docker ps | grep duri-`
3. 포트 점유 확인: `ss -tlnp | grep -E '8080|8081|8082|8083'`

**해결:**
```bash
# 승인 플래그 생성
mkdir -p .shadow && touch .shadow/ALLOW_RUN

# DuRi AI 서비스 시작
docker compose up -d

# Shadow 재시도
bash scripts/shadow_duri_integration_final.sh
```

### 문제: SSH 연결 실패

**확인 사항:**
1. Docker 컨테이너 SSH 포트 열림: `docker ps | grep 222`
2. SSH 키 인증: `ssh -p 2220 root@localhost`
3. 컨테이너 내부 curl 사용 가능: `docker exec duri-core curl -s http://localhost:8080/health`

**해결:**
```bash
# SSH 포트 확인
docker ps --format "table {{.Names}}\t{{.Ports}}" | grep duri

# HTTP 모드로 폴백
TRANSPORT=http bash scripts/shadow_duri_integration_final.sh
```

### 문제: 메트릭이 수집되지 않음

**확인 사항:**
1. Exporter 실행: `ps aux | grep metrics_exporter`
2. 메트릭 파일 생성: `ls -la var/metrics/transport_metrics.prom`
3. Exporter 노출: `curl -s http://localhost:9109/metrics | head -20`

**해결:**
```bash
# Exporter 수동 시작
cd /home/duri/DuRiWorkspace
python3 shadow/metrics_exporter_enhanced.py &

# 메트릭 파일 확인
cat var/metrics/transport_metrics.prom
```

---

## 모니터링 대시보드

### Prometheus 쿼리 예시

```promql
# 전송 모드별 호출 수
sum(rate(duri_shadow_transport_total[5m])) by (mode)

# SSH 실패율
sum(rate(duri_shadow_ssh_failures_total[5m])) / sum(rate(duri_shadow_transport_total{mode="ssh"}[5m]))

# 서비스별 성공률
sum(rate(duri_shadow_transport_total{status="success"}[5m])) by (service) / sum(rate(duri_shadow_transport_total[5m])) by (service)
```

### Grafana 대시보드

- 위치: `grafana/provisioning/dashboards/shadow_training.json`
- URL: `http://localhost:3000/d/shadow-training`

---

## 참고 자료

- [하이브리드 전송 시스템 설계](./docs/hybrid-transport.md) (미래 구현)
- [Shadow 훈련 계획](./SHADOW_TRAINING_PLAN.md)
- [진화 증거 파이프라인](./scripts/evolution/README.md)

---

**최종 업데이트:** 2025-10-31
**버전:** 1.0.0 (하이브리드 전송 시스템 통합)

