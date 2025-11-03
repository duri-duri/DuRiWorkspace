# DuRi 4-Axis Strengthening Plan

## 📊 현재 판정

- **관찰 스택**: GREEN 잠금 완료 (P≈0.997)
- **취약점**: 
  1. 수동 FREEZE_BYPASS 의존
  2. 관찰-자기치유-자기진화 루프 L2 수준 (사람 개입 多)
  3. 백업 훌륭하지만 복원/검증 자동 정량화 약함

---

## 🎯 4개 축 및 미분적 접근

### 1) 안정성/거버넌스 (Repo & CI/CD) - "사고가 안 나게"

**목표**: FREEZE 없이도 항상 머지·릴리스가 안전하게 흐르도록

**미분적 효과**:
- `∂P(GREEN 24h)/∂MergeQueue` ≈ +0.003 ~ +0.008
- `∂P(릴리스 리스크)/∂FREEZE_BYPASS차단` ≈ -0.4 ~ -0.6

**즉시 조치**:
- ✅ 서버 pre-receive에 FREEZE_BYPASS 차단 추가
- ✅ obs-lint에 sandbox 60s 스모크 추가

---

### 2) 관찰·자기치유 (Ops) - "고장 나도 스스로 복귀"

**목표**: MTTD ≤ 2분, MTTR ≤ 5분

**미분적 효과**:
- `∂P(GREEN 24h)/∂Heartbeat_v2` ≈ +0.002 ~ +0.003
- `∂MTTR/∂Auto-reload_guard` ≈ -40% ~ -60%

**즉시 조치**:
- ✅ Textfile Heartbeat v2 (seq, pid, exit code)
- ✅ Stall 자동 재기동 룰
- ✅ Auto-reload guard (롤백 훅)

**기대 효과**: P(GREEN 24h) 0.997 → 0.999–0.9993, MTTR 12–20분 → ≤ 5분

---

### 3) 자기진화 루프 (L2→L3) - "사람 보조 → 사람 승인형 자율"

**목표**: 제안·패치·검증·PR의 70% 이상 자동화

**미분적 효과**:
- `∂EV/h/∂KS_p` ≈ +0.35 (최대 영향)
- `∂EV/h/∂unique_ratio` ≈ +0.30
- `∂EV/h/∂sigma` ≈ +0.20

**즉시 조치**:
- ✅ shadow_generate.sh (약점 분석)
- ✅ shadow_validate.sh (샌드박스 검증)
- ✅ auto_pr.py (자동 PR 생성)

**기대 효과**: EV/h +0.25 (30일) → +0.4~+0.6 (90일)

---

### 4) 백업·복구의 "증명(Provable DR)" - "있다"가 아니라 "된다"

**목표**: RPO ≤ 15분, RTO ≤ 10분 증명, 복원 성공률 ≥ 0.999

**미분적 효과**:
- `∂RTO/∂DR_rehearsal` ≈ -50% ~ -70%
- `∂DR_success_rate/∂Daily_rehearsal` ≈ +0.01 ~ +0.02

**즉시 조치**:
- ✅ dr_rehearsal.sh (일일 복원 리허설)
- ✅ DR 메트릭 노출 (RTO, success_ratio)

**기대 효과**: RTO 25–40분 → ≤ 10분, DR 실패율 주당 1회 → 월간 ≤ 1회

---

## 📋 실행 로드맵

### D+7 (즉시 효과)
1. ✅ FREEZE_BYPASS 서버차단
2. ✅ obs-lint에 sandbox 60s 스모크 추가
3. ✅ Heartbeat v2 + Stall 자동재기동
4. ✅ DR 리허설 잡 1개 가동

**지표 목표**: P(GREEN 24h) ≥ 0.999, MTTR ≤ 8분

### D+30 (구조화)
5. L3 Shadow-Generator/Validator/Auto-PR 1차 완성
6. DR 카오스+복원 시나리오 3종 상시화
7. EV/h Δ기여를 PR 본문에 자동 표준화

**지표 목표**: EV/h +0.2 이상, DR 성공률 ≥ 0.995, RTO p95 ≤ 10분

### D+90 (진화 가속)
8. 데이터셋 자동 확장, Validator에 통계적 검정 포함
9. Merge Queue 완전무인 (사람 승인만)
10. 월간 "프로빙 릴리스" 트랙 (카나리 1~5%)

**지표 목표**: EV/h +0.4~+0.6, P(GREEN 30d) ≥ 0.995, RPO ≤ 15분

---

## 🎯 정량 전망 (보수적)

- **P(GREEN 24h)**: 0.997 → **0.999–0.9993**
- **EV/h**: +0.25 (30일) → **+0.4~+0.6 (90일)**
- **MTTR**: 12–20분 → **≤ 5–8분**
- **DR 성공률**: 0.98 → **≥ 0.999 (90일)**

---

## 📝 생성된 파일

1. `.git/hooks/pre-receive` - FREEZE_BYPASS 차단
2. `.github/workflows/obs-lint.yml` - sandbox smoke 추가
3. `scripts/ops/textfile_heartbeat.sh` - v2 (seq, pid, exit)
4. `scripts/ops/dr_rehearsal.sh` - DR 리허설 자동화
5. `scripts/ops/evolution/shadow_generate.sh` - L3 생성
6. `scripts/ops/evolution/shadow_validate.sh` - L3 검증
7. `scripts/ops/evolution/auto_pr.py` - L3 PR 생성

---

## 🔧 다음 단계

1. **cron 등록**:
   ```bash
   */5 * * * * cd /home/duri/DuRiWorkspace && bash scripts/ops/textfile_heartbeat.sh
   0 2 * * * cd /home/duri/DuRiWorkspace && bash scripts/ops/dr_rehearsal.sh
   ```

2. **Prometheus 리로드**:
   ```bash
   curl -X POST http://localhost:9090/-/reload
   ```

3. **GitHub Merge Queue 설정** (수동):
   - Repository Settings → Branches → Add rule
   - Require: obs-lint, promtool-check, sandbox-smoke

4. **L3 파이프라인 테스트**:
   ```bash
   bash scripts/ops/evolution/shadow_generate.sh
   bash scripts/ops/evolution/shadow_validate.sh <patch_file>
   python3 scripts/ops/evolution/auto_pr.py <validation_file>
   ```

