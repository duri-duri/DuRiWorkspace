# DuRi 관찰 스택 완료 상태 저장 (2025-11-02)

## 📋 현재 상태

- **브랜치**: `fix/p-sigma-writer`
- **태그**: `obs-green-lock-20251102-1846`
- **상태**: GREEN 잠금 완료 (P≈0.992~0.997)

## ✅ 완료된 작업

1. **pre-receive 훅**: 서버측 템플릿 함수 금지 가드
   - 위치: `.git/hooks/pre-receive`
   - 기능: `humanize*` 함수 검사 + promtool 검증

2. **reload_safe 레이트리밋**:
   - 최소 간격: 30초
   - 지수 백오프: 최대 5회 재시도
   - 메트릭: `duri_prom_reload_retries` 추가

3. **textfile heartbeat**:
   - 스크립트: `scripts/ops/textfile_heartbeat.sh`
   - 메트릭: `duri_textfile_heartbeat`
   - Alert: `TextfileHeartbeatStall`

4. **연속성 카운터 Recording Rules**:
   - `duri_obs_green_run_counter`: 성공 묶음 카운터
   - `duri_obs_green_estimate`: Beta 추정

5. **Git 푸시 완료**:
   - 브랜치: `fix/p-sigma-writer`
   - 태그: `obs-green-lock-20251102-1846`

## 🔄 재시작 후 복원 절차

### 1. Git 상태 확인
```bash
cd /home/duri/DuRiWorkspace
git fetch origin
git status
git log --oneline -5
```

### 2. 브랜치 확인 및 전환
```bash
git branch -a | grep p-sigma-writer
git checkout fix/p-sigma-writer  # 또는 이미 해당 브랜치면 스킵
git pull origin fix/p-sigma-writer
```

### 3. 백업 확인
```bash
ls -lth /mnt/hdd/ARCHIVE/INCR/*.tar.zst | head -3
```

### 4. 관찰 스택 상태 확인
```bash
# Prometheus 상태
curl -s http://localhost:9090/-/ready && echo "OK" || echo "FAIL"

# Recording rules 활성화 확인
curl -s 'http://localhost:9090/api/v1/query' --data-urlencode 'query=duri_obs_green_run_counter' | jq -r '.data.result[0].value[1] // "0"'

# Textfile heartbeat 확인
cat reports/textfile/duri_textfile_heartbeat.prom 2>/dev/null || echo "(파일 없음)"
```

### 5. 선택적 작업 (필요 시)

#### cron job 설정 (textfile heartbeat)
```bash
crontab -l | grep textfile_heartbeat || echo "*/5 * * * * cd /home/duri/DuRiWorkspace && bash scripts/ops/textfile_heartbeat.sh" | crontab -
```

#### promtool 재검증
```bash
make promtool-check
```

#### Prometheus 리로드 (필요 시)
```bash
bash scripts/ops/reload_safe.sh
```

## 📊 주요 파일 위치

- **pre-receive 훅**: `.git/hooks/pre-receive`
- **reload_safe**: `scripts/ops/reload_safe.sh`
- **textfile heartbeat**: `scripts/ops/textfile_heartbeat.sh`
- **Recording rules**: `prometheus/rules/duri-observability-contract.rules.yml`
- **백업 위치**: `/mnt/hdd/ARCHIVE/INCR/`

## 🎯 다음 작업 (선택사항)

1. Grafana 패널 생성: `duri_obs_green_run_counter`, `duri_obs_green_estimate`
2. cron job 설정: textfile heartbeat 자동 실행
3. Beta 추정 대시보드 쿼리 작성

## 📝 참고

- 현재 상태는 Git에 커밋되어 있고 원격에도 푸시됨
- 백업도 완료되어 `/mnt/hdd/ARCHIVE/INCR/`에 저장됨
- 컴퓨터 재시작 후에도 위 절차를 따라 동일한 상태로 복원 가능

