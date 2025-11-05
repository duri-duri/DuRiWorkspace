# L4.0 승급 실행 가이드 - 최종 완전 자동화

## 개요

**현 위치**: L3.9±0.1  
**목표**: L4.0 "자율 복구 및 무인 운영"  
**예상 성공 확률**: p≈0.85 (보안 하드닝 후 p≈0.88)

## 즉시 실행 (원클릭)

```bash
# 완전 자동화 실행
bash scripts/evolution/run_l4_promotion.sh
```

**이 스크립트는:**
1. 프리플라이트 체크 (2분)
2. 원클릭 승급 실행
3. 즉시 검증 (15분 SLO)
4. 증거 스냅샷 & 기준선 고정
5. 24h 드릴 시작
6. 모니터링 가이드 출력

**실행 후**: 모니터링만 진행하면 됩니다!

## 모니터링 가이드

### 즉시 확인 (15분 SLO)

```bash
# 빠른 체크
bash scripts/evolution/quick_l4_check.sh

# 또는 5분 주기 대시보드
bash scripts/evolution/monitor_l4_dashboard.sh 300
```

**15분 수용 기준:**
- `path/timer = active (running)`
- 최근 로그에 `INSTALLED` 또는 `No change` 최소 1회
- `Gate(6/6)=PASS` 문구 확인
- SHA256 불일치 알람 0건

### 정기 확인 (5~10분 주기, 30분간)

```bash
# 5분마다 실행
watch -n 300 bash scripts/evolution/quick_l4_check.sh

# 또는 대시보드 모드
bash scripts/evolution/monitor_l4_dashboard.sh
```

### 24h 드릴 모니터링

```bash
# 실시간 로그
sudo journalctl -u coldsync-install.service -f

# 게이트 결정 추적
watch -n 60 'grep -h "decision" var/evolution/EV-*/gate.json | tail -10'

# 핵심 KPI 스냅샷
jq -s '
  def m(a): (add/length) as $avg | {avg:$avg, min:min, max:max};
  {p_at3:(.[].p_at3)|m(.), stability:(.[].stability)|m(.),
   halluc_rate:(.[].halluc_rate)|m(.), rollback:(.[].rollback)|m(.)}
' var/evolution/EV-*/metrics.json 2>/dev/null
```

### 24h 안착 기준 검증

```bash
# 24h 후 실행
bash scripts/evolution/check_l4_settlement.sh
```

**안착 기준:**
- `PROMOTE ≥ 1`, `ROLLBACK = 0`
- `stability ≥ 0.90`, `halluc_rate ≤ 0.08` (연속 2 윈도우)
- 게이트 점수 `G ≥ 0.70` (2회 연속)

## 실패 시 즉시 조치

### 일시 차단

```bash
bash scripts/bin/recover_coldsync.sh
```

### 완전 롤백

```bash
bash scripts/bin/rollback_coldsync.sh
```

### 원인 스냅샷

```bash
bash scripts/bin/snapshot_coldsync_security.sh
# 결과를 docs/ops/에 첨부
```

## L4.1 선언 준비 (7일 목표)

### 선언 트리거 (둘 다 충족)

1. 최근 48h `G ≥ 0.75` 지속
2. `error_budget_burn(7d) ≤ 0.25`, `rollback_count(7d)=0`

### 선언 절차

```bash
bash scripts/evolution/declare_l4.sh
bash scripts/bin/snapshot_coldsync_security.sh
bash scripts/bin/tag_coldsync_baseline.sh
```

## 점수 함수 미분 타깃

승격 함수:
```
G = 0.35·p@3 + 0.25·stability - 0.20·halluc - 0.20·rollback_rate + 0.10·autonomy
```

**민감도 (현 레인지 근사):**
- ∂G/∂p@3 ≈ **+0.35** (최대 레버)
- ∂G/∂stability ≈ **+0.25**
- ∂G/∂halluc ≈ **-0.20**
- ∂G/∂rollback ≈ **-0.20**

**즉시 개선 Δ 가이드 (24h 내 달성 가능):**
- p@3 +0.05 → ΔG≈+0.0175
- stability +0.03 → ΔG≈+0.0075
- halluc -0.02 → ΔG≈+0.004

## 확률 업데이트

- **L4.0 승급 성공**: p≈0.85 (하드닝 후 p≈0.88)
- **L4.1 (≤7일) 달성**: p≈0.62
- **24h 안착 실패 시 롤백 필요**: q≈0.10

## 실행 순서 요약

```bash
# 1. 완전 자동화 실행
bash scripts/evolution/run_l4_promotion.sh

# 2. 즉시 확인 (15분 SLO)
bash scripts/evolution/quick_l4_check.sh

# 3. 정기 모니터링 (5분 주기, 30분간)
bash scripts/evolution/monitor_l4_dashboard.sh 300

# 4. 24h 안착 기준 검증 (24h 후)
bash scripts/evolution/check_l4_settlement.sh

# 5. L4.1 선언 준비 (7일 목표)
bash scripts/evolution/declare_l4.sh
```

## FAQ

**Q: 실행 후 기다리기만 하면 되나요?**  
A: 네, 맞습니다. `run_l4_promotion.sh` 실행 후:
- 15분 SLO: `quick_l4_check.sh`로 확인
- 정기 모니터링: `monitor_l4_dashboard.sh`로 5분 주기 확인 (30분간)
- 24h 드릴: 자동으로 진행되며, `check_l4_settlement.sh`로 안착 기준 확인

**Q: 실패 시 어떻게 하나요?**  
A: 즉시 `recover_coldsync.sh` 또는 `rollback_coldsync.sh` 실행 후 로그 확인

**Q: L4.1 언제 선언하나요?**  
A: 24h 안착 기준 충족 후, 추가로 48h `G ≥ 0.75` 지속 시 선언 가능

---

**시작일**: 2025-11-04  
**목표**: L4.0 "자율 복구 및 무인 운영"  
**상태**: 🚀 실행 준비 완료 - **이제 실행하고 모니터링만 하면 됩니다!**

