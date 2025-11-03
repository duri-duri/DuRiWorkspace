# L4 24-Hour Monitoring 시작 체크리스트

## 완료된 작업

### 1. 프리플라이트 체크 ✅
- `make promtool-check`: OK
- `make heartbeat-rules-lint`: OK
- `bash scripts/ops/reload_safe.sh`: OK

### 2. 코드 스냅샷 고정 ✅
- Git tag 생성: `l4-dryrun-start-YYYYMMDD-HHMM`
- 원격 저장소에 push 완료

### 3. Prometheus TSDB 스냅샷 ✅
- 핫 스냅 생성 (skip_head=false)
- 백업 위치: `/home/duri/BACKUP/prometheus/prom_tsdb_${SNAP_ID}_*.tar.gz`
- SHA256 체크섬 생성

### 4. 워크스페이스 원자 백업 ✅
- 압축 형식: tar.zst
- 백업 위치: `/home/duri/BACKUP/DuRiWorkspace_YYYYMMDD-HHMM.tar.zst`
- SHA256 체크섬 생성

### 5. 롤백용 체크포인트 ✅
- 체크포인트: `.reports/L4_START_COMMIT.txt`
- Git commit hash 저장

### 6. 24시간 모니터링 시작 ✅
- Screen 세션: `l4-monitor`
- 백그라운드 실행 중

## 모니터링 명령어

### 모니터링 상태 확인
```bash
# Screen 세션 확인
screen -list

# 모니터링 로그 확인
tail -f var/logs/l4_24h_monitor.log

# Screen 세션 접속
screen -r l4-monitor
```

### 중간 점검
```bash
cd /home/duri/DuRiWorkspace

# 통계 분석
bash scripts/ops/l4_24h_stats.sh

# 판정 스크립트 실행
bash scripts/ops/l4_dryrun_decision.sh
```

### 핵심 메트릭 확인
```bash
for q in duri_heartbeat_ok duri_heartbeat_fresh_120s duri_lyapunov_v; do
  curl -s --get 'http://localhost:9090/api/v1/query' --data-urlencode "query=$q" \
  | jq -r '.data.result[]?.value[1] // "N/A"' | awk -v q="[$q]" '{print q, $0}'
done
```

## 롤백 방법 (필요 시)

### 코드 롤백
```bash
cd /home/duri/DuRiWorkspace
git reset --hard "$(cat .reports/L4_START_COMMIT.txt)"
git clean -fd
```

### Git tag 확인
```bash
git tag -l "l4-dryrun-start-*"
git checkout <tag-name>
```

### Prometheus TSDB 복구 (필요 시)
```bash
# 컨테이너 정지
docker stop prometheus

# 스냅샷 복구
cd /home/duri/BACKUP/prometheus
tar -xzf prom_tsdb_*.tar.gz

# Prometheus 데이터 디렉터리에 복사
# (컨테이너 볼륨 마운트 경로 확인 필요)

# 컨테이너 재시작
docker start prometheus
```

## 모니터링 중단 (ABORT)

### 자동 중단 조건
- Lyapunov V > 0.3
- 지속적 위반 (≥ 2회 연속)

### 수동 중단
```bash
screen -S l4-monitor -X quit
```

## 24시간 후 판정

```bash
cd /home/duri/DuRiWorkspace

# 통계 분석
bash scripts/ops/l4_24h_stats.sh

# 판정 기준
# - Lyapunov V 평균 ≤ 0.2 → L4.9 승격
# - Lyapunov V 평균 ≤ 0.3 → L4.7 유지
# - Lyapunov V 평균 > 0.3 → 조사 필요
```

## 예상 결과

- 현재: L3.7 (p ≈ 0.995)
- 24시간 후 목표: L4.9 (p ≈ 0.999)
- 샘플 수: 8640 (변동폭 ~1/9로 감소)

## 한 줄 요약

**백업 완료 + 24시간 모니터링 시작됨. 24시간 후 통계 분석 및 판정.**

