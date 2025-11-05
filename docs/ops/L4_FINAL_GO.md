# L4.0 승급 실행 최종 가이드 - 강화 버전 (p≈0.90)

## 핵심 원칙

**GO 상태 유지** → **실패 여지 4곳 조임** → **p≈0.88 → p≈0.90 상향** → **실행+판정만**

## 즉시 실행

### 0) 프리플라이트 (원클릭)

```bash
cd /home/duri/DuRiWorkspace
bash scripts/evolution/preflight_l4.sh
```

**기대값:**
- `AC 스냅샷 OK`
- `path/timer enabled/active`
- `SHA256 match==true`
- `[L4] ✅ GO`

### 1) 원클릭 실행 (백그라운드) + 즉시 스팟체크

```bash
# 창1: 타임라인 실행 (백그라운드 또는 tmux)
tmux new -d -s l4 'bash scripts/evolution/run_l4_timeline.sh'

# 또는 직접 실행
bash scripts/evolution/run_l4_timeline.sh

# 창2: 즉시 스팟체크
bash scripts/evolution/spotcheck_l4.sh
```

**통과 기준:**
- `spotcheck_l4.sh` 출력에 **FAILED/MISMATCH/ROLLBACK=0** 이어야 함

### 2) 동시 모니터링 (두 창)

**창2:**
```bash
watch -n5 'bash scripts/evolution/spotcheck_l4.sh'
```

**창3:**
```bash
journalctl -u coldsync-install.service -f --no-pager | egrep --line-buffered 'FAILED|SHA256|ROLLBACK|MISMATCH|halluc|stability'
```

## 체크포인트에서만 판정

### T+2분: 초기 AC

```bash
bash scripts/evolution/check_l4_timeline.sh T2
```

**통과 기준:**
- `coldsync-install.path` / `coldsync-verify.timer` = **enabled/active**
- 저널에 `INSTALLED|No change` 1회↑
- `SHA256 mismatch 0`

### T+15분: SLO/게이트 요약

```bash
bash scripts/evolution/check_l4_timeline.sh T15
bash scripts/evolution/quick_l4_check.sh
```

**통과 기준:**
- `path/timer = active`
- `INSTALLED|No change` 확인됨
- `SHA256 mismatch 0`
- `Gate 1~4 PASS`, 에러버짓/알람=정상

### T+24h: 안착 판정

```bash
bash scripts/evolution/check_l4_timeline.sh T24h
bash scripts/evolution/check_l4_settlement.sh
```

**안착 기준:**
- `PROMOTE ≥ 1`, `ROLLBACK = 0`
- `stability ≥ 0.90`, `halluc_rate ≤ 0.08` (연속 2 윈도우)
- 게이트 점수 `G ≥ 0.70` (2회 연속)

**확정 태깅/기준선 고정:**
```bash
bash scripts/bin/snapshot_coldsync_security.sh
bash scripts/bin/tag_coldsync_baseline.sh && git push --tags
bash scripts/evolution/declare_l4.sh
```

## 개입 트리거 (보이면 즉시)

다음 조건이 감지되면 즉시 개입:

- `SHA256 MISMATCH ≥1`
- `halluc_rate>0.10`
- `stability<0.85`
- `PROMOTE=0 & ROLLBACK≥1`가 **2윈도 연속**

**개입 명령:**

```bash
bash scripts/evolution/l4_killswitch.sh recover    # 일시 차단
bash scripts/evolution/l4_killswitch.sh rollback   # 완전 롤백
```

## 스모크 테스트 (선택, 30초)

### Path 트리거 검증

```bash
# 설치기 동작 스모크: 소스 타임스탬프만 갱신해 path 트리거
touch -d 'now' scripts/bin/finalize_coldsync_autodeploy.sh
sleep 2
journalctl -u coldsync-install.service -n 60 --no-pager | egrep 'INSTALLED|No change|FAILED' || true
```

### 롤백 루틴 스모크 (논파괴)

```bash
# recover만 호출 후 즉시 복원
bash scripts/bin/recover_coldsync.sh && sleep 1 && bash scripts/bin/verify_coldsync_final.sh
```

## 빠른 정합성 점검 (선택, 30초)

```bash
# 실행 파일 존재/권한
ls -l scripts/bin/{finalize_coldsync_autodeploy.sh,test_coldsync_autodeploy.sh,status_coldsync_oneline.sh,verify_coldsync_final.sh,snapshot_coldsync_security.sh,recover_coldsync.sh,rollback_coldsync.sh,tag_coldsync_baseline.sh} \
      scripts/evolution/{preflight_l4.sh,run_l4_timeline.sh,check_l4_timeline.sh,spotcheck_l4.sh,quick_l4_check.sh,verify_l4_gate.sh,promote_to_l4.sh,execute_l4_promotion.sh} | awk '{print $1,$9}'

# systemd 상태 요약
systemctl status coldsync-install.path --no-pager | sed -n '1,5p'
systemctl status coldsync-verify.timer --no-pager | sed -n '1,5p'

# SHA 추적 로그 핵심 키워드
journalctl -u coldsync-install.service --since -15min --no-pager | egrep 'INSTALLED|No change|SHA256|MISMATCH|FAILED' | tail -n 20
```

## Prometheus 규칙 문법 체크 (있으면 좋음)

```bash
docker run --rm -v "$PWD/prometheus/rules:/rules:ro" prom/prometheus:v2.54.1 promtool check rules /rules/coldsync_autofix.rules.yml
```

## 알려진 함정 → 즉시 해결

### 이름 혼동

문서에 `status_coldsync_autodeploy.sh`가 섞여 있음. 실제 파일은 `status_coldsync_oneline.sh`. 혼동 방지용 alias 권장:

```bash
ln -sf status_coldsync_oneline.sh scripts/bin/status_coldsync_autodeploy.sh
git add -A && git commit -m "alias: status_coldsync_autodeploy -> oneline"
```

### 과도 트리거

WSL2에서 inotify 폭주 시 `No change`가 과다 발생하면, `verify.timer` 주기를 2분→5분으로 상향:

```bash
sudo systemctl edit coldsync-verify.timer
# [Timer] 섹션에 OnUnitActiveSec=5min 로 오버라이드, 이후:
sudo systemctl daemon-reload && sudo systemctl restart coldsync-verify.timer
```

### SystemCallFilter/MemoryDenyWriteExecute

특정 배포판/WSL 커널에서 막히면, 일시적으로 `SystemCallFilter=@system-service`만 남기고 재시도.

## 최종 판정 함수 (원클릭 GO/NO-GO)

```bash
bash scripts/bin/verify_coldsync_final.sh && \
bash scripts/evolution/check_l4_ac.sh && echo "[L4] ✅ GO" || echo "[L4] ❌ NO-GO"
```

## 성공 확률 (보수적 추정)

- 현재 구성: **p≈0.85**
- 보안 하드닝/타이머 튜닝 후: **p≈0.88**
- 강화된 프리플라이트 + 타임라인 절차 준수: **p≈0.90**
- 실패 조기감지·손실 최소화: **p≈0.97**

## 요약

1. **프리플라이트**: `bash scripts/evolution/preflight_l4.sh`
2. **타임라인 실행**: `bash scripts/evolution/run_l4_timeline.sh`
3. **최소 감시**: `watch -n5 'bash scripts/evolution/spotcheck_l4.sh'`
4. **체크포인트**: T+2분, T+15분, T+24h에만 수동 확인
5. **트리거 시**: 즉시 Kill-Switch 사용

---

**시작일**: 2025-11-04  
**목표**: L4.0 "자율 복구 및 무인 운영"  
**상태**: 🚀 GO 상태 - 강화된 프리플라이트 완료 (p≈0.90)
