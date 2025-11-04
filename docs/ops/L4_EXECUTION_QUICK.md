# L4.0 실행 및 최소 감시 가이드 - 실전 버전

## 핵심 원칙

**자동화가 대기·검증을 처리** → **다른 작업 하면서 세 포인트만 확인** → **트리거 시 즉시 개입**

## 즉시 실행 (3줄)

```bash
cd /home/duri/DuRiWorkspace
bash scripts/bin/status_coldsync_oneline.sh        # 사전 스냅샷
bash scripts/evolution/run_l4_timeline.sh          # 타임라인 자동 실행
```

## 작업하면서 보는 최소 감시 (두 창)

### 1. 5초 주기 원라인 감시

```bash
watch -n5 'bash scripts/evolution/spotcheck_l4.sh'
```

**이 창에서 확인:**
- 서비스/타이머 상태
- 게이트 결정 추적
- 개입 트리거 체크

### 2. 이상 신호 로그

```bash
journalctl -u coldsync-install.service -f --no-pager | egrep --line-buffered 'FAILED|SHA256|ROLLBACK|MISMATCH|halluc|stability'
```

**이 창에서 확인:**
- 실패/에러 메시지
- SHA256 불일치
- ROLLBACK 발생
- halluc/stability 이상

## 개입 트리거 (넘으면 즉시 버튼)

다음 조건이 감지되면 즉시 개입:

- `halluc_rate > 0.10` **또는** `stability < 0.85`
- `ROLLBACK > 0` 발생
- **SHA256 불일치** 탐지
- 게이트 스코어 `G < 0.70` **또는** `PROMOTE=0 & ROLLBACK≥1`가 **2윈도우 연속**

**개입 명령:**

```bash
bash scripts/evolution/l4_killswitch.sh recover    # 일시 차단 (빠른 안전)
bash scripts/evolution/l4_killswitch.sh rollback   # 완전 롤백
```

## 체크포인트만 수동 확인

### T+2분: AC 즉시검증

```bash
bash scripts/evolution/check_l4_timeline.sh T2
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

### T+24h: 안착 판정

```bash
bash scripts/evolution/check_l4_timeline.sh T24h
bash scripts/evolution/check_l4_settlement.sh
```

**안착 기준:**
- ✅ `PROMOTE ≥ 1`, `ROLLBACK = 0`
- ✅ `stability ≥ 0.90`, `halluc_rate ≤ 0.08` (연속 2 윈도우)
- ✅ 게이트 점수 `G ≥ 0.70` (2회 연속)

**확정 태깅/기준선 고정:**
```bash
bash scripts/bin/snapshot_coldsync_security.sh
bash scripts/bin/tag_coldsync_baseline.sh && git push --tags
bash scripts/evolution/declare_l4.sh
```

## 실전 워크플로우

### 1. 시작 (터미널 1)

```bash
cd /home/duri/DuRiWorkspace
bash scripts/bin/status_coldsync_oneline.sh
bash scripts/evolution/run_l4_timeline.sh
```

### 2. 최소 감시 (터미널 2, 3)

**터미널 2:**
```bash
watch -n5 'bash scripts/evolution/spotcheck_l4.sh'
```

**터미널 3:**
```bash
journalctl -u coldsync-install.service -f --no-pager | egrep --line-buffered 'FAILED|SHA256|ROLLBACK|MISMATCH|halluc|stability'
```

### 3. 체크포인트 확인 (필요 시)

- **T+2분**: `bash scripts/evolution/check_l4_timeline.sh T2`
- **T+15분**: `bash scripts/evolution/check_l4_timeline.sh T15`
- **T+24h**: `bash scripts/evolution/check_l4_timeline.sh T24h`

### 4. 트리거 발생 시 즉시 개입

```bash
bash scripts/evolution/l4_killswitch.sh recover    # 일시 차단
# 또는
bash scripts/evolution/l4_killswitch.sh rollback   # 완전 롤백
```

## 판단

- **기본 성공 확률**: p≈0.85 (보안 하드닝 후 p≈0.88)
- **위 감시 두 개만 돌려두면**: 대기 시간에 다른 일 해도 안전
- **트리거 뜨면**: 즉시 `recover` 또는 `rollback`으로 개입

## 빠른 참조

### Kill-Switch 상태 확인
```bash
bash scripts/evolution/l4_killswitch.sh status
```

### 빠른 스팟체크
```bash
bash scripts/evolution/spotcheck_l4.sh
```

### 실패 후 재시도
```bash
bash scripts/bin/recover_coldsync.sh
bash scripts/bin/finalize_coldsync_autodeploy.sh
bash scripts/evolution/execute_l4_promotion.sh
```

## 요약

1. **실행**: `bash scripts/evolution/run_l4_timeline.sh`
2. **최소 감시**: 두 창 실행 (watch + journalctl)
3. **체크포인트**: T+2분, T+15분, T+24h에만 수동 확인
4. **트리거 시**: 즉시 Kill-Switch 사용

**핵심**: 자동화가 대기·검증을 처리하니, 다른 작업 하면서 세 포인트만 확인하면 됩니다.

---

**시작일**: 2025-11-04  
**목표**: L4.0 "자율 복구 및 무인 운영"  
**상태**: 🚀 실전 실행 준비 완료

