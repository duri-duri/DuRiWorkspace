# L4.0 coldsync 자동 배포 설정 가이드

## 개요

**현재 상태: A안(유저 유닛 + ~/.local/bin) 정상 동작 중 (p≈0.995)**

VS Code 저장 시 자동 배포가 정상 작동하며, 해시 동기화도 확인되었습니다.

## 선택지

### A안: 유저 유닛 + ~/.local/bin (권장, p≈0.995)
- **장점**: 루트 권한 불필요, VS Code 저장 즉시 반영
- **단점**: `/usr/local/bin`이 아닌 `~/.local/bin` 사용
- **대상**: WSL 환경, 일반 사용자 권한으로 운영

### B안: 시스템 유닛 유지 + sudo 제거 (p≈0.98)
- **장점**: `/usr/local/bin` 유지 (시스템 전역)
- **단점**: 루트 권한 필요, systemd 서비스 설정 필요
- **대상**: 시스템 전역 스크립트 필요 시

### 최소 수정: sudo NOPASSWD + Path 개선 (p≈0.85)
- **장점**: 기존 구조 최소 변경
- **단점**: 여전히 불안정 가능
- **대상**: 빠른 수정 원할 때

## VS Code/WSL에서 실행할 명령어

### A안 채택 시 (권장)

```bash
cd ~/DuRiWorkspace

# 1. A안 설정 스크립트 실행
bash scripts/evolution/setup_coldsync_user_unit.sh

# 2. .bashrc 문법 오류 수정
bash scripts/evolution/fix_bashrc_syntax.sh
source ~/.bashrc

# 3. 검증
# VS Code에서 파일 수정 후 저장 (Ctrl+S)
sleep 3
journalctl --user -u coldsync-install.service -n 5 --no-pager | grep -E 'INSTALLED|up-to-date'
sha256sum ~/.local/bin/coldsync_hosp_from_usb.sh ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
```

### B안 채택 시

```bash
cd ~/DuRiWorkspace

# 1. B안 설정 스크립트 실행
bash scripts/evolution/setup_coldsync_system_unit_fixed.sh

# 2. .bashrc 문법 오류 수정
bash scripts/evolution/fix_bashrc_syntax.sh
source ~/.bashrc

# 3. 검증
# VS Code에서 파일 수정 후 저장 (Ctrl+S)
sleep 3
journalctl -u coldsync-install.service -n 5 --no-pager | grep -E 'INSTALLED|up-to-date'
sha256sum /usr/local/bin/coldsync_hosp_from_usb.sh ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
```

### 최소 수정 채택 시

```bash
cd ~/DuRiWorkspace

# 1. 최소 수정 스크립트 실행
bash scripts/evolution/setup_coldsync_minimal_fix.sh

# 2. .bashrc 문법 오류 수정
bash scripts/evolution/fix_bashrc_syntax.sh
source ~/.bashrc

# 3. 검증
# VS Code에서 파일 수정 후 저장 (Ctrl+S)
sleep 3
journalctl -u coldsync-install.service -n 5 --no-pager | grep -E 'INSTALLED|up-to-date'
sha256sum /usr/local/bin/coldsync_hosp_from_usb.sh ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
```

## 테스트 시나리오

### 1. 기본 저장 테스트
- VS Code에서 파일 끝에 주석 추가: `# Test $(date)`
- 저장 (Ctrl+S)
- 3초 대기 후 로그 확인

### 2. Rename 시나리오 테스트
```bash
tmp=$(mktemp)
cp ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh "$tmp"
mv "$tmp" ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
sleep 3
journalctl --user -u coldsync-install.service -n 5 --no-pager | grep -E 'INSTALLED|up-to-date'
```

### 3. 디렉터리 변경 테스트
```bash
touch ~/DuRiWorkspace/scripts/bin/.touch_$$
sleep 3
journalctl --user -u coldsync-install.service -n 5 --no-pager | grep -E 'INSTALLED|up-to-date'
```

## 실패 시 롤백

```bash
# A안 롤백
systemctl --user disable --now coldsync-install.path
rm -f ~/.config/systemd/user/coldsync-install.{service,path}

# B안 롤백
sudo systemctl disable --now coldsync-install.path
sudo rm -f /etc/systemd/system/coldsync-install.path.bak.*
sudo systemctl daemon-reload

# 최소 수정 롤백
sudo rm -f /etc/sudoers.d/coldsync
sudo systemctl daemon-reload
```

## 운영 Runbook (최종)

### 일상 수정
1. VS Code에서 소스 저장 → 3초 후 자동 배포 → 확인
   ```bash
   journalctl --user -u coldsync-install.service -n 5 --no-pager | grep -E 'INSTALLED|up-to-date'
   sha256sum ~/.local/bin/coldsync_hosp_from_usb.sh ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
   ```

### 수동 동기화 (비상)
```bash
systemctl --user start coldsync-install.service
```

### 헬스체크 (3점 점검)
```bash
systemctl --user status coldsync-install.path --no-pager | head -12
journalctl --user -u coldsync-install.service -n 20 --no-pager | tail -10
sha256sum ~/.local/bin/coldsync_hosp_from_usb.sh ~/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh
```

### 회귀 테스트
```bash
bash scripts/evolution/coldsync_regression.sh
```

### 헬스체크
```bash
bash scripts/evolution/coldsync_healthcheck.sh
```

## 실패 모드별 빠른 복구

### 로그에 반응 없음
```bash
systemctl --user restart coldsync-install.path
```

### 해시 불일치 (드물게 rename race)
```bash
systemctl --user start coldsync-install.service
```

### 이중 트리거 (로그가 2회씩)
```bash
sudo systemctl mask coldsync-install.path coldsync-install.service
```

## 장기 안정성 확보

### 유저 유닛 영구화 (재부팅 후에도 지속)
```bash
loginctl enable-linger "$USER"
```

### 과거 system unit 충돌 방지
```bash
sudo systemctl stop coldsync-install.path coldsync-install.service 2>/dev/null || true
sudo systemctl disable coldsync-install.path coldsync-install.service 2>/dev/null || true
sudo systemctl mask coldsync-install.path coldsync-install.service 2>/dev/null || true
```

## 권장 사항

1. **A안 채택 권장**: WSL 환경에서 가장 안정적 (p≈0.995)
2. **.bashrc 문법 오류 수정**: 모든 안에서 공통 적용
3. **수동 동기화 백업 유지**: `sync-coldsync` alias는 fallback으로 유지
4. **정기 헬스체크**: `coldsync_healthcheck.sh` 주기적 실행
5. **회귀 테스트**: 변경 사항 적용 후 `coldsync_regression.sh` 실행

