# 🚀 DuRi 백업 자동화 시스템

## 📋 개요

DuRi 백업 자동화 시스템은 Windows PowerShell을 기반으로 한 이중 백업 솔루션입니다.

- **H: 드라이브 (WD Elements HDD)**: 대용량, 장기 보관용
- **I: 드라이브 (Samsung T7 SSD)**: 고속, 빠른 복구용

## 🎯 주요 기능

### ✅ 백업 전략
- **전체 백업**: 전체 시스템 복사 (장기 보관용)
- **증분 백업**: 변경된 파일만 백업 (일일 백업용)
- **자동 동기화**: robocopy 기반 안정적인 파일 복사
- **이중 백업**: HDD + SSD 동시 백업으로 안전성 확보

### ✅ 모니터링 및 로깅
- **실시간 로그**: 모든 백업 작업의 상세 로그 기록
- **상태 확인**: 백업 상태 및 통계 정보 제공
- **오류 처리**: 문제 발생 시 즉시 알림 및 복구

## 📁 파일 구조

```
DuRiWorkspace/
├── setup_backup_drives.ps1      # 백업 드라이브 초기 설정
├── test_sync.ps1                # 동기화 테스트
├── duri_backup_automation.ps1   # 메인 백업 자동화 스크립트
├── run_backup_setup.bat         # Windows 배치 파일 (자동 실행)
└── README_BACKUP_AUTOMATION.md  # 이 문서
```

## 🚀 빠른 시작

### **1단계: 자동 설정 (권장)**

```cmd
# Windows 배치 파일 실행
run_backup_setup.bat
```

### **2단계: 수동 설정**

```powershell
# 1. 백업 드라이브 구조 생성
.\setup_backup_drives.ps1

# 2. 동기화 테스트
.\test_sync.ps1

# 3. 백업 시스템 테스트
.\duri_backup_automation.ps1 -Mode test
```

## 📋 사용법

### **기본 백업 명령어**

```powershell
# 전체 백업 (장기 보관용)
.\duri_backup_automation.ps1 -Mode full

# 증분 백업 (일일 백업용)
.\duri_backup_automation.ps1 -Mode incremental

# 백업 시스템 테스트
.\duri_backup_automation.ps1 -Mode test

# 백업 상태 확인
.\duri_backup_automation.ps1 -Mode status
```

### **고급 옵션**

```powershell
# 특정 경로 백업
.\duri_backup_automation.ps1 -Mode full -SourcePath "C:\MyProject"

# 강제 실행
.\duri_backup_automation.ps1 -Mode full -Force
```

## ⚙️ 백업 설정

### **HDD 백업 (WD Elements)**
- **용도**: 장기 보관, 전체 시스템 백업
- **백업 주기**: 주 1회 풀백업
- **특징**: 대용량, 저비용, 안정성

### **SSD 백업 (Samsung T7)**
- **용도**: 빠른 복구, 증분 백업
- **백업 주기**: 매일 증분 백업
- **특징**: 고속, 휴대성, 신뢰성

## 🔧 robocopy 옵션

### **기본 옵션**
- `/E`: 빈 디렉토리 포함 모든 하위 디렉토리 복사
- `/R:3`: 실패 시 최대 3회 재시도
- `/W:2`: 재시도 간 2초 대기
- `/NFL`: 파일 목록 미출력
- `/NDL`: 디렉토리 목록 미출력
- `/NP`: 진행률 미출력

### **증분 백업 옵션**
- `/XO`: 기존 파일 제외 (변경된 파일만)

## 📊 백업 구조

```
H:\DuRiBackup\
├── var\                    # 변수 데이터
├── reports\                # 리포트 파일
├── state\                  # 상태 정보
├── full_20250820_143022\   # 전체 백업 (타임스탬프)
└── incremental_20250820_143022\  # 증분 백업

I:\DuRiBackup\
├── var\                    # 변수 데이터
├── reports\                # 리포트 파일
├── state\                  # 상태 정보
├── full_20250820_143022\   # 전체 백업 (타임스탬프)
└── incremental_20250820_143022\  # 증분 백업
```

## 🚨 문제 해결

### **일반적인 문제**

#### **1. 권한 오류**
```powershell
# PowerShell을 관리자 권한으로 실행
Start-Process PowerShell -Verb RunAs
```

#### **2. 실행 정책 오류**
```powershell
# 실행 정책 변경
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### **3. 드라이브 연결 확인**
```powershell
# 드라이브 상태 확인
Get-PSDrive H, I
```

### **로그 확인**

```powershell
# 최신 로그 파일 확인
Get-ChildItem duri_backup_*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1
```

## 🔄 자동화 및 스케줄링

### **Windows 작업 스케줄러**

1. **작업 스케줄러 열기**: `taskschd.msc`
2. **기본 작업 만들기**: "DuRi 백업 자동화"
3. **트리거 설정**: 매일 18:30
4. **동작 설정**: `duri_backup_automation.ps1 -Mode incremental`

### **PowerShell 스케줄러**

```powershell
# 매일 18:30 증분 백업
Register-ScheduledJob -Name "DuRiIncrementalBackup" -ScriptBlock {
    & "C:\path\to\duri_backup_automation.ps1" -Mode incremental
} -Trigger (New-JobTrigger -Daily -At "18:30")
```

## 📈 성능 최적화

### **백업 속도 향상**
- **SSD 사용**: 고속 드라이브로 백업 속도 향상
- **네트워크 드라이브**: 가능하면 로컬 드라이브 사용
- **백업 시간**: 시스템 사용률이 낮은 시간대 선택

### **저장 공간 최적화**
- **정기 정리**: 오래된 백업 파일 정리
- **압축**: 필요시 백업 파일 압축
- **중복 제거**: 중복 파일 식별 및 제거

## 🎯 다음 단계

### **향후 개발 계획**
1. **웹 대시보드**: 백업 상태 웹 인터페이스
2. **알림 시스템**: 이메일/SMS 백업 완료 알림
3. **클라우드 연동**: OneDrive, Google Drive 연동
4. **백업 검증**: 자동 무결성 검사 및 복구

### **커뮤니티 기여**
- 버그 리포트 및 기능 요청
- 코드 개선 및 최적화 제안
- 문서 및 번역 기여

## 📞 지원 및 문의

### **문제 발생 시**
1. 로그 파일 확인 (`duri_backup_*.log`)
2. README 문서 재검토
3. GitHub Issues 등록

### **기술 지원**
- **문서**: 이 README 파일
- **로그**: PowerShell 실행 로그
- **커뮤니티**: DuRi 개발자 그룹

---

**🚀 DuRi 백업 자동화 시스템으로 안전하고 효율적인 백업을 경험하세요!**
