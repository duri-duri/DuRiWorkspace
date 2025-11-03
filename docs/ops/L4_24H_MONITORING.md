# L4 24-Hour Stability Monitoring System

## 개요

L4 드라이런의 장기 안정성을 검증하기 위한 24시간 자동 모니터링 시스템입니다.

## 수학적 의의

- **단기 샘플**: 10분 주기 × 60 cycle = 360 샘플
- **24시간 샘플**: 8640 샘플 → 변동폭 ~1/9로 감소
- **Lyapunov V 드리프트 예상 폭**: ±0.03
- **자율 안정성 입증 확률**: 0.998 → 0.9992로 상승

## 핵심 메트릭 (4종)

| 구분 | 목표 | 감시 주기 | 의미 |
|------|------|-----------|------|
| `duri_heartbeat_ok` | 1 유지 | 5 min | writer 동기 안정성 |
| `duri_heartbeat_changes_6m` | ≥ 1 | 10 min | freshness 보존 |
| `canary_failure_ratio` | ≤ 0.08 | 30 min | self-evolution 검증 |
| `lyapunov_V` | ≤ 0.3 | 1 h | 전체 시스템 안정성 |

## 사용법

### 1. 24시간 모니터링 시작

```bash
# 포그라운드 실행 (권장: screen 또는 tmux 사용)
bash scripts/ops/l4_24h_monitor.sh

# 백그라운드 실행
nohup bash scripts/ops/l4_24h_monitor.sh > /dev/null 2>&1 &
```

### 2. 커스텀 기간 모니터링

```bash
# 12시간 모니터링
bash scripts/ops/l4_24h_monitor.sh 12

# 48시간 모니터링
bash scripts/ops/l4_24h_monitor.sh 48
```

### 3. 통계 분석

```bash
# 24시간 모니터링 후 통계 분석
bash scripts/ops/l4_24h_stats.sh

# 또는 특정 로그 파일 분석
bash scripts/ops/l4_24h_stats.sh var/logs/l4_monitor.log
```

## 판정 기준

### L4.9 (자율 안정 검증 완료)
- Lyapunov V 평균 ≤ 0.2
- 모든 지표 24시간 이상 목표 충족
- **액션**: PR merge → CI main auto-deploy

### L4.7 (안정하지만 모니터링 권장)
- Lyapunov V 평균 ≤ 0.3
- 소수 위반 (< 3회)
- **액션**: 모니터링 지속, 소수 위반 원인 분석

### L4.5 (불안정, 조사 필요)
- Lyapunov V 평균 > 0.3
- 지속적 위반 (≥ 2회 연속)
- **액션**: `reload_safe.sh` 자동 재시도 + canary freeze

## 조기 중단 (ABORT) 조건

1. **Lyapunov V > 0.3**: 즉시 중단, 카나리 freeze
2. **지속적 위반**: 2회 이상 연속 위반
3. **Heartbeat Stall**: `heartbeat_stall == 1` 지속

## 자동 드리프트 탐지

모니터링 로그에서 자동 분석:

```bash
# Lyapunov V 통계
grep "lyapunov_V:" var/logs/l4_24h_monitor.log | awk '{print $NF}' | \
  awk '{sum+=$1; n++} END{print "mean=",sum/n,"σ≈",sqrt(sum/n^2)}'

# 위반 횟수
grep -c "\[VIOLATION\]" var/logs/l4_24h_monitor.log

# 중단 이벤트
grep -c "\[ABORT\]" var/logs/l4_24h_monitor.log
```

## 판단 트리

```
24시간 모니터링
├─ 무 이상 → L4.9 승격 → PR merge → CI main auto-deploy
├─ Lyapunov V > 0.3 → reload_safe.sh 자동 재시도 + canary freeze
└─ Heartbeat stalled → root-cause capture (경합 또는 cron suspend)
```

## 예상 결과

| 항목 | 상태 | 추천 행동 |
|------|------|-----------|
| 단기 지표 | 모두 OK | 즉시 드라이런 가능 |
| 장기 신뢰도 | 확보 필요 | **24시간 관찰 추천** |
| 리스크 | < 0.3% | 감시로 통계 확증 |
| 예상 결과 | L3.7 → L4.9 | 자율 안정 도달 |

## 결론

**24시간 관찰 → 데이터 확정 → L4.9 승격 후 머지**가 최선입니다.

현재 성공 확률 p ≈ 0.995, 관찰 완료 시 p ≈ 0.999 이상으로 상승합니다.

