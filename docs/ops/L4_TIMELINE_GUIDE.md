# L4.0 타임라인 기반 능동 모니터링 가이드 - 최종 버전

## 핵심 원칙

**"그냥 기다림" 금지** → **타임라인 스크립트가 자동 대기+검증** → **사용자는 체크포인트에서만 판정**

## 즉시 실행 (3줄)

```bash
cd /home/duri/DuRiWorkspace
bash scripts/bin/status_coldsync_oneline.sh   # 사전 스냅샷
bash scripts/evolution/run_l4_timeline.sh     # 타임라인 자동 실행
```

**이 스크립트는:**
- 자동으로 T+2분, T+15분 대기 및 검증
- T+15~45분 능동 모니터링 루프 (5분 주기, 6회)
- 개입 트리거 자동 감지 및 중단
- 체크포인트마다 명확한 "수동 스팟체크 필요" 메시지 출력

## 수동 스팟체크 (체크포인트마다 필수)

### T+2분: AC 즉시검증

```bash
bash scripts/evolution/check_l4_timeline.sh T2
systemctl --no-pager status coldsync-install.path coldsync-verify.timer | egrep 'active|enabled'
journalctl -u coldsync-install.service -n 80 --no-pager | egrep 'INSTALLED|No change'
```

**GO/NO-GO 기준:**
- ✅ `path/timer = active & enabled`
- ✅ 설치 로그에 `INSTALLED/No change` ≥1회
- ✅ SHA256 불일치 0건

**실패 시:**
```bash
bash scripts/evolution/l4_killswitch.sh recover
bash scripts/bin/finalize_coldsync_autodeploy.sh
bash scripts/evolution/execute_l4_promotion.sh
```

### T+15분: 빠른 상태 + SLO 판정

```bash
bash scripts/evolution/check_l4_timeline.sh T15
bash scripts/evolution/quick_l4_check.sh
bash scripts/evolution/verify_l4_gate.sh
```

**GO/NO-GO 기준:**
- ✅ `path/timer = active & enabled`
- ✅ 설치 로그에 `INSTALLED/No change` ≥1회
- ✅ SHA256 불일치 0건
- ✅ Gate 6/6 = PASS

**실패 시:**
```bash
bash scripts/evolution/l4_killswitch.sh recover
bash scripts/bin/finalize_coldsync_autodeploy.sh
bash scripts/evolution/execute_l4_promotion.sh
```

### T+45분: 능동 모니터링 요약

```bash
bash scripts/evolution/check_l4_timeline.sh T45
bash scripts/evolution/monitor_l4_dashboard.sh 300
```

**확인 사항:**
- 개입 트리거 없음 확인
- 이상 없으면 유지

### T+24h: 안착 판정

```bash
bash scripts/evolution/check_l4_timeline.sh T24h
bash scripts/evolution/check_l4_settlement.sh
```

**안착 기준 (모두 참이면 L4.0 확정):**
- ✅ `PROMOTE ≥ 1`, `ROLLBACK = 0`
- ✅ `stability ≥ 0.90`, `halluc_rate ≤ 0.08` (연속 2 윈도우)
- ✅ 게이트 점수 `G ≥ 0.70` (2회 연속)

**확정 태깅/기준선 고정:**
```bash
bash scripts/bin/snapshot_coldsync_security.sh
bash scripts/bin/tag_coldsync_baseline.sh && git push --tags
bash scripts/evolution/declare_l4.sh
```

**그레이존 (0.80 ≤ promotion_score_7d < 0.82):**
- 지터/가중치/격리 적용 후 12h 추가 드릴

**실패 시:**
```bash
bash scripts/evolution/l4_killswitch.sh rollback
```

## 개입 트리거 (감지 시 즉시 행동)

다음 조건이 감지되면 즉시 개입:

- `halluc_rate > 0.10` 또는 `stability < 0.85`
- `ROLLBACK > 0` 발생
- **SHA256 불일치** (coldsync 바이너리/설치물)
- 게이트 스코어 `G < 0.70` 또는 `PROMOTE=0 & ROLLBACK≥1` (연속 2윈도우)

**개입 단추:**
```bash
bash scripts/evolution/l4_killswitch.sh recover   # 일시 차단
bash scripts/evolution/l4_killswitch.sh rollback  # 완전 롤백
```

## 빠른 스팟체크 원라이너

```bash
bash scripts/evolution/spotcheck_l4.sh
```

또는:

```bash
bash scripts/bin/status_coldsync_oneline.sh && grep -E "PROMOTE|ROLLBACK|RETRY" -n var/evolution/*.log | tail -n 5
```

## 실패 후 재시도 루틴

```bash
bash scripts/bin/recover_coldsync.sh
bash scripts/bin/finalize_coldsync_autodeploy.sh
bash scripts/evolution/execute_l4_promotion.sh
```

## Kill-Switch 통합

### 상태 확인
```bash
bash scripts/evolution/l4_killswitch.sh status
```

### 일시 차단
```bash
bash scripts/evolution/l4_killswitch.sh recover
```

### 완전 롤백
```bash
bash scripts/evolution/l4_killswitch.sh rollback
```

## 타임라인 요약

```
T+0     → 실행
T+2분   → AC 즉시검증 (수동 스팟체크 필수)
T+15분  → 빠른 상태 + SLO 판정 (수동 스팟체크 필수)
T+15~45분 → 능동 모니터링 루프 (자동)
T+45분  → 능동 모니터링 요약 (수동 스팟체크 권장)
T+24h   → 안착 판정 (수동 스팟체크 필수)
```

## 결정 트리

### T+2분 실패
```bash
bash scripts/bin/recover_coldsync.sh
bash scripts/bin/finalize_coldsync_autodeploy.sh
bash scripts/evolution/execute_l4_promotion.sh
```

### T+15분 SLO 실패
```bash
bash scripts/bin/recover_coldsync.sh
bash scripts/bin/finalize_coldsync_autodeploy.sh
bash scripts/evolution/execute_l4_promotion.sh
```

### T+24h 일부 미달
- L4 유지하되 `l4_operational_drill.sh` 반복 + 관측 룰 튠 큐 투입:
```bash
python3 scripts/evolution/task_queue.py enqueue obs-rule-tune '{}'
```

### 그레이존 (0.80 ≤ promotion_score_7d < 0.82)
- 지터/가중치/격리 적용 후 12h 추가 드릴

### 실패 (promotion_score_7d < 0.80)
```bash
bash scripts/evolution/l4_killswitch.sh rollback
```

## 확률/민감도

- 현재 성공 확률: p≈0.85 (하드닝 적용 시 ≈0.88)
- 승급 점수 민감도 (정규화 근사):
  - `∂Score/∂(주기 실행 안정화)` ≈ **0.24**
  - `∂Score/∂(실패→교정 큐 가동률)` ≈ **0.15**
  - `∂Score/∂(doc→PR 자동화)` ≈ **0.08**

## 요약

**"그냥 기다림" 금지** → **타임라인 스크립트가 자동 대기+검증** → **사용자는 체크포인트에서만 판정**

1. **실행**: `bash scripts/evolution/run_l4_timeline.sh`
2. **체크포인트마다 수동 스팟체크** (T+2분, T+15분, T+45분, T+24h)
3. **개입 트리거 감지 시 즉시 Kill-Switch 사용**

**어떤 시점이든 문제 발생 시:**
```bash
bash scripts/evolution/l4_killswitch.sh recover   # 일시 차단
bash scripts/evolution/l4_killswitch.sh rollback   # 완전 롤백
```

---

**시작일**: 2025-11-04  
**목표**: L4.0 "자율 복구 및 무인 운영"  
**상태**: 🚀 타임라인 기반 능동 모니터링 준비 완료
