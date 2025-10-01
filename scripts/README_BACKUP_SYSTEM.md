# 🗂️ DuRi 통합 백업 시스템 사용법

## 🎯 **백업 모드 4종**

### **1. 풀백업 (full) - USB 검증형 100% 백업**
```bash
# 기본값: USB 롤백 검증 가능한 완전 백업
./scripts/duri_backup.sh
./scripts/duri_backup.sh full

# 특징:
# - 모든 파일 포함 (메타데이터, ACL, xattr 보존)
# - USB 이미지가 있으면 즉시 복원 스모크 테스트
# - 파일명: FULL__YYYY-MM-DD__HHMM__host-<host>.tar.zst
```

### **2. 개발 백업 (dev) - 개발 편의 선택 백업**
```bash
./scripts/duri_backup.sh dev

# 특징:
# - 빠른 백업 (불필요한 파일 제외)
# - exclude 규칙 엄격 적용
# - 파일명: DEV__YYYY-MM-DD__HHMM__host-<host>.tar.zst
```

### **3. 확장 백업 (extended) - 중간 단계**
```bash
./scripts/duri_backup.sh extended

# 특징:
# - dev보다 넓은 범위
# - full보다 가벼움
# - 파일명: EXT__YYYY-MM-DD__HHMM__host-<host>.tar.zst
```

### **4. 아티팩트 백업 (artifact) - 산출물 중심**
```bash
./scripts/duri_backup.sh artifact

# 특징:
# - 출시/연구 산출물 중심
# - 테스트/스크립트 등 제외
# - 파일명: ART__YYYY-MM-DD__HHMM__host-<host>.tar.zst
```

---

## 🚀 **빠른 시작**

### **풀백업 (권장)**
```bash
./scripts/duri_backup.sh
```

### **개발용 백업**
```bash
./scripts/duri_backup.sh dev
```

### **기존 스크립트 호환성**
```bash
# 기존 명령어도 그대로 작동
./scripts/unified_backup_full.sh
```

---

## 📁 **백업 저장 위치**

### **USB 백업**
- 경로: `/mnt/usb/`
- 파일: `<PREFIX>__YYYY-MM-DD__HHMM__host-<host>.tar.zst`

### **데스크톱 백업**
- 경로: `/mnt/c/Users/admin/Desktop/두리백업/YYYY/MM/DD/`
- 파일: `<PREFIX>__YYYY-MM-DD__HHMM__host-<host>.tar.zst`

---

## 🔍 **백업 검증**

### **풀백업 모드에서만**
- USB 이미지가 있으면 자동으로 복원 스모크 테스트
- 파일 수 비교 및 복원률 계산
- 복원 성공 여부 확인

### **로그 확인**
- 로그 위치: `/tmp/duri2-backup/` (권한 문제 시)
- 파일명: `run_YYYY-MM-DD__HHMM_<MODE>.log`

---

## ⚙️ **설정 파일**

### **Exclude 규칙**
- `scripts/backup_exclude_dev.txt` - 개발 백업용
- `scripts/backup_exclude_extended.txt` - 확장 백업용
- `scripts/backup_exclude_artifact.txt` - 아티팩트 백업용

### **풀백업**
- exclude 규칙 없음 (모든 파일 포함)

---

## 🎯 **사용자 명령 매핑**

| 사용자 명령 | 백업 모드 | 설명 |
|-------------|-----------|------|
| "풀백업 해" | `full` | USB 검증형 100% 백업 |
| "백업" | `dev` | 개발 편의 선택 백업 |
| "백업백업" | `extended` | 중간 단계 백업 |
| "백업백업백업" | `full` | 풀백업과 동일 |

---

## 🚨 **주의사항**

1. **USB 마운트**: `/mnt/usb` 경로에 USB가 마운트되어 있어야 함
2. **권한**: 로그 디렉토리 권한 문제 시 `/tmp/duri2-backup/` 사용
3. **용량**: 충분한 저장 공간 확보 필요
4. **검증**: 풀백업 모드에서만 USB 롤백 검증 수행

---

## 🔧 **문제 해결**

### **권한 오류**
```bash
# 로그 디렉토리 권한 문제 시
export LOG_DIR="/tmp/duri2-backup"
./scripts/duri_backup.sh full
```

### **USB 마운트 확인**
```bash
ls -la /mnt/usb/
```

### **백업 파일 확인**
```bash
ls -la /mnt/c/Users/admin/Desktop/두리백업/$(date +%Y)/$(date +%m)/$(date +%d)/
```

---

**마지막 업데이트**: 2025-08-17
**작성자**: DuRi AI Assistant
**상태**: ✅ **통합 백업 시스템 완성!**
