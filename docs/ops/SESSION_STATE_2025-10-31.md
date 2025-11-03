# 작업 세션 상태 저장 (2025-10-31)

## 📋 오늘 작업 요약

### 1. 백업 체계 정리
- **문서화 완료**: `docs/ops/BACKUP_SYSTEM.md`
- **3단계 백업 체인**: HDD 증분 → USB 미러 (G: Ventoy) → HOSP/HOME 콜드 백업
- **자동 실행**: systemd 타이머 (매일 02:30)
- **G: 드라이브 마운트**: 자동 마운트 스크립트 (`scripts/_mount_g.sh`, `scripts/_umount_g.sh`)

### 2. pgbouncer 인증 문제 해결
- **문제**: Postgres 내부에 `postgres` 롤이 없음 + pgbouncer 인증 설정 불일치
- **해결 방법**: 
  - Single-user 모드로 슈퍼유저 `pgbouncer_auth` 생성
  - `auth_query` 방식으로 전환 (userlist.txt 없이 Postgres에서 직접 인증 정보 조회)
  - 앱 전용 계정 `duri_core` 생성 및 권한 부여
  - `postgres` 롤 생성 (로그 소음 제거)

### 3. Shadow Training Ground
- **24h 파일럿**: 진행 중
- **비동기 emotion 처리**: 202 Accepted + job_id 확인 완료
- **EV 생성**: 정상 작동

---

## 🔧 현재 시스템 상태

### Docker 컨테이너
- **duri-postgres**: healthy
- **duri-pgbouncer**: healthy (auth_query 방식 활성화)
- **duri-core**: healthy (202 경로 정상)
- **duri-brain**: healthy
- **기타 DuRi 노드**: 정상

### pgbouncer 설정
- **auth_type**: `scram-sha-256`
- **auth_user**: `pgbouncer_auth`
- **auth_query**: `SELECT usename, passwd FROM pg_shadow WHERE usename = $1`
- **admin_users**: `pgbouncer_auth`

### DB 롤 상태
- **pgbouncer_auth**: 슈퍼유저 (인증 전용)
- **duri_core**: 앱 전용 계정 (최소 권한)
- **postgres**: 일반 로그인 롤 (헬스체크용)

### 백업 상태
- **HDD 증분 백업**: 자동 실행 중 (systemd 타이머)
- **USB 미러**: G: Ventoy 드라이브 (`/mnt/g/두리백업/latest/`)
- **HOSP 트리거**: USB 미러 완료 시 자동 실행

---

## 📝 중요 파일 및 설정

### 백업 관련
- **메인 백업 스크립트**: `scripts/duri_backup.sh`
- **USB 미러 스크립트**: `scripts/run_usb_mirror_to_cold.sh`
- **HOSP 콜드 백업**: `/usr/local/bin/coldsync_hosp_from_usb.sh`
- **백업 문서**: `docs/ops/BACKUP_SYSTEM.md`

### pgbouncer 관련
- **설정 파일**: `/etc/pgbouncer/pgbouncer.ini` (컨테이너 내부)
- **userlist.txt**: `/etc/pgbouncer/userlist.txt` (auth_user용)
- **인증 방식**: `auth_query` (중앙 관리)

### Shadow Training
- **메인 스크립트**: `scripts/shadow_duri_integration_final.sh`
- **24h 파일럿**: `scripts/pilot_24h.sh`
- **비동기 emotion**: `duri_core/app/api.py` (202 Accepted)

---

## 🔄 다음 작업 (재개 시)

### 1. pgbouncer 인증 완전 정리
- [ ] 애플리케이션 DSN을 `duri_core` 사용자로 변경 (`docker-compose.yml`)
- [ ] pgbouncer 로그의 "no such user: postgres" 경고 확인 및 해결

### 2. EV_1h 모니터링
- [ ] 10분 주기 확인 (목표: EV_1h ≥ 4)
- [ ] `pilot_24h.sh` 실행 상태 확인

### 3. 백업 체인 확인
- [ ] USB 미러 완료 여부 확인
- [ ] HOSP 트리거 실행 여부 확인

---

## 💾 저장 시점 정보

- **저장 시간**: 2025-10-31 (현재)
- **작업 디렉토리**: `/home/duri/DuRiWorkspace`
- **Git 브랜치**: `main` (확인 필요)
- **Docker 상태**: 모든 컨테이너 healthy

---

## 🚀 재개 명령어

```bash
# 1. WSL 재시작 후 환경 복원
bash ~/.config/duri/restore/wsl_restore.sh

# 2. Docker 컨테이너 상태 확인
docker ps | grep duri

# 3. pgbouncer 인증 확인
docker exec duri-pgbouncer cat /etc/pgbouncer/pgbouncer.ini | grep -E "^auth_type|^auth_user|^auth_query"

# 4. 백업 상태 확인
ls -lth /mnt/hdd/ARCHIVE/INCR/*.tar.zst | head -3

# 5. EV 생성 확인
find var/evolution -maxdepth 1 -type d -name "EV-*" -newermt "-1 hour" | wc -l
```

---

## ⚠️ 주의사항

1. **G: 드라이브 마운트**: WSL 재시작 시 자동 마운트 확인 필요
2. **pgbouncer 설정**: 컨테이너 재시작 시 설정 유지 확인
3. **애플리케이션 DSN**: 현재 `postgres` 사용자 사용 중 → `duri_core`로 변경 권장

---

## 📊 현재 메트릭

- **EV_1h**: 2 (증가 중)
- **202 경로**: 정상 작동
- **DB 연결**: pgbouncer_auth 정상
- **백업 체인**: 자동 실행 중

