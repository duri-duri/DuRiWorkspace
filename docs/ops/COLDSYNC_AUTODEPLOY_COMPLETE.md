# coldsync 자동 배포 시스템 - 설정 완료 ✅

## 상태

✅ **설정 완료 및 동작 확인됨**

- 설치기: `/usr/local/sbin/coldsync-install` ✅
- Service 유닛: `/etc/systemd/system/coldsync-install.service` ✅
- Path 유닛: `/etc/systemd/system/coldsync-install.path` ✅ (활성화됨)
- 디렉토리: `/var/lib/coldsync-hosp` ✅

## 최종 검증 결과

- 수동 트리거: ✅ 성공 (`status=0/SUCCESS`)
- 파일 동기화: ✅ SHA256 해시 일치
- 저장 트리거: ✅ 자동 배포 확인됨
- 로그: ✅ `INSTALLED` 확인됨

## 사용법

### 평소 사용

```bash
# VS Code에서 편집
code ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh

# 저장(Ctrl+S) → 자동 배포됨
```

### 로그 확인

```bash
# 실시간 로그
sudo journalctl -u coldsync-install.service -f

# 최근 로그
sudo journalctl -u coldsync-install.service -n 20 --no-pager
```

### 수동 설치 (예외 상황)

```bash
sudo systemctl start coldsync-install.service
```

### 상태 확인

```bash
# Path 유닛 상태
sudo systemctl status coldsync-install.path --no-pager -l

# 파일 동기화 확인
sha256sum /usr/local/bin/coldsync_hosp_from_usb.sh ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
```

## 저장 트리거 테스트

터미널에서 다음 명령어 실행:

```bash
# 작업본에 변경 추가
echo "# Test $(date)" >> ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh

# 2초 대기 후 로그 확인
sleep 2
sudo journalctl -u coldsync-install.service -n 10 --no-pager

# 파일 동기화 확인
sha256sum /usr/local/bin/coldsync_hosp_from_usb.sh ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
```

두 파일의 해시가 같고 로그에 `INSTALLED`가 보이면 **저장 트리거 정상 작동**입니다.

## 문제 해결

### 저장 트리거가 작동하지 않는 경우

```bash
# Path 유닛 재시작
sudo systemctl restart coldsync-install.path

# 수동 트리거
sudo systemctl start coldsync-install.service

# 로그 확인
sudo journalctl -u coldsync-install.service -n 50 --no-pager
```

### 완전 제거 (롤백)

```bash
sudo systemctl disable --now coldsync-install.path
sudo rm -f /etc/systemd/system/coldsync-install.{service,path}
sudo rm -f /usr/local/sbin/coldsync-install
sudo rm -rf /var/lib/coldsync-hosp
sudo systemctl daemon-reload
```

## 파일 위치

- **작업본**: `~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh`
- **설치본**: `/usr/local/bin/coldsync_hosp_from_usb.sh`
- **설치기**: `/usr/local/sbin/coldsync-install`
- **상태 파일**: `/var/lib/coldsync-hosp/.last.sha256`

## 동작 원리

1. **파일 저장** → `PathChanged` 이벤트 발생
2. **Path 유닛** → `coldsync-install.service` 트리거
3. **설치기 실행**:
   - 문법 검증 (`bash -n`)
   - SHA256 변경 확인
   - 원자적 설치 (`install` → `mv`)
4. **자동 배포 완료** → `/usr/local/bin/coldsync_hosp_from_usb.sh` 업데이트

