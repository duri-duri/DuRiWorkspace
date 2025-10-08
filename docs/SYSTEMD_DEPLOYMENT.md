# 🚀 Systemd 배포 가이드

## 개요
DuRi Shadow Mode를 systemd 서비스로 운영하는 방법입니다.

## 설치

### 1. systemd 유닛 설치
```bash
# systemd 유닛 파일 복사
sudo cp systemd/*.service /etc/systemd/system/

# logrotate 설정 복사
sudo cp systemd/*.logrotate /etc/logrotate.d/

# systemd 데몬 리로드
sudo systemctl daemon-reload
```

### 2. 서비스 활성화
```bash
# 모든 Shadow Mode 서비스 시작
make start-shadow

# 또는 개별 시작
sudo systemctl enable --now duri-rag-eval
sudo systemctl enable --now duri-pr-gate
sudo systemctl enable --now duri-rag-eval-tuned
```

## 운영

### 서비스 상태 확인
```bash
# 전체 상태 확인
make status-shadow

# 개별 상태 확인
sudo systemctl status duri-rag-eval
sudo systemctl status duri-pr-gate
sudo systemctl status duri-rag-eval-tuned
```

### 서비스 중지
```bash
# 모든 서비스 중지
make stop-shadow

# 개별 중지
sudo systemctl disable --now duri-rag-eval
```

### 로그 확인
```bash
# 실시간 로그 확인
sudo journalctl -u duri-rag-eval -f
sudo journalctl -u duri-pr-gate -f
sudo journalctl -u duri-rag-eval-tuned -f

# 최근 로그 확인
sudo journalctl -u duri-rag-eval --since "1 hour ago"
```

## 설정

### 환경변수 조정
서비스 파일에서 `SLEEP_SECS` 값을 조정할 수 있습니다:

```bash
# 서비스 파일 편집
sudo systemctl edit duri-rag-eval

# 또는 직접 편집
sudo nano /etc/systemd/system/duri-rag-eval.service
```

### 자동 재시작
서비스는 자동으로 재시작됩니다:
- `Restart=always`: 항상 재시작
- `RestartSec=5`: 5초 후 재시작

## 트러블슈팅

### 서비스 시작 실패
```bash
# 상세 로그 확인
sudo journalctl -u duri-rag-eval -n 50

# 수동 실행으로 문제 확인
cd /home/duri/DuRiWorkspace
SLEEP_SECS=7200 scripts/loop_rag_eval.sh
```

### 권한 문제
```bash
# 사용자 확인
whoami

# 작업 디렉토리 권한 확인
ls -la /home/duri/DuRiWorkspace
```

## 로그 관리

### logrotate 설정
- 위치: `/etc/logrotate.d/duri-workspace`
- 크기: 10MB 초과 시 로테이션
- 보관: 7개 파일
- 압축: 활성화

### 수동 로그 정리
```bash
# 오래된 로그 파일 정리
find /home/duri/DuRiWorkspace/var/logs -name "*.log.*" -mtime +7 -delete
```

## 환경 변수 외부화

### 설정 파일 생성
```bash
# 환경 변수 설정 파일 생성
sudo tee /etc/default/duri-workspace >/dev/null << 'ENV_EOF'
SLEEP_SECS=7200
# 기타 환경 변수 추가 가능
ENV_EOF
```

### 환경 변수 조정
운영팀이 `SLEEP_SECS`만 바꾸고 싶을 때:
```bash
# 설정 파일 편집
sudo nano /etc/default/duri-workspace

# 서비스 재시작
sudo systemctl restart duri-rag-eval
```

### 지원되는 환경 변수
- `SLEEP_SECS`: 루프 주기 (기본값: 7200초)
- 기타 환경 변수는 필요에 따라 추가 가능

## 리로드 플로우 (핫리로드)

### 환경 변수 변경 시
```bash
# 환경 변수 변경
echo 'SLEEP_SECS=60' | sudo tee /etc/default/duri-workspace

# 서비스 재시작 없이 즉시 반영
sudo systemctl reload duri-rag-eval

# 변경 확인
sudo journalctl -u duri-rag-eval -n 20 --no-pager
```

### 리로드 장점
- **서비스 중단 없음**: 루프가 계속 실행되면서 설정 변경
- **즉시 반영**: 다음 루프 턴에서 새로운 설정 적용
- **운영 편의성**: 재시작 없이 설정 조정 가능

### 지원되는 환경 변수
- `SLEEP_SECS`: 루프 주기 (기본값: 7200초)
- 기타 환경 변수는 필요에 따라 추가 가능

## sudo 비대화식 대비

### 로컬 환경에서 sudo 인증 필요 시
```bash
# 비대화식 sudo 실패 시
make install-systemd SUDO="sudo"
```

### CI/비대화식 환경
```bash
# NOPASSWD 설정 후
make install-systemd SUDO="sudo -n"
```

### 루트 환경
```bash
# 루트 셸에서
make install-systemd SUDO=""
```
