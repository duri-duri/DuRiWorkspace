# DuRi 백업 체계 전체 정리

## 📋 개요

DuRi 백업 체계는 **3단계 연쇄 백업 시스템**으로 구성되어 있습니다:

```
HDD 증분 백업 → USB 미러 (G: Ventoy) → HOSP/HOME 콜드 백업
```

---

## 🏗️ 백업 체인 구조

### 1단계: HDD 증분 백업 (Primary Backup)
- **위치**: `/mnt/hdd/ARCHIVE/INCR/` 또는 `/mnt/hdd/ARCHIVE/FULL/`
- **형식**: `INCR__YYYY-MM-DD__HHMM__hostname.tar.zst` (증분) / `FULL__YYYY-MM-DD__HHMM__hostname.tar.zst` (전체)
- **스크립트**: `scripts/duri_backup.sh`
- **스냅샷**: `/var/lib/duri-backup/snapshots/duri_ws.snar` (증분 추적용)
- **로그**: `/var/log/duri2-backup/backup_YYYYMMDD_HHMMSS.log`

#### 실행 방법
```bash
# 증분 백업 (기본)
bash scripts/duri_backup.sh incr

# 전체 백업
bash scripts/duri_backup.sh full
```

#### 자동 실행
- **systemd 타이머**: 매일 02:30 자동 실행 (`/etc/systemd/system/duri-backup.timer`)
- **서비스**: `/etc/systemd/system/duri-backup.service`

#### 제외 규칙
- 위치: `/var/log/duri2-backup/tar.exclude`
- 내용:
  - `.duri_guard` (안전 센티넬)
  - 런타임/볼라틸: `data/prometheus/**`, `data/**/wal/**`, `data/**/queries.active`
  - VCS/캐시/대용량: `**/.git/`, `**/.github/`, `**/.venv/`, `**/__pycache__/`, `**/node_modules/`, `**/logs/`
  - 백업 아티팩트: `ARCHIVE/`, `backup_repository/`, `duri_snapshots/`, `*.tar.zst`, `*.sha256`

---

### 2단계: USB 미러 (Intermediate Mirror)
- **위치**: `/mnt/g/두리백업/latest/` (G: Ventoy 드라이브, **불변 경로**)
- **형식**: rsync로 전체 워크스페이스 동기화
- **스크립트**: `scripts/duri_backup.sh` (내부에서 자동 실행)
- **handoff 마커**:
  - `.handoff_READY`: USB 미러 완료 신호
  - `.handoff.seq`: 시퀀스 번호 (자동 증가)

#### 실행 조건
- HDD 증분 백업 완료 후 자동 실행
- G: 드라이브가 마운트되어 있어야 함 (자동 마운트 시도)
- rsync 완료 후 (exit 0 또는 23) handoff 마커 생성

#### G: 드라이브 마운트
- **자동 마운트 스크립트**: `scripts/_mount_g.sh`, `scripts/_umount_g.sh`
- **sudoers 설정**: 비밀번호 없이 마운트 가능 (`setup_g_mount_nopasswd.sh`)
- **검증**: `/mnt/g`가 `/dev/sdb` (루트)를 가리키지 않아야 함

#### rsync 옵션
- `--no-times`, `--no-perms`, `--no-owner`, `--no-group` (drvfs 호환성)
- `--delete`, `--delete-delay` (소스 기준 동기화)
- `--max-size=100M` (대용량 파일 제외)
- 제외 규칙: HDD 백업과 동일 (`tar.exclude`)

---

### 3단계: HOSP/HOME 콜드 백업 (Cold Backup)
- **HOSP 위치**: `/mnt/e/DuRiSafe_HOSP/latest/`
- **HOME 위치**: `/mnt/f/DuRiSafe_HOME/latest/`
- **트리거 스크립트**: `/usr/local/bin/coldsync_hosp_from_usb.sh` (HOSP), `scripts/duri_cold_from_usb.sh` (HOSP/HOME 선택 가능)

#### 실행 조건
- USB 미러 완료 (`/mnt/g/두리백업/latest/.handoff_READY` 존재)
- `duri_backup.sh`에서 자동 트리거 (rsync 성공 시)

#### 실행 흐름
1. USB 미러 완료 확인
2. handoff 마커 생성 (`.handoff_READY`, `.handoff.seq`)
3. **자동 트리거**: `coldsync_hosp_from_usb.sh` 실행 (HOSP)
4. 수동 실행: `scripts/duri_cold_from_usb.sh hosp|home`

#### HOSP 콜드 백업 스크립트
```bash
#!/usr/bin/env bash
# /usr/local/bin/coldsync_hosp_from_usb.sh
USB=/mnt/g/두리백업/latest
DST=/mnt/e/DuRiSafe_HOSP/latest
# rsync로 USB → HOSP 동기화
```

---

## 📁 백업 디렉토리 구조

```
/mnt/hdd/ARCHIVE/
├── FULL/              # 전체 백업 (수동 실행 시)
│   └── FULL__YYYY-MM-DD__HHMM__hostname.tar.zst
└── INCR/              # 증분 백업 (기본)
    └── INCR__YYYY-MM-DD__HHMM__hostname.tar.zst

/mnt/g/두리백업/         # G: Ventoy 드라이브 (USB 미러)
└── latest/            # 최신 워크스페이스 동기화본
    ├── .handoff_READY # USB 미러 완료 신호
    └── .handoff.seq   # 시퀀스 번호

/mnt/e/DuRiSafe_HOSP/   # HOSP 콜드 백업 (병원 서버)
└── latest/            # USB에서 동기화된 최신본

/mnt/f/DuRiSafe_HOME/   # HOME 콜드 백업 (집 서버)
└── latest/            # USB에서 동기화된 최신본

/var/lib/duri-backup/
└── snapshots/
    └── duri_ws.snar   # 증분 백업 스냅샷 (tar --listed-incremental)

/var/log/duri2-backup/
├── backup_YYYYMMDD_HHMMSS.log  # 백업 실행 로그
└── tar.exclude                 # 제외 규칙 파일
```

---

## 🔄 백업 체인 실행 흐름

### 자동 실행 (systemd 타이머)
1. 매일 02:30 → `duri-backup.timer` 트리거
2. `duri-backup.service` 실행 → `bash scripts/duri_backup.sh incr`
3. HDD 증분 백업 (`tar --zstd --listed-incremental`)
4. USB 미러 (rsync, G: 드라이브 자동 마운트)
5. handoff 마커 생성 (`.handoff_READY`, `.handoff.seq`)
6. **자동 트리거**: `coldsync_hosp_from_usb.sh` (HOSP)

### 수동 실행
```bash
# 1단계: HDD 증분 백업
bash scripts/duri_backup.sh incr

# 2단계: USB 미러 (자동 포함, 별도 실행 시)
bash scripts/run_usb_mirror_to_cold.sh

# 3단계: HOSP/HOME 콜드 백업 (수동)
bash scripts/duri_cold_from_usb.sh hosp  # HOSP
bash scripts/duri_cold_from_usb.sh home  # HOME
```

---

## 🛠️ 주요 스크립트

### 메인 백업 스크립트
- **`scripts/duri_backup.sh`**: HDD 증분/전체 백업 + USB 미러 + HOSP 트리거

### USB 관련
- **`scripts/run_usb_mirror_to_cold.sh`**: USB 미러링부터 콜드백업까지 연쇄 실행
- **`scripts/_mount_g.sh`**: G: 드라이브 마운트 (sudoers NOPASSWD)
- **`scripts/_umount_g.sh`**: G: 드라이브 언마운트
- **`scripts/setup_g_mount_nopasswd.sh`**: sudoers 설정 (비밀번호 없이 마운트)

### 콜드 백업
- **`/usr/local/bin/coldsync_hosp_from_usb.sh`**: HOSP 콜드 백업 (USB → HOSP)
- **`scripts/duri_cold_from_usb.sh`**: HOSP/HOME 콜드 백업 (매니페스트 기반 증가분)
- **`scripts/duri_cold_backup_home.sh`**: HOME 콜드 백업 (HOSP → HOME 동기화)

### 캐스케이드 워커
- **`scripts/backup_cascade_worker.sh`**: 백업 연쇄 반응 실행
- **`scripts/backup_cascade_scan_and_enqueue.sh`**: HDD 백업 변경 스캔 및 큐잉

---

## 🔍 백업 상태 확인

### 현재 백업 프로세스 확인
```bash
# 백업 프로세스 확인
ps aux | grep "duri_backup\|rsync.*두리백업" | grep -v grep

# 최신 HDD 백업 파일
ls -lth /mnt/hdd/ARCHIVE/INCR/*.tar.zst | head -3

# USB 미러 상태
ls -lh /mnt/g/두리백업/latest/.handoff* 2>/dev/null

# HOSP 트리거 실행 여부
ps aux | grep "coldsync_hosp" | grep -v grep
```

### 백업 진행 상태 스크립트
```bash
bash scripts/duri_backup_progress.sh
```

---

## ⚙️ cron 작업 (추가 백업 작업)

### `/etc/cron.d/duri-archive`
- **매일 09:15**: 레거시 백업 수집 + GOLD 갱신 (`import_legacy_backups.sh`)
- **매일 11:15**: 백업 신선도 감시 (`ops_backup_staleness_guard.sh`)
- **매일 14:20**: 오프사이트 디스크 동기화 (AGE 암호화)
- **월~토 14:50**: 클라우드 오프사이트 (rclone crypt 업로드)
- **매주 일요일 15:10**: 백업 정리 (5G FULL 격리 + 자동삭제)
- **매월 1일 09:40**: 건강검진 (`test_hdd_backup_checklist.sh`)
- **분기별 11:50**: 복구 드릴 (`ops_quarterly_restore_drill.sh`)

---

## 🔐 보안 및 권한

### sudoers 설정
- G: 드라이브 마운트/언마운트 비밀번호 없이 실행 가능
- 설정 파일: `/etc/sudoers.d/duri_g_mount` (자동 생성)

### 파일 권한
- HDD 백업: 일반 사용자 권한 (duri)
- USB 미러: drvfs 마운트 (Windows 권한 적용)
- 콜드 백업: 소유자 권한 유지

---

## 🚨 문제 해결

### G: 드라이브 인식 안 됨
```bash
# 자동 마운트 시도
sudo ~/DuRiWorkspace/scripts/_mount_g.sh

# 마운트 상태 확인
df -h /mnt/g
mountpoint -q /mnt/g && echo "OK" || echo "FAIL"

# WSL 재시작 필요 시
wsl --shutdown
```

### USB 미러 진행 안 됨
- rsync 프로세스 확인: `ps aux | grep rsync`
- G: 드라이브 마운트 확인: `mountpoint -q /mnt/g`
- handoff 마커 확인: `ls -lh /mnt/g/두리백업/latest/.handoff*`

### HOSP 트리거 실행 안 됨
- handoff 마커 확인: `test -f /mnt/g/두리백업/latest/.handoff_READY`
- 스크립트 존재 확인: `ls -lh /usr/local/bin/coldsync_hosp_from_usb.sh`
- 수동 실행: `bash /usr/local/bin/coldsync_hosp_from_usb.sh`

---

## 📊 백업 체계 다이어그램

```
┌─────────────────────────────────────────────────────────────┐
│                    DuRi 백업 체계                             │
└─────────────────────────────────────────────────────────────┘

1️⃣ HDD 증분 백업 (Primary)
   ↓
   [tar --zstd --listed-incremental]
   ↓
   /mnt/hdd/ARCHIVE/INCR/INCR__*.tar.zst
   ↓
   스냅샷: /var/lib/duri-backup/snapshots/duri_ws.snar
   
2️⃣ USB 미러 (Intermediate)
   ↓
   [rsync] (G: Ventoy 드라이브 자동 마운트)
   ↓
   /mnt/g/두리백업/latest/
   ↓
   handoff 마커: .handoff_READY, .handoff.seq
   
3️⃣ 콜드 백업 (Cold)
   ├─ HOSP: /mnt/e/DuRiSafe_HOSP/latest/
   │   └─ [자동 트리거] coldsync_hosp_from_usb.sh
   │
   └─ HOME: /mnt/f/DuRiSafe_HOME/latest/
       └─ [수동] duri_cold_from_usb.sh home

───────────────────────────────────────────────────────────────

자동 실행: systemd 타이머 (매일 02:30)
수동 실행: bash scripts/duri_backup.sh incr

