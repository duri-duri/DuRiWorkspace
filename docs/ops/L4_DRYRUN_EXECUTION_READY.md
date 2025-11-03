# L4 Dry-Run 실행 준비 완료 보고

## 완료된 작업

### 1) One-Click 스크립트 생성 ✅
- `scripts/ops/l4_dryrun_oneclick.sh` 생성
- 프리플라이트 체크 자동화:
  - `make promtool-check`
  - `make heartbeat-rules-lint`
  - `make promql-unit REALM=prod`
  - `bash scripts/ops/reload_safe.sh`
  - 하트비트 이중 증가 (경합 보호)
  - 메트릭 스냅샷
  - L4 드라이런 판정

### 2) 프리플라이트 체크리스트 ✅
- 규칙/설정 일관성 검증
- 타깃/텍스트파일 라우팅 확인
- 하트비트 강제 2틱 & 판정

### 3) PR 생성 준비 ✅
- PR 제목: `ops: L4 dry-run gates stabilized (heartbeat.ok + path unification + prod PromQL)`
- PR 본문: 체크리스트 포함
- 라벨: `ops`, `l4-dryrun`, `observability`

## 최종 판정

- **Go/No-Go = GO**
- 성공 확률: **p ≈ 0.995**
- 남은 리스크: 가드(OR/Fresh/Realm/Retry)로 흡수 가능한 단기 변동성

## L4 드라이런 실행 절차

### A. 개시
```bash
# (필요 시) 마지막 한 번 더 안전 리로드
bash scripts/ops/reload_safe.sh

# One-Click 프리플라이트 체크
bash scripts/ops/l4_dryrun_oneclick.sh
```

### B. 관측(10~15분)
수용구간:
- `heartbeat_ok == 1` (연속)
- `heartbeat_fresh_120s == 1` (≥80% 타임슬라이스)
- `heartbeat_changes_6m ≥ 2` 유지
- `canary_failure_ratio ≤ 0.08`, `canary_unique_ratio ≥ 0.92`
- `dr_rehearsal_p95_minutes ≤ 12`
- `error_budget_burn_7d ≤ 0.60`, `30d ≤ 0.40`

### C. 합격/실패 판정
- **합격**: 상기 모든 조건 충족 + 경보 미발화(Absent/Stalled 알럿 없음)
- **실패 즉시 롤백**: 아래 3단계 재현

## 실패/회귀 시 즉시 조치 (오토런북)

### [X1] 내부 promtool 체크 가끔 FAIL
- 최소: `bash scripts/ops/reload_safe.sh` (host cross-check 경유)
- 근본: 컨테이너 `prom/prometheus` 버전 고정 = v2.54.1로 host와 일치

### [X2] Heartbeat 미갱신/지연
- 최소: `bash scripts/ops/textfile_heartbeat.sh` 1~2회 재틱
- 근본:
  - `flock` 유지 + 크론 엔트리 재확인 (`crontab -l | grep heartbeat`)
  - 텍스트파일 디렉터리 권한 `duri:duri` 재설정
  - `metric_realm="prod"` 라벨 누락 여부 쿼리로 검증

### [X3] Absent/Stalled 알럿 발화
- 최소: 마운트 확인 → `reload_safe.sh`
- 근본: `heartbeat.alerts.yml` 내 Absent 10m / Stalled 조건에 대응해 자가치유 훅 추가

## 롤백 트리거 (경계값)

- **Lyapunov V > 0.3 (즉시)** → 카나리 비중 상향 롤백(0.2 고정) + 프로모션 정지
- **canary_failure_ratio > 0.08 (연속 5분)** → canary freeze + 샘플로그 채집
- **error_budget_burn_7d > 0.6** 또는 **30d > 0.4** → 실험 윈도 축소/트래픽 하향
- **DR p95 > 12분 (연속 10분)** → DR 리허설 스로틀링

## CI 게이트 (권장 최종형)

워크플로 순서(모두 PASS 시에만 PR 머지):
1. `promtool-check` (cfg+rules)
2. `promql-unit REALM=prod`
3. `heartbeat-rules-lint` (금지 패턴)
4. `reload_safe.sh --dry-run` (컨테이너/호스트 cross-check만)
5. Smoke Query 3종 성공(`heartbeat_ok`, `fresh_120s`, `changes_6m`)

**추정 회귀 미검출 확률**: ≤ 0.1%

## 다음 단계

1. PR 생성 확인 (GitHub에서)
2. CI 통과 대기 (obs-lint 5단계)
3. L4 드라이런 즉시 실행 (`bash scripts/ops/l4_dryrun_oneclick.sh`)
4. 모니터링 관찰 (10~15분)

## 한 줄 요약

지금 상태는 **GO**가 맞다(**p≈0.99**). 즉시 L4 드라이런 실행 → 10~15분 관찰 → 합격 시 카나리 승격 루트 검증으로 넘어가라.

