# 🗂️ DuRi 백업 및 롤백 완전 가이드

> **⚠️ 중요**: 이 문서는 백업 시 반드시 참조해야 하는 핵심 문서입니다!
> 롤백 작업 전에 반드시 이 가이드를 확인하세요.

---

## 📊 백업 파일 전수 조사 결과

### **1. 대형 백업 파일들 (600MB+ 대)**
- **`DuRi_Backup_Phase6_20250807_172145.tar.gz`** (679M) - 8월 7일 17:22
- **`DuRi_Backup_Phase5_20250807_165308.tar.gz`** (679M) - 8월 7일 16:53  
- **`DuRi_Backup_Phase4_20250807_163323.tar.gz`** (678M) - 8월 7일 16:33
- **`DuRi_Phase6_Completion_Backup_20250729_132725.tar.gz`** (634M) - 7월 29일
- **`DuRiWorkspace_20250727_1634_complete_backup.tar.gz`** (631M) - 7월 27일

### **2. 중형 백업 파일들 (47MB)**
- **`DuRi_BackupBackupBackup_20250810_224813.tar.gz`** (47M) - 8월 10일 22:48
- **`DuRi_Backup_20250810_224720.tar.gz`** (47M) - 8월 10일 22:47
- **`DuRi_Backup_20250810_224713.tar.gz`** (47M) - 8월 10일 22:47
- **`DuRi_BackupBackup_20250810_224756.tar.gz`** (47M) - 8월 10일 22:47

### **3. 소형 백업 파일들 (3.4-3.6MB)**
- **통합 시스템 백업들** (3.5M):
  - `unified_performance_optimizer_backup.tar.gz`
  - `unified_learning_system_backup.tar.gz`
  - `unified_judgment_system_backup.tar.gz`
  - `unified_conversation_service_backup.tar.gz`
  - `performance_monitor_backup.tar.gz`

- **추론 시스템 백업들** (3.4M):
  - `abductive_reasoning_backup.tar.gz`
  - `deductive_reasoning_backup.tar.gz`
  - `inductive_reasoning_backup.tar.gz`
  - `logical_processor_backup.tar.gz`
  - `reasoning_engine_backup.tar.gz`
  - `conflict_resolver_backup.tar.gz`

---

## 🗂️ 백업 파일 보관 구조

### **A. 메인 백업 위치**
```
/home/duri/DuRiWorkspace/
├── DuRi_Backup_Phase*.tar.gz (600MB+ 대형 백업)
├── DuRi_Backup*.tar.gz (47MB 중형 백업)
└── DuRi_*_Backup*.tar.gz (3-7MB 소형 백업)
```

### **B. DuRiCore 전용 백업 위치**
```
/home/duri/DuRiWorkspace/DuRiCore/backups/
├── unified_*.tar.gz (3.5MB 통합 시스템)
└── *_reasoning_*.tar.gz (3.4MB 추론 시스템)
```

### **C. 백업 백업 위치**
```
/home/duri/DuRiWorkspace/backup/DuRiCore/backups/
├── unified_*.tar.gz (3.5MB 통합 시스템)
└── *_reasoning_*.tar.gz (3.4MB 추론 시스템)
```

### **D. 백업 저장소 위치**
```
/home/duri/DuRiWorkspace/backup_repository/
└── learning_system_fully_activated_20250808_091854/
    └── DuRiCore/backups/
        ├── unified_*.tar.gz (3.5MB)
        └── *_reasoning_*.tar.gz (3.4MB)
```

---

## 🔄 정확한 롤백 방법

### **1. 전체 시스템 롤백 (600MB+ 백업)**
```bash
# Phase6 최신 백업으로 롤백
cd /home/duri/DuRiWorkspace
tar -xzf DuRi_Backup_Phase6_20250807_172145.tar.gz

# 또는 Phase5 백업으로 롤백
tar -xzf DuRi_Backup_Phase5_20250807_165308.tar.gz
```

### **2. 핵심 모듈 롤백 (47MB 백업)**
```bash
# 최신 백업백업백업으로 롤백
tar -xzf DuRi_BackupBackupBackup_20250810_224813.tar.gz

# 또는 일반 백업으로 롤백
tar -xzf DuRi_Backup_20250810_224720.tar.gz
```

### **3. 개별 시스템 롤백 (3.4-3.6MB 백업)**
```bash
# 통합 시스템 롤백
cd /home/duri/DuRiWorkspace/DuRiCore/backups
tar -xzf unified_performance_optimizer_backup.tar.gz

# 추론 시스템 롤백
tar -xzf abductive_reasoning_backup.tar.gz
```

---

## 🔍 사용자 정의 백업 시스템 정리

### **A. 3단계 백업 구조 확인**
- **1단계**: `DuRi_Backup_*.tar.gz` (47MB) - 일반 백업
- **2단계**: `DuRi_BackupBackup_*.tar.gz` (47MB) - 백업 백업  
- **3단계**: `DuRi_BackupBackupBackup_*.tar.gz` (47MB) - 백업 백업 백업

### **B. 백업 스크립트 위치**
- **`duri-backup.sh`** - 1단계 백업
- **`duri-backup-backup.sh`** - 2단계 백업
- **`duri-backup-backup-backup.sh`** - 3단계 백업

### **C. 백업 우선순위**
1. **최신 백업백업백업** (8월 10일 22:48) - 가장 안전
2. **일반 백업** (8월 10일 22:47) - 표준 백업
3. **백업 백업** (8월 10일 22:47) - 중간 안전도
4. **Phase 백업** (8월 7일) - 전체 시스템 백업

---

## 🚨 백업 명령 시 반드시 지켜야 할 원칙

### **⚠️ 핵심 원칙 1: 백업 요청 중요도에 따른 차별화**
- **"백업"** → 일반 백업 (기본 수준, 핵심 파일만)
- **"백업백업"** → 중요 백업 (중간 수준, 중요 파일 + 추가 파일)
- **"백업백업백업"** → 완벽한 복제 수준 (최고 수준, 모든 파일 + 복제 가이드)

### **⚠️ 핵심 원칙 2: 백업 저장 위치**
- **올바른 위치**: `/mnt/c/Users/admin/Desktop/두리백업/` (바탕화면)
- **잘못된 위치**: `/home/duri/DuRiWorkspace/` (duri_head 내부)
- **백업은 반드시 바탕화면의 "두리백업" 폴더에 저장**

### **⚠️ 핵심 원칙 3: 3단계 백업 시스템의 진짜 목적**
- 단순한 파일 백업이 아님
- **완벽한 시스템 복제**까지 가능한 수준의 백업
- 각 단계별로 포함되는 파일의 범위와 상세도가 다름

### **⚠️ 핵심 원칙 4: 백업 실행 전 확인사항**
1. **백업 위치 확인**: 바탕화면 "두리백업" 폴더인지 확인
2. **백업 수준 확인**: 요청된 백업 수준에 맞는 스크립트 사용
3. **저장 공간 확인**: 바탕화면에 충분한 공간 확보
4. **백업 완료 후**: 바탕화면에 파일이 제대로 저장되었는지 확인

---

## ⚠️ 롤백 권장사항

### **1. 안전한 롤백 순서**
1. **현재 상태 백업** → 2. **테스트 환경에서 검증** → 3. **실제 롤백 실행**

### **2. 롤백 전 체크리스트**
- [ ] 백업 파일 무결성 확인 (`tar -tzf` 명령어로)
- [ ] 충분한 디스크 공간 확보
- [ ] 현재 작업 중인 파일들 저장
- [ ] 롤백 후 시스템 상태 확인 계획

### **3. 롤백 후 검증**
- [ ] 핵심 기능 동작 확인
- [ ] 파일 구조 정상 여부 확인
- [ ] 시스템 성능 테스트
- [ ] 필요시 추가 롤백 준비

---

## 🚨 긴급 롤백 시나리오

### **시나리오 1: 전체 시스템 문제 발생**
```bash
# 1. 현재 상태 백업
tar -czf emergency_backup_$(date +%Y%m%d_%H%M%S).tar.gz .

# 2. Phase6 백업으로 롤백
tar -xzf DuRi_Backup_Phase6_20250807_172145.tar.gz

# 3. 시스템 상태 확인
ls -la DuRiCore/
python3 DuRiCore/test_safety_controller.py
```

### **시나리오 2: 핵심 모듈 문제 발생**
```bash
# 1. 문제 모듈 백업
tar -czf problem_module_backup_$(date +%Y%m%d_%H%M%S).tar.gz DuRiCore/

# 2. 백업백업백업으로 롤백
tar -xzf DuRi_BackupBackupBackup_20250810_224813.tar.gz

# 3. 모듈 동작 확인
python3 DuRiCore/test_safety_controller.py
```

### **시나리오 3: 개별 시스템 문제 발생**
```bash
# 1. 문제 시스템 백업
tar -czf problem_system_backup_$(date +%Y%m%d_%H%M%S).tar.gz DuRiCore/

# 2. 해당 시스템 백업으로 롤백
cd DuRiCore/backups
tar -xzf unified_performance_optimizer_backup.tar.gz

# 3. 시스템 동작 확인
python3 test_safety_controller.py
```

---

## 📝 백업 파일 검증 명령어

### **1. 백업 파일 내용 확인**
```bash
# 백업 파일 내부 구조 확인
tar -tzf DuRi_Backup_Phase6_20250807_172145.tar.gz | head -20

# 백업 파일 크기 및 날짜 확인
ls -lh *.tar.gz | sort -k5 -hr
```

### **2. 백업 파일 무결성 검사**
```bash
# 백업 파일 무결성 확인
tar -tzf DuRi_Backup_Phase6_20250807_172145.tar.gz > /dev/null && echo "백업 파일 정상" || echo "백업 파일 손상"
```

### **3. 백업 파일 압축 해제 테스트**
```bash
# 임시 디렉토리에서 압축 해제 테스트
mkdir test_extract
cd test_extract
tar -xzf ../DuRi_Backup_Phase6_20250807_172145.tar.gz
ls -la
cd ..
rm -rf test_extract
```

---

## 🔗 관련 문서 및 스크립트

### **백업 관련 문서**
- `BACKUP_INFO.md` - 백업 시스템 개요
- `AUGUST_6_7_WORK_SUMMARY.md` - 8월 6-7일 작업 요약
- `REFACTORING_PLAN.md` - 리팩토링 계획

### **백업 스크립트**
- `duri-backup.sh` - 1단계 백업
- `duri-backup-backup.sh` - 2단계 백업
- `duri-backup-backup-backup.sh` - 3단계 백업

### **시스템 파일**
- `integrated_evolution_system.py` - 통합 진화 시스템
- `test_safety_controller.py` - 안전성 컨트롤러 테스트

---

## 📅 백업 파일 생성 일정

### **8월 7일 백업**
- Phase4, Phase5, Phase6 백업 (600MB+)
- 3단계 통합 학습 시스템 백업
- 전략 판단 4단계 통합 시스템 백업

### **8월 8일 백업**
- learning_system_fully_activated 백업
- 통합 시스템 및 추론 시스템 백업

### **8월 10일 백업**
- 백업, 백업백업, 백업백업백업 (47MB)
- DuRiCore 모듈별 백업

---

## 🎯 롤백 시 주의사항

1. **백업 파일 우선순위 준수**: 백업백업백업 → 백업 → 백업백업 순서
2. **롤백 전 현재 상태 백업**: 문제 발생 시 원인 분석을 위해
3. **단계별 롤백**: 전체 → 모듈 → 개별 시스템 순서로 진행
4. **검증 필수**: 롤백 후 반드시 시스템 동작 확인
5. **문서화**: 롤백 과정과 결과를 반드시 기록

---

## 📊 2025-08-10 백업 진행 상황

### **🎯 오늘(2025-08-10) 실행한 3가지 백업 수준**

#### **1단계 — 폴더 확인 및 생성 ✅**
- **바탕화면 "두리백업" 폴더**: `/mnt/c/Users/admin/Desktop/두리백업` 존재 확인
- **2025-08 폴더**: 생성 완료
- **당일 날짜 폴더**: `2025-08-10` 생성 완료

#### **2단계 — 대형 백업 파일 복사 ✅**
- **5개 대형 백업 파일** (600MB+) 복사 완료:
  - Phase4~6 백업 파일들
  - Completion 백업 파일
  - Workspace 전체 백업 파일

#### **3단계 — 중형 백업 파일 복사 ✅**
- **4개 중형 백업 파일** (47MB) 복사 완료:
  - `DuRi_BackupBackupBackup_20250810_224813.tar.gz`
  - `DuRi_Backup_20250810_224720.tar.gz`
  - `DuRi_Backup_20250810_224713.tar.gz`
  - `DuRi_BackupBackup_20250810_224756.tar.gz`

#### **4단계 — 소형 모듈 백업 복사 🔄 (진행 예정)**
- **통합 시스템 백업 세트** (3.5MB):
  - `unified_performance_optimizer_backup.tar.gz`
  - `unified_learning_system_backup.tar.gz`
  - `unified_judgment_system_backup.tar.gz`
  - `unified_conversation_service_backup.tar.gz`
  - `performance_monitor_backup.tar.gz`

- **추론 시스템 백업 세트** (3.4MB):
  - `abductive_reasoning_backup.tar.gz`
  - `deductive_reasoning_backup.tar.gz`
  - `inductive_reasoning_backup.tar.gz`
  - `logical_processor_backup.tar.gz`
  - `reasoning_engine_backup.tar.gz`
  - `conflict_resolver_backup.tar.gz`

### **📁 바탕화면 "두리백업" 폴더 구조**
```
/mnt/c/Users/admin/Desktop/두리백업/
├── 2025-08/
│   └── 2025-08-10/
│       ├── 대형백업/ (600MB+ 파일들)
│       ├── 중형백업/ (47MB 파일들)
│       └── 소형백업/ (3.4-3.6MB 파일들 - 예정)
└── README.md (백업 파일 설명서)
```

---

## 🎯 다음 단계 계획

### **즉시 진행할 작업**
1. **소형 모듈 백업 복사**: 통합 시스템 + 추론 시스템 백업 세트
2. **백업 파일 검증**: 복사된 파일들의 무결성 확인
3. **백업 완료 보고서**: 전체 백업 현황 정리

### **백업 완료 후 검증 작업**
1. **파일 크기 확인**: 각 백업 수준별 적절한 크기인지 검증
2. **파일 내용 확인**: 백업 파일 내부 구조 검증
3. **롤백 테스트**: 임시 환경에서 백업 파일 복원 테스트

---

## 📋 백업 진행 상황 체크리스트

### **✅ 완료된 작업**
- [x] 바탕화면 "두리백업" 폴더 구조 생성
- [x] 대형 백업 파일 5개 복사 (600MB+)
- [x] 중형 백업 파일 4개 복사 (47MB)
- [x] 날짜별 폴더 정리

### **🔄 진행 중인 작업**
- [ ] 소형 모듈 백업 파일 복사 (3.4-3.6MB)
- [ ] 백업 파일 무결성 검증
- [ ] 백업 완료 보고서 작성

### **📅 예정된 작업**
- [ ] 롤백 테스트 환경 구축
- [ ] 백업 파일 사용법 가이드 작성
- [ ] 정기 백업 스케줄 설정

---

> **📌 2025-08-10은 중요한 날이어서 백업, 백업백업, 백업백업백업을 모두 실행했습니다.**
> **평상시에는 필요에 따라 하나의 백업 수준만 실행하면 됩니다.**
