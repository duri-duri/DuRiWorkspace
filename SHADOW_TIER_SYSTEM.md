# Shadow Tier 시스템 가이드

## 📋 개요

Shadow 시스템을 **3단계 Tier**로 관리하여 목적에 맞는 활성화 강도를 선택합니다.

- **Tier-0**: 온디맨드 (기본, 안전)
- **Tier-1**: 파일럿 (하이브리드, 실험)
- **Tier-2**: 상시 풀가동 (보류)

## 🎯 Tier별 특징

### Tier-0: 온디맨드 모드 (권장 기본)

**목적**: 운영 안정·재현성이 1순위

**특징**:
- HTTP 기본 전송
- 수동 실행만 (온디맨드)
- 주기적 건강검진 (자동)
- 카오스 주입 비활성화
- 카나리 제어기 비활성화

**사용 시기**:
- 일상 운영
- 안정성 우선
- 리스크 최소화

**실행 방법**:
```bash
# 온디맨드 실행
bash scripts/shadow_ondemand.sh

# 또는 직접
TRANSPORT=http bash scripts/shadow_duri_integration_final.sh
```

### Tier-1: 파일럿 모드 (48시간 파일럿 권장)

**목적**: 하이브리드 활성화 (HTTP 기본 + SSH 플러그인)

**특징**:
- HTTP 기본 + SSH 플러그인 (30%)
- 하이브리드 전송 지원
- 게이트 체크 자동 수행
- 카오스 주입 비활성화
- 파일럿 KPI 수집

**사용 시기**:
- 48시간 파일럿 실험
- 하이브리드 효과 검증
- 점진적 활성화 테스트

**실행 방법**:
```bash
# 파일럿 실행
bash scripts/shadow_pilot.sh

# 또는 직접
TRANSPORT=mixed SSH_CANARY=0.30 bash scripts/shadow_duri_integration_final.sh
```

### Tier-2: 상시 풀가동 모드 (보류)

**목적**: 자율 진화/탐색력이 1순위

**특징**:
- 자동 카나리 제어기
- 상시 가동
- 카오스 주입 활성화
- 완전 자동화

**사용 시기**:
- Tier-1 파일럿 성공 후
- 장기 진화 실험
- 최대 탐색력 필요 시

**실행 방법**:
```bash
# Tier-2 전환 (주의)
bash scripts/shadow_tier_manager.sh set 2
```

## 🛠️ Tier 관리

### Tier 상태 확인

```bash
bash scripts/shadow_tier_manager.sh status
```

### Tier 전환

```bash
# Tier-0로 전환 (온디맨드)
bash scripts/shadow_tier_manager.sh set 0

# Tier-1로 전환 (파일럿)
bash scripts/shadow_tier_manager.sh set 1

# Tier-2로 전환 (상시 풀가동)
bash scripts/shadow_tier_manager.sh set 2
```

### KPI 판정 (48시간 파일럿)

```bash
bash scripts/shadow_tier_manager.sh kpi
```

**판정 기준** (4개 지표 중 3개 이상 통과):
1. Evidence Velocity: ≥24 EV/일
2. 알림 경보 수: 0건
3. Exporter 실패율: <0.5%
4. CPU 사용률: <70%

**판정 결과**:
- **3개 이상 통과** → Tier-1 유지 (부분 활성화 지속)
- **2개 이하** → Tier-0 전환 (온디맨드)

## 📊 48시간 파일럿 체크리스트

### 1. 게이트 체크

```bash
bash scripts/shadow_gate_check.sh
```

### 2. 파일럿 시작

```bash
# 파일럿 실행
bash scripts/shadow_pilot.sh

# 또는 직접
TRANSPORT=mixed SSH_CANARY=0.30 bash scripts/shadow_duri_integration_final.sh
```

### 3. 측정 KPI (자동 수집)

```bash
# KPI 자동 수집 및 판정
bash scripts/shadow_tier_manager.sh kpi
```

**수동 확인**:
```bash
# Evidence Velocity
find var/evolution -maxdepth 1 -type d -name "EV-*" -mtime -1 | wc -l

# 유의 EV 비율 (HTTP vs SSH 차이)
# evidence_score.sh 결과 파싱 필요

# 알림 경보
curl -s http://localhost:9090/api/v1/alerts | grep ABTestPValueEdgeCase | wc -l

# Exporter 실패율
curl -s http://localhost:9109/metrics | grep duri_shadow_exporter_up

# CPU 사용률
top -bn1 | grep "Cpu(s)"
```

### 4. 판정

- **3개 이상 개선** → Tier-1 유지
- **2개 이하** → Tier-0 전환

## 🚀 최소 실행 (10분)

### 1. 주기 점검 타이머 (건강검진) - Tier-0

```bash
# systemd user timer 생성
mkdir -p ~/.config/systemd/user

# Timer 정의
cat > ~/.config/systemd/user/shadow-health.timer <<EOF
[Unit]
Description=Shadow health check

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Service 정의
cat > ~/.config/systemd/user/shadow-health.service <<EOF
[Unit]
Description=Run shadow_check_health

[Service]
Type=oneshot
ExecStart=$HOME/DuRiWorkspace/scripts/shadow_check_health.sh --verbose
EOF

# 활성화
systemctl --user daemon-reload
systemctl --user enable --now shadow-health.timer
```

### 2. 온디맨드 실행 에일리어스 (파일럿 편의)

```bash
# ~/.bashrc에 추가
cat >> ~/.bashrc <<'EOF'

# Shadow 온디맨드 실행
alias shadow-http='cd $HOME/DuRiWorkspace && TRANSPORT=http bash scripts/shadow_duri_integration_final.sh'
alias shadow-ssh='cd $HOME/DuRiWorkspace && TRANSPORT=ssh CORE_SSH=127.0.0.1:2220 bash scripts/shadow_duri_integration_final.sh'
alias shadow-pilot='cd $HOME/DuRiWorkspace && bash scripts/shadow_pilot.sh'
alias shadow-kpi='cd $HOME/DuRiWorkspace && bash scripts/shadow_tier_manager.sh kpi'
EOF

source ~/.bashrc
```

### 3. 증거 일치성 스폿체크

```bash
# EV 번들 생성 및 점수 계산
bash scripts/evolution/evidence_bundle.sh
bash scripts/evolution/evidence_score.sh

# HTTP p-value 확인
curl -fsS http://localhost:9109/metrics | awk "/^duri_ab_p_value/{print \$2; exit}"

# FILE p-value 확인
awk "/^duri_ab_p_value/{print \$2; exit}" var/metrics/ab_eval.prom
```

## 📈 활성화가 절대적으로 필요한 조건

다음 조건 중 하나 이상 충족 시 Tier-2 고려:

1. **자가진화/탐색 KPI 정체**
   - 유의 EV 비율(일) < 20% (p<0.05)로 7일 연속

2. **복원탄력성(회복력) 실험 필요**
   - 의도된 네트워크 실패/지연 포함 회귀 억제 목표

3. **신규 행동 축 필요**
   - 원격 실행/SSH 상호작용이 모델 품질에 직접 기여한다는 사전 가설

**위가 아니면 온디맨드 실행(Tier-0)이 합리적**

## 🔔 자동 전환 규칙

### Tier-0 → Tier-1 자동 전환 조건
- 게이트 체크 통과
- 사용자 명시적 요청

### Tier-1 → Tier-0 자동 전환 조건
- KPI 판정 실패 (4개 중 2개 이하 통과)
- 알림 경보 지속 (ABTestPValueEdgeCase 5분)
- 게이트 체크 실패

### Tier-1 → Tier-2 전환 조건
- 48시간 파일럿 성공
- 사용자 명시적 승인
- KPI 4개 모두 통과

## 📚 관련 문서

- [Shadow 훈련장 가이드](./SHADOW_TRAINING_GROUND.md)
- [카나리 활성화](./SHADOW_CANARY_ACTIVATION.md)
- [빠른 시작](./SHADOW_QUICKSTART.md)

---

**최종 업데이트:** 2025-10-31
**버전:** 1.0.0 (Tier 시스템 통합)

