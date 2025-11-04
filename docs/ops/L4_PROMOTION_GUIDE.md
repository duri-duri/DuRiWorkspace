# L4.0 승급 절차 - 실행 가이드

## 개요

**현 위치**: L3.9±0.1  
**목표**: L4.0 "자율 복구 및 무인 운영"  
**예상 성공 확률**: p≈0.85 (보안 하드닝 후 p≈0.88)

## 즉시 실행

```bash
# 원클릭 승급 절차
bash scripts/evolution/promote_to_l4.sh
```

이 스크립트는:
1. 브랜치 생성 (`ops/coldsync-l4-gate`)
2. L4.0 Gate 검증 (6/6)
3. 프로모션 스코어 확인 (7일)
4. L4.0 선언 및 태깅 (`l4-coldsync-go-YYYYMMDD`)

## L4.0 Gate 조건 (6/6 통과 필요)

### Gate 1: 자가복구 (Δ1)
- 조건: `sha256(src)!=sha256(dst)` 상태가 2분 지속되면 자동 재설치→해시 일치
- 증거: 알람→재설치 로그→일치 해시가 **2분 내** 확인

### Gate 2: 권한·경로 봉쇄 (Δ2)
- 조건: `sudoers` 화이트리스트 외 명령/경로 시도 시 100% 차단 + 감사 로그
- 증거: 금지 경로 시도 테스트에서 **설치본 미변경**, 로그에 차단 기록
- 보안 하드닝: `RestrictNamespaces`, `PrivateDevices`, `DevicePolicy`, `IPAddressDeny`, `UMask=0077`

### Gate 3: Plan→Exec→Verify→Report 체인 (Δ3)
- 조건: 최근 실행 10건 **pass_rate ≥ 0.97**, 실패는 10분 내 롤백
- 증거: `plans/plan_coldsync.jsonl` 실행 시 검증 3종 통과

### Gate 4: 타이머 백스탑
- 조건: Path 감지가 죽어도 `coldsync-verify.timer`가 **2분 주기**로 무결성 확인 및 복구
- 증거: inotify 의도적 차단 후에도 타이머 경로로 복구 성공

### Gate 5: 프로모션 스코어
- 조건: 지난 7일 `promotion_score ≥ 0.82`, `pass_rate_7d ≥ 0.98`, `safety_incident==0`
- 증거: `promotion_gate_v2.py --window 7d` 출력 스냅샷

### Gate 6: 무인 운영 지표
- 조건: `human_intervention_rate == 0` (최근 24h), MTTR(알람→복구) ≤ 2분
- 증거: Shadow Runner/Gate Executor 로그 + Grafana 패널 캡처

## 보안 하드닝 추가 (선택)

```bash
# Δ2 신뢰도 +0.03
bash scripts/evolution/harden_l4_security.sh
```

추가 항목:
- `RestrictNamespaces=yes`
- `PrivateDevices=yes`
- `DevicePolicy=closed`
- `IPAddressDeny=any`
- `UMask=0077`

## 운영 관측·가드

### 목표 SLO (28일 롤링)
- Drift MTTR p95 ≤ **120s**
- Drift 발생률 ≤ **0.5/day**
- Human intervention rate **0**
- Gate pass rate ≥ **0.98**

### 즉시 상태 확인

```bash
bash scripts/bin/status_coldsync_oneline.sh
```

### 24h 드릴

```bash
bash scripts/evolution/l4_operational_drill.sh
```

또는 개별 실행:
```bash
bash scripts/bin/verify_coldsync_final.sh
bash scripts/bin/snapshot_coldsync_security.sh
bash scripts/bin/tag_coldsync_baseline.sh
```

## 비상시 복구

### 즉시 차단 (일시 롤백)

```bash
bash scripts/bin/recover_coldsync.sh
```

### 완전 롤백 (원상복구)

```bash
bash scripts/bin/rollback_coldsync.sh
```

## 리스크 테이블

| 증상 | 원인 추정 | 즉각 조치 |
|------|----------|-----------|
| 드리프트 복구 실패 | timer 죽음/권한 | `systemctl start coldsync-verify.timer` → `verify_coldsync_final.sh` |
| 차단 로그 無 | service 하드닝 누락 | `harden_l4_security.sh` 재실행 후 Δ2 재시험 |
| pass<0.98 | 플랜 flaky | 실패 case만 재실행, 10회 중 불안정 플랜 격리 |
| SHA equal인데 재설치 반복 | 해시 산출 경로 중복 | `monitor_coldsync_sha.sh` 메트릭 확인→ 중복 타깃 제거 |

## 검증 프로토콜 (T1~T5)

### T1: 드리프트 복구
```bash
sudo sed -i '1i# drift-test' /usr/local/bin/coldsync_hosp_from_usb.sh
sleep 150
sha256sum /usr/local/bin/coldsync_hosp_from_usb.sh ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
sudo journalctl -u coldsync-install.service -n 30 --no-pager
```

### T2: 금지 경로 차단
```bash
sudo bash -lc 'cp /etc/hosts /usr/local/bin/coldsync_hosp_from_usb.sh' || echo "[OK] blocked"
```

### T3: 체인 통과율
```bash
bash scripts/evolution/verify_l4_gate.sh | grep "Gate 3"
```

### T4: inotify 다운
```bash
systemctl stop coldsync-install.path
sleep 150
sha256sum /usr/local/bin/coldsync_hosp_from_usb.sh ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
systemctl start coldsync-install.path
```

### T5: Gate 점수
```bash
python3 scripts/evolution/promotion_gate_v2.py --window 168 --gate L4.1 --print
```

## 다음 단계

L4.0 승급 후:
1. L4.1 진화 시스템 가동: `bash scripts/evolution/start_l4_evolution.sh`
2. Day21: systemd 타이머 + 태스크 큐 연결
3. L4.1 목표: p≈0.62 (7일 내)

---

**시작일**: 2025-11-04  
**목표**: L4.0 "자율 복구 및 무인 운영"  
**상태**: 🚀 승급 준비 완료

