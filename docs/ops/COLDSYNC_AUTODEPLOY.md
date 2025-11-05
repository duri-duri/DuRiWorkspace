# coldsync 자동 배포 시스템 - 설정 가이드

## 개요

`~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh` 파일을 편집하고 저장하면, 
자동으로 `/usr/local/bin/coldsync_hosp_from_usb.sh`에 배포됩니다.

## 초기 설정 (1회만 실행)

```bash
cd ~/DuRiWorkspace
bash scripts/bin/setup_coldsync_autodeploy.sh
```

이 스크립트는:
1. 루트 설치기 (`/usr/local/sbin/coldsync-install`) 생성
2. systemd Service 유닛 생성
3. systemd Path 유닛 생성 및 활성화
4. 초기 검증 실행

## 일상 사용법

### 편집
```bash
code ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
```

### 저장
VS Code에서 저장(`Ctrl+S`)하면 자동으로:
- 파일 변경 감지
- 문법 검증 (`bash -n`)
- SHA256 변경 확인
- `/usr/local/bin`에 자동 배포

## 운영 명령어

### 로그 확인
```bash
# 실시간 로그
sudo journalctl -u coldsync-install.service -f

# 최근 로그
sudo journalctl -u coldsync-install.service -n 50 --no-pager
```

### 수동 설치 (예외 상황)
```bash
sudo /usr/local/sbin/coldsync-install
```

### 상태 확인
```bash
# Path 유닛 상태
sudo systemctl status coldsync-install.path

# Service 상태
sudo systemctl status coldsync-install.service
```

### 비활성화 (롤백)
```bash
sudo systemctl disable --now coldsync-install.path
sudo systemctl daemon-reload
```

### 완전 제거
```bash
sudo systemctl disable --now coldsync-install.path
sudo rm -f /etc/systemd/system/coldsync-install.{service,path}
sudo rm -f /usr/local/sbin/coldsync-install
sudo rm -rf /var/lib/coldsync-hosp
sudo systemctl daemon-reload
```

## 동작 원리

1. **Path 유닛**: `~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh` 파일 변경 감지
2. **Service 유닛**: 변경 감지 시 루트 설치기 실행
3. **설치기**: 
   - 문법 검증 (`bash -n`)
   - SHA256 비교 (변경 없으면 SKIP)
   - 원자적 설치 (`install` → `mv`)
   - 상태 저장 및 로그 기록

## 안전 장치

- **문법 검증**: 저장 전 `bash -n` 실행
- **중복 방지**: SHA256 기반 변경 감지
- **원자적 설치**: 임시 파일 → 이동 (`mv`)
- **보안 하드닝**: systemd 서비스 보안 옵션 적용
- **화이트리스트**: 쓰기 경로 제한 (`ReadWritePaths`)

## 트러블슈팅

### Path가 감지되지 않는 경우
```bash
# Path 유닛 재시작
sudo systemctl restart coldsync-install.path

# 수동 트리거
sudo systemctl start coldsync-install.service
```

### 설치 실패 시
```bash
# 로그 확인
sudo journalctl -u coldsync-install.service -n 50 --no-pager

# 문법 검증
bash -n ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
```

### systemd 사용 불가 환경 (WSL 구버전 등)
`inotifywait` 기반 대안 스크립트 사용:
```bash
bash scripts/bin/watch_coldsync.sh  # (별도 생성 필요)
```

## 파일 위치

- **작업본**: `~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh`
- **설치본**: `/usr/local/bin/coldsync_hosp_from_usb.sh`
- **설치기**: `/usr/local/sbin/coldsync-install`
- **상태 파일**: `/var/lib/coldsync-hosp/.last.sha256`
- **Service 유닛**: `/etc/systemd/system/coldsync-install.service`
- **Path 유닛**: `/etc/systemd/system/coldsync-install.path`

