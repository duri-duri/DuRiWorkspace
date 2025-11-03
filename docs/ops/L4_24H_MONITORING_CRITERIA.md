# L4 24시간 모니터링 합격 기준 및 ABORT 규칙

## 합격 기준 (정량)

24시간 모니터링 종료 후 다음 기준을 모두 충족해야 **L4.9 선언**:

### 핵심 지표 (필수)

1. **Heartbeat 안정성**
   - `duri_heartbeat_ok == 1` (유지율 ≥ 99.9%)
   - `duri_heartbeat_fresh_120s == 1` (유지율 ≥ 99.5%)
   - `duri_heartbeat_changes_6m ≥ 1` (지속적 증가)

2. **Canary 품질**
   - `canary_failure_ratio ≤ 0.08` (P95 구간 기준)
   - `canary_unique_ratio ≥ 0.92`

3. **Error Budget**
   - `error_budget_burn_7d ≤ 0.60`
   - `error_budget_burn_30d ≤ 0.40`

4. **Disaster Recovery**
   - `dr_rehearsal_p95_minutes ≤ 12`

5. **Lyapunov 안정성**
   - `duri_lyapunov_v ≤ 0.2` (단조감소 추세)
   - 상승 이벤트 ≤ 1회/24h
   - 상승 폭 < 0.2

### 판정 로직

```bash
# 24시간 후 실행
bash scripts/ops/l4_24h_stats.sh

# 합격 조건:
# - Mean Lyapunov V ≤ 0.2
# - Abort 조건 0회
# - 모든 핵심 지표 목표 충족
```

## ABORT 규칙 (즉시 중단)

다음 조건 중 **하나라도 발생** 시 즉시 모니터링 중단 및 롤백:

### 즉시 ABORT (강제 종료, 실패 p>0.5)

1. **Lyapunov V 초과**
   - 조건: `duri_lyapunov_v > 0.3` 연속 5분
   - 조치: 즉시 중단, 롤백 실행

2. **Heartbeat Fresh 실패**
   - 조건: `duri_heartbeat_fresh_120s == 0` 연속 5분
   - 조치: 즉시 중단, 롤백 실행

3. **Heartbeat OK 실패**
   - 조건: `duri_heartbeat_ok != 1` 연속 5분
   - 조치: 즉시 중단, 롤백 실행

4. **Canary 실패율 초과**
   - 조건: `canary_failure_ratio > 0.08` 연속 5분
   - 조치: 즉시 중단, 롤백 실행

### 경고 (Watch, 모니터링 계속)

1. **Error Budget Burn**
   - 조건: `error_budget_burn_7d > 0.6` 10분 이상
   - 조치: 경고 로그, 모니터링 계속

2. **DR RTO 초과**
   - 조건: `dr_rehearsal_p95_minutes > 12` 15분 이상
   - 조치: 경고 로그, 모니터링 계속

## 롤백 절차

ABORT 발생 시 자동 롤백:

```bash
# 1) 롤백 스크립트 실행
bash scripts/ops/l4_dryrun_rollback.sh

# 2) 수동 롤백 (스크립트 실패 시)
# 규칙 되돌리기
git revert --no-edit <마지막 룰 커밋> || true
bash scripts/ops/reload_safe.sh

# 코드/데이터 스냅샷 기준 복귀
git reset --hard $(cat .reports/L4_START_COMMIT.txt)
docker compose -f compose.observation.yml restart prometheus
```

## 모니터링 상태 확인

```bash
# 모니터링 진행 상황 확인
screen -r l4-monitor

# 중간 통계 확인
bash scripts/ops/l4_24h_stats.sh

# 핵심 지표 즉시 확인
for q in duri_heartbeat_ok duri_heartbeat_fresh_120s duri_heartbeat_changes_6m duri_lyapunov_v; do \
  printf "[%s] " "$q"; curl -s --get 'http://localhost:9090/api/v1/query' --data-urlencode "query=$q{metric_realm=\"prod\"}" \
  | jq -r '.data.result[]?.value[1] // "N/A"'; echo ""; done
```

## 근본 원인 요약

### 해결된 문제

1. **Compose v1→v2 이행**
   - 문제: `KeyError: 'ContainerConfig'` (v1 잔재)
   - 해결: docker compose v2로 통일

2. **PromQL 문법 오류**
   - 문제: `timestamp()`에 range vector 사용
   - 해결: 직접 ts 지표 + fallback 사용

3. **Admin API Snapshot Race**
   - 문제: ID 발급 ↔ 디렉토리 생성 race
   - 해결: async 폴링 가드 추가

4. **테스트 결정론**
   - 문제: 기대 벡터 라벨/이름 미정합
   - 해결: 엄밀 매칭 & 절대시간 비교

### 남은 리스크

1. **node-exporter 타겟 헬스 경고**
   - 가능성: 운영 관측 누락/오탐 60%, 실제 타깃 미기동/네트워크 40%
   - 조치: compose에 node-exporter 서비스 확인, 타겟 헬스 모니터링

2. **Heartbeat 초기 결측**
   - 가능성: 리로드 직후 샘플 미도착 윈도우 >90%
   - 조치: `or on() vector(0)` fallback 유지, 짧은 완충(2~3분)

## 최적화 방향

1. **False Alarm 감소**
   - `freshness window` 120s 유지
   - 룰 순서를 `fresh→ok`로 배치
   - 기대 오경보: ~0.1% → 0.08%

2. **Reload 실패 감소**
   - `reload_safe.sh`의 컨테이너/호스트 promtool 교차검증 유지
   - 재시도 3→5로 완만 상향 (성공률 +0.02)

3. **샘플 주기 안정화**
   - `textfile_heartbeat.sh` 실행 주기 60s로 고정
   - `flock` 유지로 경합 방지

## 다음 행동

1. **타깃 헬스 확인**
   ```bash
   curl -s http://localhost:9090/api/v1/targets | jq -r '.data.activeTargets[] | "\(.labels.job) \(.health)"'
   ```

2. **핵심 지표 확인**
   ```bash
   for q in duri_heartbeat_ok duri_heartbeat_fresh_120s duri_heartbeat_changes_6m duri_lyapunov_v; do \
     printf "[%s] " "$q"; curl -s --get 'http://localhost:9090/api/v1/query' --data-urlencode "query=$q{metric_realm=\"prod\"}" \
     | jq -r '.data.result[]?.value[1] // "N/A"'; echo ""; done
   ```

3. **중간 점검**
   ```bash
   bash scripts/ops/l4_24h_stats.sh
   ```

4. **스냅샷 재확인**
   ```bash
   bash scripts/ops/prometheus_snapshot.sh
   ```

## 결론

- **L4 드라이런: GO 유지** (p ≈ 0.997-0.999)
- **24시간 모니터링**: 진행 중
- **ABORT 규칙**: 명확화 완료
- **롤백 절차**: 자동화 스크립트 준비 완료

**목표: 24시간 안정성 검증 후 L4.9 판정**

