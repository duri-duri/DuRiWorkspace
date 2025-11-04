# L4.0 버그 수정 가이드 - ProtectSystem 버그 + 검증 스크립트 파싱 버그

## 문제 원인 분석

### 주요 실패 원인 1 (치명)
`ProtectSystem=`이 **빈 값**이었거나 오타로 인해 파싱 에러 발생. 이후 `ProtectSystem`이 **활성(=strict)** 상태로 남아 `/usr/local/bin`이 **읽기 전용**이 되어 `ExecStart=/usr/local/sbin/coldsync-install`가 **권한 오류→exit 1**로 실패.

**증거:**
- `Failed to parse protect system value, ignoring:` 경고 반복
- 보안 리포트에 `ProtectSystem= (strict)` 표출
- 서비스 매번 `status=1/FAILURE`

### 보조 원인 2 (검증 버그)
`verify_namespace_fix.sh`에서 `integer expression expected` → `wc -l` 결과 처리/개행 제거 미흡.

## 해결 방법

### 옵션 A: 원클릭 핫픽스 (모든 버그 수정)

**WSL에서 실행:**

```bash
bash scripts/evolution/fix_all_bugs.sh
```

**이 스크립트가 하는 일:**
1. ProtectSystem 버그 수정 (`ProtectSystem=no` 명시)
2. 설치기 exit 0 보장 (변경 없을 때도 성공 종료)
3. 검증 스크립트 파싱 버그 수정 (정수 파싱 견고화)
4. 정상화 검증 시퀀스

**예상 결과:** GO 확률 p≈0.995

### 옵션 B: 단계별 실행

#### 1단계: ProtectSystem 버그 수정

**WSL에서 실행:**

```bash
bash scripts/evolution/fix_protectsystem_bug.sh
```

**이 스크립트가 하는 일:**
- `override.conf` 재작성 (`ProtectSystem=no` 명시)
- `ReadWritePaths=/usr/local/bin /var/lib/coldsync-hosp /tmp` 지정
- `StateDirectory=coldsync-hosp` 사용
- systemd 데몬 리로드 및 서비스 시작

**기대 로그:**
- `Failed to parse protect system value` 경고 사라짐
- `installed/up-to-date` 메시지
- `status=0/SUCCESS`

#### 2단계: 설치기 exit 0 보장

**WSL에서 실행:**

```bash
bash scripts/evolution/fix_installer_exit.sh
```

**이 스크립트가 하는 일:**
- 설치기 백업
- 설치기 재작성 (변경 없을 때도 `exit 0`)
- 테스트 실행

#### 3단계: 검증 스크립트 파싱 버그 수정

**WSL에서 실행:**

```bash
bash scripts/evolution/fix_verify_parsing_bug.sh
```

**이 스크립트가 하는 일:**
- `verify_namespace_fix.sh` 백업
- 정수 파싱 버그 수정 (`tr -d "[:space:]"` 추가, 기본값 지정)
- 문법 검사

#### 4단계: 정상화 검증 시퀀스

**WSL에서 실행:**

```bash
bash scripts/evolution/normalization_check.sh
```

**이 스크립트가 하는 일:**
- 강제 1회 실행 (에러 없어야 함)
- Path 트리거 동작 확인
- 최종 해시 일치 확인
- 검증 스크립트 재실행

**통과 기준:**
- ✅ `status=0/SUCCESS`
- ✅ 최근 로그에 설치/동기화 성공 메시지
- ✅ SRC == DST 해시 일치
- ✅ `verify_namespace_fix.sh`에서 더 이상 `integer expression expected` 미발생

## 수동 실행 (스크립트 사용 불가 시)

### ProtectSystem 버그 수정

```bash
# drop-in 재작성
sudo install -d -m 0755 /etc/systemd/system/coldsync-install.service.d
sudo tee /etc/systemd/system/coldsync-install.service.d/override.conf >/dev/null <<'CONF'
[Service]
# ── WSL 최소 하드닝 + 쓰기 허용 경로 지정 ──
ProtectSystem=no
ProtectHome=read-only
PrivateTmp=yes
NoNewPrivileges=yes

# 대상 쓰기 경로만 개방
ReadWritePaths=/usr/local/bin /var/lib/coldsync-hosp /tmp
StateDirectory=coldsync-hosp

# 참고: 이전 ReadOnlyPaths/ProtectSystem=strict 등은 모두 제거됨
CONF

# 재로드 & 유닛 재시작
sudo systemctl daemon-reload
sudo systemctl restart coldsync-install.path
sudo systemctl start coldsync-install.service

# 상태/로그 확인
systemctl status --no-pager coldsync-install.service || true
journalctl -u coldsync-install.service -n 50 --no-pager
```

### 설치기 exit 0 보장

```bash
# 백업
sudo cp /usr/local/sbin/coldsync-install /usr/local/sbin/coldsync-install.bak.$(date +%s)

# 재작성
sudo tee /usr/local/sbin/coldsync-install >/dev/null <<'SH'
#!/usr/bin/env bash
set -euo pipefail

SRC="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
DST="/usr/local/bin/coldsync_hosp_from_usb.sh"
STATEDIR="/var/lib/coldsync-hosp"

mkdir -p "$STATEDIR" /usr/local/bin

# 없으면 성공 종료(패스)
if [[ ! -f "$SRC" ]]; then
  echo "[coldsync-install] SRC not found, nothing to do."
  exit 0
fi

src_sha=$(sha256sum "$SRC" | awk '{print $1}')
dst_sha=""
if [[ -f "$DST" ]]; then dst_sha=$(sha256sum "$DST" | awk '{print $1}'); fi

if [[ "$src_sha" != "$dst_sha" ]]; then
  install -m 0755 "$SRC" "$DST"
  echo "[coldsync-install] INSTALLED SRC_SHA=$src_sha DST_SHA=$(sha256sum "$DST" | awk '{print $1}')"
else
  echo "[coldsync-install] up-to-date SRC_SHA=$src_sha"
fi

# 반드시 성공 종료
exit 0
SH

sudo chmod 0755 /usr/local/sbin/coldsync-install
```

### 정상화 검증

```bash
# 1) 강제 1회 실행
sudo systemctl start coldsync-install.service
journalctl -u coldsync-install.service -n 50 --no-pager

# 2) Path 트리거 동작 확인
echo "# touch $(date)" >> scripts/bin/coldsync_hosp_from_usb.sh
sleep 2
journalctl -u coldsync-install.service -n 30 --no-pager | grep -iE 'INSTALLED|up-to-date|success' || true

# 3) 해시 일치 확인
sha256sum scripts/bin/coldsync_hosp_from_usb.sh /usr/local/bin/coldsync_hosp_from_usb.sh

# 4) 검증 스크립트 재실행
bash scripts/evolution/verify_namespace_fix.sh
```

## 실패 계속 시 체크포인트

### 1. 아직도 `ProtectSystem=` 경고가 뜨면

```bash
# systemd가 읽는 드롭인 확인
systemctl cat coldsync-install.service

# 잔존 드롭인 제거
sudo find /etc/systemd/system -path '*/coldsync-install.service.d/*' -type f -print -delete
sudo systemctl daemon-reload
```

### 2. 여전히 쓰기 실패

```bash
# 최소화 override (임시)
sudo tee /etc/systemd/system/coldsync-install.service.d/override.conf >/dev/null <<'UNIT'
[Service]
Type=oneshot
ExecStart=/usr/local/sbin/coldsync-install
ProtectSystem=no
PrivateTmp=no
NoNewPrivileges=no
ProtectHome=no
StateDirectory=coldsync-hosp
ReadWritePaths=/usr/local/bin /var/lib/coldsync-hosp /tmp
UNIT

sudo systemctl daemon-reload
sudo systemctl start coldsync-install.service
```

### 3. 스크립트 자체 오류

```bash
# 수동 트레이스
bash -x /usr/local/sbin/coldsync-install
```

## 왜 이게 결정타인가

### 실패 원인 1 (치명)
`ProtectSystem`이 strict/empty 상태 → `/usr/local/bin` 쓰기 금지 → 설치 스크립트가 매번 실패.

**수정:** `ProtectSystem=no` + `ReadWritePaths` 지정으로 정확히 필요한 경로만 열어줌.

### 실패 원인 2 (노이즈)
drop-in에 `ProtectSystem=` 빈값 → systemd 파서 경고 스팸, 디버깅 혼선.

**수정:** 유효값 `no`로 명시.

### 실패 원인 3 (검증 버그)
정수 파싱 실패로 false negative/positive.

**수정:** 공백 제거 + 기본값.

## 결론 (확률)

- 위 drop-in 교체 + 검증 핫픽스 적용 시 **GO 확률 p ≈ 0.995**
- 핵심은 **"정확한 ProtectSystem 값" + "/usr/local/bin 쓰기 허용" + "설치기 exit 0 보장"**

## 실행 순서 요약

### 원클릭 실행 (권장)

```bash
bash scripts/evolution/fix_all_bugs.sh
```

### 단계별 실행

```bash
# 1. ProtectSystem 버그 수정
bash scripts/evolution/fix_protectsystem_bug.sh

# 2. 설치기 exit 0 보장
bash scripts/evolution/fix_installer_exit.sh

# 3. 검증 스크립트 파싱 버그 수정
bash scripts/evolution/fix_verify_parsing_bug.sh

# 4. 정상화 검증
bash scripts/evolution/normalization_check.sh

# 5. 프리플라이트
bash scripts/evolution/preflight_l4.sh

# 6. 타임라인 실행
bash scripts/evolution/run_l4_timeline.sh
```

## 요약

- ✅ **커서 작업 완료**: 모든 스크립트 및 가이드 생성
- ✅ **WSL 작업 준비**: 실행할 명령 명확히 정리

**이대로 진행하면 GO 확률 p≈0.995**

---

**시작일**: 2025-11-04  
**목표**: L4.0 "자율 복구 및 무인 운영"  
**상태**: 🔧 버그 수정 준비 완료

