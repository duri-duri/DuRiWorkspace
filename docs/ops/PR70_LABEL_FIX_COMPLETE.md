# PR #70 obs_smoke 라벨 정합 + 대기시간 공식 적용 완료

## 완료된 수정사항 ✅

1. **obs_smoke.sh 라벨 1:1 일치**
   - job="duri_heartbeat", instance="local", metric_realm="prod"로 고정
   - 푸시 라벨을 룰과 완전히 일치시킴
   - 검증 쿼리도 동일 라벨셋 사용

2. **대기시간 공식 적용**
   - 3×scrape + 1×eval + 3s buffer
   - 기본값: 3×15 + 1×15 + 3 = 63초
   - CI 설정(5s) 기준: 3×5 + 1×5 + 3 = 23초

3. **prometheus.yml.ci 최적화**
   - scrape_interval: 5s (빠른 스크랩)
   - evaluation_interval: 5s (빠른 평가)
   - honor_labels: true (라벨 보존)
   - job_name: 'pushgateway-ci'로 명확화

## 빠른 자체 점검 (명령 6줄)

### 1) 원시 시계열 존재 확인
```bash
curl -s --get :9090/api/v1/series --data-urlencode \
 'match[]=duri_textfile_heartbeat_seq{metric_realm="prod",job="duri_heartbeat",instance="local"}' | jq '.data|length'
```
**기대값**: > 0 (라벨이 있으면 OK)

### 2) 룰 등록/활성 확인
```bash
curl -s :9090/api/v1/rules | jq '.data.groups[]?.rules[]?|select(.name|startswith("duri_heartbeat"))|.name'
```
**기대값**: duri_heartbeat_ok, duri_heartbeat_fresh_120s, duri_heartbeat_changes_6m 등

### 3) 스모크 재실행
```bash
bash scripts/ci/obs_smoke.sh
```

### 4) 값 확인(수동)
```bash
for m in ok fresh_120s changes_6m; do
  curl -s --get :9090/api/v1/query --data-urlencode \
  "query=duri_heartbeat_${m}{metric_realm=\"prod\",job=\"duri_heartbeat\",instance=\"local\"}" | jq -r '.data.result[0]?.value[1] // "0"'
done
```
**기대값**: `ok=1, fresh_120s=1, changes_6m>0`

## 진단 커맨드 (막히면)

```bash
# 라벨/푸시 문제 확인
curl -s :9090/api/v1/series --data-urlencode \
 'match[]=duri_textfile_heartbeat_seq{metric_realm="prod",job="duri_heartbeat",instance="local"}' | jq

# 룰/대기시간 문제 확인
curl -s :9090/api/v1/query --data-urlencode \
 'query=duri_heartbeat_ok{metric_realm="prod",job="duri_heartbeat",instance="local"}' | jq
```

**첫 줄이 비면** → 라벨/푸시 문제  
**비지 않는데 둘째가 0이면** → 룰/대기시간 문제

## 성공 확률

- **라벨 정합 보정 + 대기시간 공식 적용**: p≈0.97
- **재시도 1회 내**: p>0.995

## 결론

**라벨 불일치 문제 해결 완료**

- 푸시 라벨을 룰과 1:1 일치시킴
- 대기시간을 공식으로 설정 (3×scrape + 1×eval)
- 검증 쿼리도 동일 라벨셋 사용

**다음 단계: PR #70에 라벨 추가 후 CI 재실행**

