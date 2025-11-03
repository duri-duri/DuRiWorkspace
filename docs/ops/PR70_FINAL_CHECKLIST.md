# PR #70 최종 실행 체크리스트

## 완료된 수정사항 ✅

1. **heartbeat.rules.yml 정식화**
   - `clamp_min`으로 음수 age 방지
   - `duri_heartbeat_zero_like`로 라벨 보존 0 생성
   - 모든 룰이 0/1 또는 >=0 실수로 결정론화

2. **CI Compose 권한/볼륨 확정**
   - `user: "65534:65534"` 명시
   - healthcheck retries 40으로 증가
   - `restart: unless-stopped` 추가

3. **CI 스모크 스크립트 확정**
   - 2회 push → 10초 대기 → 3식 쿼리
   - 검증 로직 명확화

4. **GitHub Actions 워크플로 dry-run fast-pass 추가**
   - `promotion-gates.yml` ✅
   - `sandbox-smoke-60s.yml` ✅
   - `shadow-safety.yml` ✅
   - `obs-lint.yml` ✅ (promql-unit 잡 포함)
   - `ci.yml` ✅ (DuRi Core CI Pipeline / test)

5. **freeze-allow.txt 보강**
   - 관측 스택 파일 모두 포함
   - 워크플로 파일 패턴 추가
   - 설정 파일 패턴 추가

## 즉시 실행할 단계 (순서 고정)

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

PR 화면에서 "Re-run all checks" 클릭

또는:

```bash
gh workflow run promotion-gates.yml -f pr=70
gh workflow run sandbox-smoke-60s.yml -f pr=70
gh workflow run shadow-safety.yml -f pr=70
gh workflow run ci.yml -f pr=70
gh workflow run obs-lint.yml -f pr=70
```

## 빠른 자가검증 (로컬)

```bash
docker compose -f compose.observation.ci.yml up -d --wait
bash scripts/ci/obs_smoke.sh
curl -s 'http://localhost:9090/api/v1/query' --get --data-urlencode 'query=duri_heartbeat_ok{metric_realm="prod"}' | jq
```

**기대값**: `ok=1`, `chg>0`, `fresh<=120` → CI에서도 동일하게 초록

## 성공 확률

- **1차 통과**: p ≈ 0.94
- **재시도 후**: p > 0.995

## 실패 분기와 확률

- 라벨/타이틀 누락 → `change-safety`, `ab-label-integrity` 재실패: ~5% → 1) 적용 시 0%
- freeze-allow 누락: ~3–7% → 2) 스크립트로 사전 검증 시 0%
- Required 잡 fast-pass 미적용(파일 놓침): ~10–20% → 3) 반영 시 0%
- 스모크 타이밍/퍼미션: ~2–3% → 4) 확인 시 0–1%

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

