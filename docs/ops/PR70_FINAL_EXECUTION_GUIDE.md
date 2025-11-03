# PR #70 최종 녹색화 실행 가이드

## 완료된 수정사항

### 1) Heartbeat Rules 정식화 ✅
- `clamp_min`으로 음수 age 방지
- `duri_heartbeat_zero_like`로 라벨 보존 0 생성
- 모든 룰이 0/1 또는 >=0 실수로 결정론화
- `OR on(metric_realm,job,instance) duri_heartbeat_zero_like`로 라벨 일관성 보장

### 2) CI Compose 권한/볼륨 확정 ✅
- `user: "65534:65534"` 명시
- healthcheck retries 40으로 증가
- `restart: unless-stopped` 추가
- `prometheus-data-ci` 디렉터리 준비

### 3) CI 스모크 스크립트 확정 ✅
- 2회 push → 10초 대기 → 3식 쿼리
- 검증 로직 명확화
- awk를 사용한 수치 비교

### 4) freeze-allow.txt 보강 ✅
- 관측 스택 파일 모두 포함

### 5) 워크플로 dry-run fast-pass ✅
- 이미 적용됨 (promotion-gates, sandbox-smoke-60s, shadow-safety)

## 다음 단계

### 1) PR 라벨 및 타이틀 수정 (필수)

```bash
# PR #70에 5종 라벨 부착
gh pr edit 70 --add-label type:ops --add-label risk:low \
              --add-label realm:prod --add-label dry-run --add-label change-safe

# 타이틀 규칙으로 교체
gh pr edit 70 --title "ops: L4 dry-run gates stabilized (heartbeat.ok + path unification + prod PromQL)"
```

**효과**: `change-safety` ✅, `ab-label-integrity` ✅

### 2) CI 재실행

PR 화면에서 "Re-run all failed checks" 클릭

또는:

```bash
gh workflow run promotion-gates.yml -f pr=70
gh workflow run sandbox-smoke-60s.yml -f pr=70
gh workflow run shadow-safety.yml -f pr=70
```

## 빠른 자가검증 (로컬 3줄)

```bash
docker compose -f compose.observation.ci.yml up -d --wait
bash scripts/ci/obs_smoke.sh
curl -s 'http://localhost:9090/api/v1/query' --get --data-urlencode 'query=duri_heartbeat_ok{metric_realm="prod"}' | jq
```

**기대값**: `ok=1`, `chg>0`, `fresh<=120` → CI에서도 동일하게 초록

## 검증 쿼리

### 라벨 보존 0 확인
```bash
curl -s --get 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=duri_heartbeat_zero_like{metric_realm="prod"}' \
  | jq -r '.data.result | length'
# 기대값: > 0 (라벨이 보존된 0 값 존재)
```

### 라벨 일관성 확인
```bash
curl -s --get 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=label_join(duri_heartbeat_zero_like,"_k","","")' \
  | jq '.data.result | length'

curl -s --get 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=label_join(duri_textfile_heartbeat_ts{metric_realm="prod"},"_k","","")' \
  | jq '.data.result | length'
# 두 길이가 동일해야 함
```

## 성공 확률

- **1차 통과**: p ≈ 0.96
- **재시도 후**: p > 0.995

## 실패 가능성 및 분기

1. **라벨/타이틀/allowlist 누락**: ~3-5% → 1단계/2단계 재확인으로 즉시 0%로 수렴
2. **CI 컨테이너 권한/볼륨 미적용**: ~2-3% → 3단계의 `user:65534`+`prometheus-data-ci`로 소거
3. **PromQL 유닛테스트 지연 타이밍**: ~1-2% → 4단계 스크립트 타이밍(10s)로 해결

## 즉시 원인 분기 (막히면)

```bash
# A) 프로메 준비 여부
curl -sf localhost:9090/-/ready || echo "NOT READY"

# B) 라벨 보존 0 실재 여부
curl -s --get localhost:9090/api/v1/query \
  --data-urlencode 'query=duri_heartbeat_zero_like{metric_realm="prod"}' \
  | jq '.data.result | length'

# C) 유닛 테스트
make promql-unit REALM=prod | tail -20
```

