# 🚀 백업 리팩토링 실행 명령어 가이드

> **복사&붙여넣기용 명령어 모음**

## ✅ **1단계: 환경 설정**

```bash
# 1) ops/summary 디렉토리 생성
mkdir -p ops/summary

# 2) config.env 파일 생성
cat > ops/summary/config.env << 'EOF'
# 로그/상태 경로
BACKUP_LOG_DIR="backup_logs"
GATE_LOG_DIR="gate_logs"
SYS_LOG_DIR="var/logs"
STATE_DIR="var/state"

# 산출물
SUMMARY_JSON="ops/summary/summary.json"
SUMMARY_MD="ops/summary/summary.md"

# README 대상 파일
README_PATH="README.md"

# Git 설정
GIT_BRANCH="main"
GIT_USER_NAME="auto-bot"
GIT_USER_EMAIL="auto-bot@example.local"

# 동작 옵션
DRY_RUN="1"          # 1=실제 파일 미수정 (테스트용)
LOCK_PATH="ops/summary/README_patch.lock"

# 실패시 강등 정책
GRACE_DEGRADE_FULL_ON_INCR_FAIL="1"
DEFER_RETENTION_ON_FAIL="1"
EOF
```

## 🧪 **2단계: DRY-RUN 테스트**

```bash
# 1) DRY-RUN 모드로 실행
export DRY_RUN=1
bash ops/summary/summary_report.sh

# 2) 결과 확인
ls -la ops/summary/
cat ops/summary/summary.json
cat ops/summary/summary.md

# 3) README 미수정 확인 (DRY-RUN이므로 변경 없어야 함)
git status
```

## 🚀 **3단계: 실제 실행**

```bash
# 1) DRY-RUN 해제
unset DRY_RUN

# 2) 실제 실행
bash ops/summary/summary_report.sh

# 3) 결과 확인
git status
git log --oneline -5
```

## 🔧 **4단계: Windows 백업 자동화 테스트**

```powershell
# PowerShell에서 실행
cd ops/windows_backup
.\run_backup_setup.bat

# 또는 수동 실행
powershell -NoProfile -ExecutionPolicy Bypass -File ".\setup_backup_drives.ps1"
powershell -NoProfile -ExecutionPolicy Bypass -File ".\test_sync.ps1"
powershell -NoProfile -ExecutionPolicy Bypass -File ".\duri_backup_automation.ps1" -Mode test
```

## 📅 **5단계: 스케줄러 등록**

### **Linux/WSL cron**
```bash
# 19:05 매일 실행
echo "05 19 * * * cd $(pwd) && ops/summary/summary_report.sh >> var/logs/summary.log 2>&1" | crontab -
```

### **Windows 작업 스케줄러**
```cmd
# PowerShell에서 실행
schtasks /Create /TN "DuRi_Summary_Daily" /TR "bash.exe -lc \"cd /mnt/c/Repo && ops/summary/summary_report.sh\"" /SC DAILY /ST 19:05
```

## 🚨 **문제 발생 시 롤백**

```bash
# 1) README 자동 커밋 되돌리기
git revert HEAD --no-edit

# 2) 백업 시스템 롤백
bash rollback_backup_system.sh

# 3) 전체 시스템 복구
git reset --hard SAFE_BACKUP
```

## 📊 **상태 확인**

```bash
# 1) 현재 Phase 상태 확인
cat ops/summary/summary.json

# 2) 로그 확인
tail -f var/logs/summary.log

# 3) Git 상태 확인
git status
git log --oneline -10
```

## ✅ **성공 확인 체크리스트**

- [ ] `ops/summary/summary.json` 생성됨
- [ ] `ops/summary/summary.md` 생성됨  
- [ ] README Phase 표에 ✅ 자동 반영됨
- [ ] Git 커밋 성공 (auto: daily phase update)
- [ ] 로그에 오류 없음
- [ ] Windows 백업 자동화 정상 동작

---

> **💡 팁**: 처음에는 DRY-RUN 모드로 충분히 테스트한 후 실제 실행하세요!



