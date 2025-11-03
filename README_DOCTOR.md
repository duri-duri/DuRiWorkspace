# DuRi Doctor: 자동 진단 및 수리 제안 시스템

## 개요

"덧대기" 방지와 자동 진단 체계 구축을 위한 단일 엔트리 진단 시스템입니다.

## 핵심 파일

- **`scripts/doctor.sh`**: 단일 진단 엔트리 (정량 지표→원인 추정→수정 가이드)
- **`gates.yml`**: 선언적 게이트 정의
- **`scripts/gate_check.sh`**: gates.yml과 doctor.sh 출력을 합쳐 pass/fail 판정
- **`tests/test_ab_variance.py`**: AB p-value 분산 테스트
- **`tests/test_ev_cadence.py`**: EV 생성 속도 테스트
- **`.cursorrules`**: Cursor 자동 제안 지침
- **`cursor-tasks.md`**: 자동 제안 태스크 목록
- **`config/duri.env`**: 단일 설정 원천

## 실행 순서

### 1. 진단 실행

```bash
bash scripts/doctor.sh
```

출력: 정량 지표, 원인 추정, 수정 가이드

### 2. 게이트 체크

```bash
bash scripts/gate_check.sh
```

출력: gates.yml 기준 pass/fail 판정

### 3. 테스트 실행

```bash
pytest -q tests/
```

또는 개별 실행:

```bash
python3 -m pytest tests/test_ab_variance.py -v
python3 -m pytest tests/test_ev_cadence.py -v
```

### 4. Shadow 워커 시작

```bash
bash scripts/start_shadow_2worker.sh
```

### 5. (선택) systemd timer 설치

```bash
sudo cp systemd/duri-pilot.* /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now duri-pilot.timer
```

## 게이트 임계값

`gates.yml`에서 정의:

- **EV velocity**: warn=2.5/h, pass=4.0/h
- **AB p-value**: require_variance=true, min_samples=10, p_threshold=0.05
- **Shadow epoch**: p50≤360s, p95≤720s
- **DB consistency**: expected_db=duri_db
- **Last EV age**: warn=3600s, fail=7200s

## Cursor 활용

### 자동 제안

1. `.cursorrules` 파일을 읽어 진단 우선순위와 수정 원칙 적용
2. `cursor-tasks.md`의 태스크 템플릿으로 공통 이슈 해결
3. `scripts/doctor.sh` 실행 후 결과 기반 수정 제안

### 태스크 예시

- `[Task] EV cadence < 2.5/h`: 파일럿 주기, 워커 병렬화 확인
- `[Task] AB p-value constant`: 입력 분기, RNG seed, 캐시 제거
- `[Task] Shadow epoch p95 > 12m`: 병렬화, 타임아웃, 병목 분석

## 운영 고정화 원칙

1. **단일 설정 원천**: `config/duri.env`에 모든 설정 집약
2. **상태 머신화**: `pilot_24h.sh`에서 `STATE=(IDLE→HARVEST→EVAL→BUNDLE→PUSH)` 출력
3. **캐시 무력화**: EV별 작업 전 `rm -f $EV/ab_eval.*` 강제
4. **메트릭 상수 알람**: `ABPValueConstant` 5분당 3회 발생 시 "하드 게이트 FAIL"

## 성공 판정 기준

- EV_1h ≥ 2.5 (warning), ≥4.0 (pass)
- AB p-value 분산 > 0 (unique_vals ≥ 2)
- Shadow epoch p50 ≤ 6분, p95 ≤ 12분
- DB 일관성 (duri_db 사용)
- 파일럿 프로세스 실행 중

## 문제 해결

### EV cadence < 2.5/h

```bash
# 1. 파일럿 주기 확인
grep "MIN_GAP_SEC\|MAX_GAP_SEC" scripts/pilot_24h.sh

# 2. 워커 프로세스 확인
pgrep -fa "shadow_parallel_worker\|pilot_24h"

# 3. 워커 시작
bash scripts/start_shadow_2worker.sh
```

### AB p-value constant

```bash
# 1. 입력 경로 확인
grep "\--input" scripts/evolution/evidence_bundle.sh

# 2. RNG seed 확인
grep "combined_seed" scripts/evolution/make_ab_eval_prom_min.py

# 3. 캐시 제거 (주의: 기존 EV 삭제)
find var/evolution -name "ab_eval.prom" -delete
```

### Shadow epoch p95 > 12m

```bash
# 1. 병렬화 확인
pgrep -fa "shadow_parallel_worker" | wc -l

# 2. Bundle 비동기화 확인
grep "BUNDLE_ASYNC" scripts/shadow_duri_integration_final.sh

# 3. 타임아웃 확인
grep "BUNDLE_TIMEOUT" scripts/evolution/evidence_bundle.sh
```

## 참고

- 모든 스크립트는 `config/duri.env`에서 설정을 읽습니다.
- `scripts/doctor.sh`를 먼저 실행하여 상태를 파악하세요.
- `cursor-tasks.md`에서 공통 이슈의 수정 체크리스트를 확인하세요.

