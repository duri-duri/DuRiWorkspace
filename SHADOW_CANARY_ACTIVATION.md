# Shadow 카나리 점진적 활성화 가이드

## 🎯 목표

Shadow 훈련장을 **카나리 방식으로 점진적으로 활성화**하여 안정성을 보장하면서 실전 변이 커버리지를 확보합니다.

## 📋 활성화 전 체크리스트

### 1. 게이트 조건 확인

```bash
cd /home/duri/DuRiWorkspace
bash scripts/shadow_gate_check.sh
```

**필수 조건 4개:**
- ✓ Export/메트릭 동기: FILE p == HTTP p (허용 오차 ≤ 1e-9)
- ✓ EV 사이클 무결성: ANCHOR.SHA256SUMS 존재 & summary: RECORDED*
- ✓ 루프 안정: loop_*.sh 최근 24h 자체 재기동 ≤ 2회
- ✓ 프리즈가드/허용경로: 모든 필수 경로 포함

### 2. 시스템 상태 확인

```bash
bash scripts/shadow_check_health.sh --verbose
```

## 🚀 카나리 활성화 절차

### 단계 1: 게이트 체크

```bash
bash scripts/shadow_gate_check.sh
```

게이트 통과 시 다음 단계로 진행.

### 단계 2: 카나리 제어기 시작

```bash
# 카나리 제어기 시작 (백그라운드)
python3 shadow/canary_controller.py &
echo $! > var/run/canary_controller.pid

# 상태 확인
cat var/run/canary.env  # SSH_CANARY 값 확인
```

### 단계 3: Shadow 카나리 모드 시작

```bash
# 카나리 모드 설정
export DURI_SHADOW_TRANSPORT=MIXED
export SSH_CANARY=0.15  # 초기 15% (카나리 제어기가 자동 조절)

# Shadow 시작
bash scripts/shadow_duri_integration_final.sh
```

### 단계 4: 모니터링

```bash
# 메트릭 확인 (3개 핵심 지표)
curl -s http://localhost:9109/metrics | grep -E \
  'duri_shadow_transport|duri_shadow_ssh_failures|duri_shadow_ssh_latency|duri_ab_p_value'

# 카나리 값 확인
cat var/run/canary.env

# 로그 모니터링
tail -f var/logs/shadow.log | grep -E "\[MIXED\]|\[CHAOS\]"
```

## 📊 카나리 파라미터

### 초기 설정

| 파라미터 | 기본값 | 범위 | 설명 |
|---------|-------|------|------|
| `SSH_CANARY` | 0.15 (15%) | 0.0 ~ 0.4 | SSH 카나리 확률 |
| `SSH_TIMEOUT` | 8초 | - | SSH 타임아웃 |
| `SSH_RETRY` | 2회 | - | SSH 재시도 횟수 |
| `CHAOS_ENABLED` | 1 (활성) | 0/1 | 카오스 주입 활성화 |
| `CHAOS_DELAY_PROB` | 0.005 (0.5%) | - | 지연 카오스 확률 |
| `CHAOS_DROP_PROB` | 0.01 (1%) | - | 패킷 드롭 카오스 확률 |

### 자동 조절 규칙 (PI 컨트롤러)

- **목표 실패율**: 5%
- **조절 주기**: 5분
- **최대 값**: 40%
- **최소 값**: 0% (폴백)

### 폴백 조건

1. **즉시 폴백** (SSH_CANARY = 0):
   - SSH 실패율 > 10% (10분 지속)
   - `ab_p_value == 0|1` (5분 지속)

2. **점진적 감소**:
   - SSH 실패율 > 5% (10분 지속)
   - SSH_CANARY를 80%로 감소

3. **자동 재개**:
   - 폴백 후 30분 경과
   - 게이트 조건 재통과
   - SSH_CANARY를 10%부터 재시작

## 🔔 알림룰

### Prometheus 알림 (자동 폴백 트리거)

1. **ShadowSSHFailureSpike**
   - 조건: SSH 실패율 > 5% (10분 지속)
   - 동작: 자동 폴백 (MIXED → HTTP)

2. **ShadowTransportDrift**
   - 조건: 전송 모드 비율 변화 > 20% (10분)
   - 동작: 알림만 (정보)

3. **ABTestPValueEdgeCase** (기존)
   - 조건: `ab_p_value == 0|1` (5분 지속)
   - 동작: Shadow 정지 + 파이프라인 점검 알림

## 🛠️ 문제 해결

### 문제: 카나리 제어기가 카나리 값을 조절하지 않음

**확인:**
```bash
# 제어기 프로세스 확인
ps aux | grep canary_controller

# 상태 파일 확인
cat var/run/canary_controller.state

# 메트릭 파일 확인
tail -20 var/metrics/transport_metrics.prom
```

**해결:**
```bash
# 제어기 재시작
pkill -f canary_controller.py
python3 shadow/canary_controller.py &
```

### 문제: SSH 실패율이 높음

**확인:**
```bash
curl -s http://localhost:9109/metrics | grep duri_shadow_ssh_failures
```

**해결:**
- 자동 폴백 대기 (카나리 제어기가 자동으로 조절)
- 수동 폴백: `export SSH_CANARY=0`

### 문제: 카오스 주입이 너무 강함

**해결:**
```bash
export CHAOS_ENABLED=0  # 카오스 비활성화
# 또는
export CHAOS_DELAY_PROB=0.001  # 지연 확률 감소
export CHAOS_DROP_PROB=0.005   # 드롭 확률 감소
```

## 📈 모니터링 대시보드

### Grafana 쿼리 예시

```promql
# SSH 카나리 비율
sum(rate(duri_shadow_transport_total{mode="ssh"}[5m])) / 
sum(rate(duri_shadow_transport_total[5m]))

# SSH 실패율
sum(rate(duri_shadow_transport_total{mode="ssh",status="failure"}[5m])) / 
sum(rate(duri_shadow_transport_total{mode="ssh"}[5m]))

# SSH 평균 지연 시간
avg(duri_shadow_ssh_latency_ms)

# 전송 모드별 호출 수
sum(rate(duri_shadow_transport_total[5m])) by (mode)
```

## 🎯 성공 기준

- ✓ SSH 실패율 < 5% (지속)
- ✓ SSH p95 지연 < 2× HTTP p95 지연
- ✓ `ab_p_value` 정상 범위 (0 < p < 1)
- ✓ 카나리 제어기 자동 조절 정상 동작
- ✓ EV 번들 정상 생성 (transport 메타 포함)

## 📚 관련 문서

- [Shadow 훈련장 가이드](./SHADOW_TRAINING_GROUND.md)
- [빠른 시작](./SHADOW_QUICKSTART.md)
- [카나리 제어기 코드](./shadow/canary_controller.py)
- [알림룰 정의](./prometheus/rules/duri-ab-test.rules.yml)

---

**최종 업데이트:** 2025-10-31
**버전:** 1.0.0 (카나리 점진적 활성화)

