# L4.0 실행 최종 가이드 - 실행+판정만

## 핵심 원칙

**아티팩트·가이드 전부 갖춰짐** → **실행+판정만** → **말 길게 안 함**

## 0) 마지막 3점 고정 (30초)

```bash
cd /home/duri/DuRiWorkspace
bash scripts/evolution/finalize_l4_preflight.sh
```

**기대값:**
- 유닛 상태 확인됨
- 해시 일치 (또는 아직 설치되지 않음)
- status_coldsync_oneline.sh 존재/실행권한 OK

## 1) 사전 스냅샷 (≤1분)

```bash
bash scripts/evolution/preflight_l4.sh
```

**기대값:**
- AC 표시가 모두 **OK**
- `[L4] ✅ GO`
- 성공 확률 p≈0.90

## 2) 타임라인 실행 + 즉시 스팟체크

```bash
# 백그라운드 실행
tmux new -d -s l4 'bash scripts/evolution/run_l4_timeline.sh'

# 또는 직접 실행
bash scripts/evolution/run_l4_timeline.sh

# 즉시 스팟체크
bash scripts/evolution/spotcheck_l4.sh
```

**기대값:**
- `FAILED=0`
- `MISMATCH=0`
- `ROLLBACK=0`

## 3) 동시 모니터링 (두 창)

**창2:**
```bash
watch -n5 'bash scripts/evolution/spotcheck_l4.sh'
```

**창3:**
```bash
journalctl -u coldsync-install.service -f --no-pager | egrep --line-buffered 'FAILED|SHA256|ROLLBACK|MISMATCH|halluc|stability'
```

## 4) 단 두 번의 판정 포인트

### T+2분: 초기 AC

```bash
bash scripts/evolution/check_l4_timeline.sh T2
```

**통과 기준 (필수):**
- `coldsync-install.path` / `coldsync-verify.timer` → enabled/active
- journal에 `INSTALLED` 또는 `No change` ≥1회
- `SHA256 mismatch == 0`

### T+15분: SLO/게이트 요약

```bash
bash scripts/evolution/check_l4_timeline.sh T15
bash scripts/evolution/quick_l4_check.sh
```

**통과 기준 (필수):**
- `path/timer = active`
- `INSTALLED|No change` 확인됨
- `SHA256 mismatch == 0`
- quick 체크에서 Gate 1~4 PASS

### T+24h: 안착 후 마감

```bash
bash scripts/evolution/check_l4_settlement.sh && \
bash scripts/bin/snapshot_coldsync_security.sh && \
bash scripts/bin/tag_coldsync_baseline.sh && git push --tags
```

## 5) 개입 트리거 (보이면 즉시)

다음 조건이 감지되면 즉시 개입:
- `SHA256 MISMATCH`
- `halluc_rate>0.10`
- `stability<0.85`
- `PROMOTE=0 & ROLLBACK≥1` (2윈도우 연속)

**개입 명령:**

```bash
bash scripts/evolution/l4_killswitch.sh recover     # 일시 차단
bash scripts/evolution/l4_killswitch.sh rollback    # 완전 롤백
```

## 원클릭 판정 (바로 결론만 보고 싶을 때)

```bash
bash scripts/bin/verify_coldsync_final.sh && \
bash scripts/evolution/check_l4_ac.sh && echo "[L4] ✅ GO" || echo "[L4] ❌ NO-GO"
```

## 빠른 함정 교정 (필요 시만)

### 1. 이름 혼재

```bash
ln -sf status_coldsync_oneline.sh scripts/bin/status_coldsync_autodeploy.sh
git add -A && git commit -m "alias: status_coldsync_autodeploy -> oneline"
```

### 2. WSL2 inotify 과다 트리거

```bash
sudo systemctl edit coldsync-verify.timer
# [Timer]에 OnUnitActiveSec=5min 추가 후:
sudo systemctl daemon-reload && sudo systemctl restart coldsync-verify.timer
```

### 3. SystemCallFilter/MDWE 충돌

`MemoryDenyWriteExecute=yes` 유지가 어렵다면 일시 비활성 → 재시험.

## 결론

- 현 상태: **GO 권고** (p≈0.90)
- 위 순서대로 돌리고 `T+2 / T+15 / T+24h`만 판정하면 됨
- 실패시 손실은 Kill-Switch로 즉시 제한 가능

---

**시작일**: 2025-11-04  
**목표**: L4.0 "자율 복구 및 무인 운영"  
**상태**: 🚀 GO - 실행+판정만 남음

