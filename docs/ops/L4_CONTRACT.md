# L4 Automation Contract

## 불변식(Invariants)

이 문서는 L4 자동화 시스템의 핵심 불변식을 정의합니다. 이 불변식은 시스템의 올바른 동작을 보장하며, 위반 시 시스템은 자동으로 복구되거나 경고를 발생시킵니다.

### 1. 입력 불변식 (Input Invariant)
- **정의**: `var/audit/decisions.ndjson`은 "한 줄 = 한 JSON 객체" 형식이어야 합니다.
- **보장**: 손상 라인은 정규화 단계(`ndjson_canonicalize.sh`)에서 폐기됩니다.
- **검증**: `fromjson?`로 파싱 실패 시 자동 드랍.

### 2. 해석 불변식 (Interpretation Invariant)
- **정의**: 최근 7일 내 유효 decision 집합에서 UTC 시각으로 가장 최근 1건만 반환합니다.
- **보장**: `sort_by(.ts, .seq) | group_by(.ts) | map(last)`로 최신 1건만 선택.
- **검증**: 출력은 항상 단일 스칼라 문자열입니다.

### 3. 출력 불변식 (Output Invariant)
- **정의**: `l4_weekly_decision_ts{decision="<ESCAPED>"} <UNIX_UTC>` 형식으로 출력됩니다.
- **보장**: 라벨 값은 따옴표/역슬래시 이스케이프 후 단일 라벨로 출력됩니다.
- **검증**: `decision ∈ {GO, NO-GO, REVIEW, HOLD, HEARTBEAT, APPROVED, CONTINUE}` 허용집합 보장.

### 4. 동시성 불변식 (Concurrency Invariant)
- **정의**: 같은 소스 파일을 다루는 모든 경로는 동일 락(`decisions.ndjson.lock`)을 사용합니다.
- **보장**: `with_lock.sh`를 통한 배타적 접근.
- **검증**: 동시 실행 시 락 대기 또는 건너뛰기.

### 5. 테스트 불변식 (Test Invariant)
- **정의**: "로그 문자열"이 아니라 "UTC Δ ≤ 120s"로 합격/불합격을 판단합니다.
- **보장**: 절대값 변환, 상한 캡 600s, 합격선 120s 유지. ζ(scrape_interval + 1s) 보정 적용.
- **검증**: `effective_delta = |time() - l4_weekly_decision_ts| - ζ ≤ 120s`로 검증.

### 6. 관측 불변식 (Observability Invariant)
- **정의**: 최소 4종 지표가 항상 노출되어야 합니다.
  - `l4_weekly_decision_ts`: 주간 결정 타임스탬프
  - `l4_canon_total{}` / `l4_canon_bad{}`: 정규화 통계
  - `l4_backfill_last_rc{}`: 백필 결과 코드 (0=ok, >0=error)
  - `l4_boot_status{}`: 부팅 상태 (0/1)
- **보장**: 각 스크립트가 종료 시 Prometheus textfile 형식으로 메트릭 노출.
- **검증**: Prometheus scrape 주기 내 신선도 확인 및 알람 규칙 적용.

## 검증 방법

각 불변식은 다음 방법으로 검증됩니다:

1. **입력 불변식**: `ndjson_canonicalize.sh` 실행 시 파싱 실패 라인 자동 드랍
2. **해석 불변식**: `backfill_weekly.sh` 실행 시 단일 스칼라 출력 확인
3. **출력 불변식**: `validate_weekly_prom.sh`로 형식, 라벨, 타임스탬프 검증
4. **동시성 불변식**: `with_lock.sh` 사용 확인
5. **테스트 불변식**: `l4_chaos_test.sh` A4 테스트에서 UTC Δ 검증

## 위반 시 조치

불변식 위반 시:

- **입력 불변식**: 손상 라인 자동 드랍 (정규화 단계)
- **해석 불변식**: 기본값 "HOLD" 반환
- **출력 불변식**: 검증 스크립트 FAIL
- **동시성 불변식**: 락 대기 또는 건너뛰기
- **테스트 불변식**: 카오스 테스트 A4 FAIL

## 최종 게이트(프로모션 조건)

### 24h 관찰 통과 → Dry-Run 승인
- `P(A1..A7 == PASS) ≥ 0.995` (롤링 24h)
- `P(A6_bad_ratio ≤ 0.01) ≥ 0.99` (롤링 7d)
- `P(|Δ| ≤ 120s) ≥ 0.995` (롤링 24h)

### 7d 연속 통과 → Promotion
- 누적 FAIL 0회
- `Δ` p95 ≤ 120s
- 정규화 후 중복 = 0

## 버전

- **생성일**: 2025-11-06
- **버전**: 1.1.0
- **상태**: Stable (L4 Finalize)

