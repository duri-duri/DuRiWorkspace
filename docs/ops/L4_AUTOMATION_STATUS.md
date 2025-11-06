# L4 자동화 시스템 현황

## 완전 자동화 상태

L4 시스템은 **사용자 개입 없이** 완전 자동으로 동작합니다.

## 자동화된 기능

### 1. 일일 관찰 루프
- **트리거**: `l4-daily.timer` (매일 09:11 KST)
- **실행**: `l4_daily_runner.sh` → `l4_daily_observation.sh`
- **작업**:
  - 운영 체크리스트 실행
  - L4 평가 스크립트 실행
  - SLO 메트릭 쿼리
  - 감사 로그 일관성 확인
  - 정책 학습 PR 확인
- **결과**: `var/audit/logs/daily_*.log`에 자동 기록
- **사용자 개입**: **불필요**

### 2. 주간 요약 및 판정
- **트리거**: `l4-weekly.timer` (매주 일요일 16:00 KST)
- **실행**: `l4_weekly_runner.sh` → `l4_weekly_summary.sh` → `l4_post_decision.sh`
- **작업**:
  - 주간 점수 계산 (자동)
  - 판정 생성 (APPROVED/CONTINUE/REVIEW/HOLD) (자동)
  - 인간 행동 가이드 생성 (자동)
  - NDJSON/JSON 스냅샷 생성 (자동)
  - Prometheus 메트릭 업데이트 (자동)
  - 스톱룰 체크 (자동)
- **결과**: 
  - `var/audit/logs/weekly_*.log`
  - `var/audit/decisions.ndjson`
  - `var/audit/decisions/*.json`
  - Prometheus textfile 메트릭
- **사용자 개입**: **불필요**

### 3. 정규화 시스템
- **트리거**: `l4-canonicalize.timer` (매시간)
- **실행**: `l4_canonicalize_ndjson.sh`
- **작업**:
  - NDJSON 정렬 (ts,seq 기준)
  - 중복 제거
  - 디렉터리 fsync
- **사용자 개입**: **불필요**

### 4. 그림자 재생
- **트리거**: `l4-shadow-replay.timer` (09:30, 21:30 KST)
- **실행**: `l4-shadow-replay.service`
- **작업**: 데이터 공백 자동 해소
- **사용자 개입**: **불필요**

### 5. 데일리 퀵체크
- **트리거**: `l4-daily-quick.timer` (매일 09:10 KST)
- **실행**: `l4_daily_quick_check.sh`
- **작업**: HOLD 상태 24h 내 감지
- **사용자 개입**: **불필요**

## 사용자 개입이 필요한 경우

### 초기 설정 (한 번만)
1. 환경 변수 설정:
   ```bash
   bash /tmp/l4_final_env_fix.sh  # 위에서 생성된 스크립트
   ```
   또는 수동으로:
   ```bash
   systemctl --user edit l4-weekly.service
   # [Service] 섹션에 추가:
   # Environment=NODE_EXPORTER_TEXTFILE_DIR=/var/lib/node_exporter/textfile_collector
   ```

2. 타이머 활성화 (이미 완료):
   ```bash
   systemctl --user enable --now l4-*.timer
   ```

### 비상 상황 (필요 시)
1. 전체 중단:
   ```bash
   systemctl --user stop l4-*.timer
   ```

2. 개별 재시작:
   ```bash
   systemctl --user restart l4-weekly.service
   ```

## 자동화 보장

- 모든 타이머는 `Persistent=true`로 설정되어 재부팅 후에도 자동 재시작
- Linger 활성화로 사용자 로그아웃 후에도 계속 실행
- 환경 변수는 systemd drop-in으로 고정되어 재부팅 후에도 유지
- 모든 결정은 자동 생성되며 사용자 승인 불필요

## 모니터링 (선택적)

사용자는 **선택적으로** 다음을 확인할 수 있습니다:

```bash
# 일일 검증 (30초)
bash scripts/ops/l4_validation.sh

# 최신 결정 확인
jq -cr '. | {ts,decision,score}' var/audit/decisions.ndjson | tail -5

# Prometheus 메트릭 확인
cat ${NODE_EXPORTER_TEXTFILE_DIR}/l4_weekly_decision.prom
```

하지만 **자동화는 계속 동작**합니다.

## 결론

**"켜두기만 하면" 되는 시스템입니다.**

- 7일간 사용자 개입 **불필요**
- 모든 결정 **자동 생성**
- 모든 로그 **자동 기록**
- 모든 메트릭 **자동 수집**

단지 초기 설정만 한 번 완료하면, 이후 완전 자동으로 동작합니다.

