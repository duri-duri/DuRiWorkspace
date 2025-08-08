# DuRi Control System v1.0.0 수동 백업 가이드

## 🎯 백업 목적
- DuRi Control System v1.0.0 최종 완성 버전 백업
- GitHub 100MB 제한을 고려한 최적화된 백업
- 프로덕션 배포 준비 완료 상태 보존

## 📦 백업 명령어

### 1. 기존 백업 파일 정리
```bash
# 현재 디렉토리에서 모든 tar.gz 파일 삭제
find . -name "*.tar.gz" -type f -delete
find . -name "*.zip" -type f -delete
```

### 2. 최종 백업 생성
```bash
# 현재 날짜와 시간으로 백업 파일명 생성
BACKUP_DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="DuRiWorkspace_v1.0.0_final_${BACKUP_DATE}.tar.gz"

# 백업 생성 (backup_exclude.txt 사용)
tar --exclude-from="backup_exclude.txt" -czf "$BACKUP_NAME" .

# 백업 파일 크기 확인
du -h "$BACKUP_NAME"
```

### 3. 백업 파일 무결성 확인
```bash
# 백업 파일 내용 확인
tar -tzf "$BACKUP_NAME" | head -20

# 백업 파일 무결성 검사
tar -tzf "$BACKUP_NAME" > /dev/null && echo "백업 파일 정상" || echo "백업 파일 오류"
```

## 📋 백업 포함 내용

### ✅ 포함되는 파일들
- **소스 코드**: duri_control/, duri_core/, duri_brain/, duri_evolution/
- **Docker 설정**: docker-compose.yml, docker/ 디렉토리
- **자동화 스크립트**: deploy/ 디렉토리
- **문서**: README.md, CHANGELOG.md, BACKUP_INFO.md
- **환경 설정**: deploy/env.prod.example
- **테스트 코드**: duri_control/tests/
- **공통 모듈**: duri_common/
- **설정 파일**: config/ 디렉토리

### ❌ 제외되는 파일들
- **기존 백업 파일들**: *.tar.gz, *.zip
- **로그 파일들**: logs/, *.log, *.txt
- **Git 저장소**: .git/
- **캐시 파일들**: __pycache__/, *.pyc
- **환경 변수**: .env (보안상)
- **임시 파일들**: *.tmp, .cache/
- **IDE 설정**: .vscode/, .idea/
- **스냅샷 디렉토리**: duri_snapshots/, backup/, backups/

## 🔍 백업 전 확인사항

### 시스템 상태 확인
```bash
# Docker 컨테이너 상태
docker-compose ps

# API 서버 상태
curl http://localhost:8083/health/

# 서비스 초기화 상태
curl http://localhost:8083/health/services
```

### 중요 파일 존재 확인
```bash
# 필수 파일들 확인
ls -la docker-compose.yml
ls -la deploy/
ls -la duri_control/
ls -la README.md
ls -la CHANGELOG.md
```

## 💾 백업 복원 방법

### 1. 백업 파일 압축 해제
```bash
tar -xzf DuRiWorkspace_v1.0.0_final_YYYYMMDD_HHMMSS.tar.gz
```

### 2. 프로젝트 디렉토리로 이동
```bash
cd DuRiWorkspace
```

### 3. 환경 변수 설정
```bash
cp deploy/env.prod.example .env
# .env 파일을 편집하여 필요한 설정 변경
```

### 4. 시스템 빌드 및 시작
```bash
# 전체 시스템 빌드
./deploy/build_all.sh

# 서비스 시작 (헬스 체크 포함)
./deploy/start_services.sh --wait --health-check
```

### 5. 시스템 상태 확인
```bash
# API 문서 확인
curl http://localhost:8083/docs

# 서비스 상태 확인
curl http://localhost:8083/monitor/services
```

## 📊 예상 백업 크기

### 백업 크기 예상
- **소스 코드**: ~10MB
- **Docker 설정**: ~1MB
- **문서**: ~1MB
- **자동화 스크립트**: ~1MB
- **총 예상 크기**: ~15-20MB

### GitHub 호환성
- GitHub 파일 크기 제한: 100MB
- 예상 백업 크기: 15-20MB
- ✅ GitHub 업로드 가능

## 🚨 주의사항

### 보안
- `.env` 파일은 백업에서 제외됩니다 (보안상)
- 프로덕션 환경에서는 반드시 `.env` 파일을 별도로 관리하세요

### 복원 시
- 백업 복원 후 반드시 환경 변수를 설정하세요
- Docker 이미지 재빌드가 필요할 수 있습니다
- 데이터베이스 초기화가 필요할 수 있습니다

## 📞 문제 해결

### 백업 실패 시
```bash
# 디스크 공간 확인
df -h

# 권한 확인
ls -la

# tar 명령어 수동 실행
tar --exclude-from="backup_exclude.txt" -czf test_backup.tar.gz .
```

### 복원 실패 시
```bash
# 백업 파일 무결성 확인
tar -tzf backup_file.tar.gz

# 충돌하는 파일 확인
ls -la

# Docker 컨테이너 정리
docker-compose down --remove-orphans
```

---

**백업 생성일**: 2025-07-25  
**DuRi Control System 버전**: v1.0.0  
**상태**: 최종 완성 버전 