# L4.0 승급 실행 가이드 - 최종 버전

## 개요

**현 위치**: L3.9±0.1  
**목표**: L4.0 "자율 복구 및 무인 운영"  
**예상 성공 확률**: p≈0.85 (보안 하드닝 후 p≈0.88)

## 즉시 실행 (원클릭)

```bash
# 원클릭 승급 실행
bash scripts/evolution/execute_l4_promotion.sh
```

이 스크립트는:
1. 사전 AC 체크 (자동)
2. 최종 하드닝 + 회귀
3. 상태/무결성 확인
4. 증거 스냅샷 + 기준선 태깅
5. L4.0 Gate 검증 (6/6)
6. L4.0 승급 실행
7. 즉시 검증 (5분 셋)
8. 24h 드릴 시작
9. L4.1 준비 (태스크 큐 시드)

## 합격 기준 (AC1~AC6)

### AC1: 감시·자율
- `coldsync-install.path` = enabled/active
- `coldsync-verify.timer` = enabled/active

### AC2: 무결성
- 운영본↔작업본 SHA256 완전 일치
- 최근 로그에 `INSTALLED` 또는 `No change`

### AC3: 자가복구
- `prometheus/rules/coldsync_autofix.rules.yml` 로드됨
- `promtool check rules` 통과

### AC4: 권한 봉쇄
- `ProtectSystem=strict`
- `NoNewPrivileges=yes`
- `CapabilityBoundingSet=` (빈)
- `ReadOnlyPaths/ReadWritePaths` 일치

### AC5: 게이트 6/6
- `verify_l4_gate.sh` 출력에 Gate1~6 모두 PASS

### AC6: 증거 기록
- `snapshot_coldsync_security.sh` 산출물 존재
- `tag_coldsync_baseline.sh` 태그가 git에 존재

**필요충분조건**: AC1~AC6 모두 PASS → L4.0 선언 가능

## 단계별 실행 (원클릭 실패 시)

```bash
# 1. 최종 하드닝 + 회귀
bash scripts/bin/finalize_coldsync_autodeploy.sh
bash scripts/bin/test_coldsync_autodeploy.sh

# 2. 상태/무결성 확인
bash scripts/bin/status_coldsync_oneline.sh
bash scripts/bin/verify_coldsync_final.sh

# 3. 증거 스냅샷 + 기준선 태깅
bash scripts/bin/snapshot_coldsync_security.sh
bash scripts/bin/tag_coldsync_baseline.sh

# 4. L4.0 게이트 검증→선언
bash scripts/evolution/verify_l4_gate.sh
bash scripts/evolution/promote_to_l4.sh
```

## 즉시 관측

```bash
# 빠른 체크
bash scripts/evolution/quick_l4_check.sh

# 또는 개별 실행
systemctl is-active coldsync-verify.timer && systemctl is-active coldsync-install.path
grep -h '"decision"' var/evolution/EV-*/gate.json | tail
sha256sum /usr/local/bin/coldsync_hosp_from_usb.sh ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
```

## 실패 모드 Top3 → 즉시 교정

### 1. 타이머 미활성/미존재
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now coldsync-verify.timer || true
sudo systemctl enable --now coldsync-install.path || true
```

### 2. 권한/경로 충돌
```bash
# /var/lib/coldsync-hosp 누락
sudo mkdir -p /var/lib/coldsync-hosp && sudo chmod 755 /var/lib/coldsync-hosp

# 유닛 수정 후 재로드
sudo systemctl daemon-reload
sudo systemctl restart coldsync-install.service
```

### 3. 룰 구문 오류/미적용
```bash
promtool check rules prometheus/rules/*.yml
sudo systemctl restart prometheus || true
```

## 롤백

### 일시 차단
```bash
bash scripts/bin/recover_coldsync.sh
```

### 완전 롤백
```bash
bash scripts/bin/rollback_coldsync.sh
```

## L4.1로의 미분적 상승

### 즉시 Δ (7일 내 p≈0.62 목표)

```bash
# 큐 시드 태스크 주입 (구현 필요)
python3 scripts/evolution/task_queue.py enqueue obs-rule-tune '{}'
python3 scripts/evolution/task_queue.py enqueue config-patch '{}'
python3 scripts/evolution/task_queue.py enqueue doc-to-pr '{}'
```

### 민감도 (정규화)
- ∂prom_score/∂(자율 주기 실행) ≈ **0.24**
- ∂prom_score/∂(실패시 교정 큐) ≈ **0.15**
- ∂prom_score/∂(doc→Draft-PR 자동화) ≈ **0.08**

## 선언 템플릿

```
[DECLARE L4.0]
AC1..AC6 = PASS
Hash一致, Self-heal rules=Loaded, Gate(6/6)=PASS, Snapshot+Tag=OK
Decision = PROMOTE_TO_L4.0 (p=0.85→0.88 w/ hardening)
Next = L4.1 loop (auto-run + corrective queue + doc→PR)
```

## 목표 SLO (28일 롤링)

- Drift MTTR p95 ≤ **120s**
- Drift 발생률 ≤ **0.5/day**
- Human intervention rate **0**
- Gate pass rate ≥ **0.98**

## 24h 드릴 목표

- `PROMOTE ≥ 1` & `ROLLBACK = 0`
- `stability ≥ 0.90`, `halluc_rate ≤ 0.08`
- 게이트 점수 `G ≥ 0.70` **연속 2회** 달성 시 L4.1 선언 준비

---

**시작일**: 2025-11-04  
**목표**: L4.0 "자율 복구 및 무인 운영"  
**상태**: 🚀 승급 실행 준비 완료

