# 커서 재시작 후 즉시 실행할 명령어들

## 🚀 **1단계: 서버 상태 확인**

```bash
# 현재 실행 중인 서버 확인
ps aux | grep uvicorn

# 포트 사용 상황 확인
ss -tlnp | grep :8001

# 서버 응답 테스트
curl -s http://localhost:8001/health
```

**예상 결과**: `{"status":"ok"}`

## 🔧 **2단계: 서버 재시작 (필요시)**

만약 서버가 응답하지 않으면:

```bash
# 기존 서버 종료
pkill -f "uvicorn"

# 서버 재시작
cd ~/DuRiWorkspace/duri_core
PYTHONPATH=/home/duri/DuRiWorkspace DB_HOST=localhost DB_PASSWORD=duri123 DB_USER=duri DB_NAME=duri_db python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## 📋 **3단계: 현재 상황 확인**

```bash
# 현재 디렉토리 구조 확인
ls -la ~/DuRiWorkspace/

# 백업 파일들 확인
ls -la ~/DuRiWorkspace/*backup*.md
ls -la ~/DuRiWorkspace/*progress*.md
ls -la ~/DuRiWorkspace/*separation*.md
```

## 🎯 **4단계: 다음 작업 선택**

### **옵션 A: Cursor Extension 완성**
```bash
# Extension 설정 파일 수정 (포트 8001로 변경)
# Extension 빌드 및 설치
# 통신 테스트
```

### **옵션 B: 노드 분리 시작**
```bash
# brain 노드 분리 시작
cd ~/DuRiWorkspace
mkdir -p duri_brain
# (분리 작업 계속...)
```

### **옵션 C: 자동화 파이프라인 구현**
```bash
# 대화 필터링 로직 구현
# 대화 요약 및 분석 기능
# 메모리 시스템과의 연동
```

## 📊 **현재 상태 요약**

### **✅ 완료된 작업들**
- 서버 인프라 정리 (포트 8001에서 정상 작동)
- 환경 변수 표준화
- API 엔드포인트 구현 (/health, /status, /judge, /learn)
- 노드 분리 계획 수립

### **🎯 다음 우선순위**
1. **Cursor Extension 완성** - 실시간 대화 캡처
2. **brain 노드 분리** - 판단 시스템 독립화
3. **evolution 노드 분리** - 학습 시스템 독립화
4. **control 노드 분리** - 제어 시스템 독립화

### **📁 중요한 파일들**
- `backup_duri_progress_2025_08_01.md` - 오늘 백업
- `duri_progress_summary_2025_08_01.md` - 진행 상황 요약
- `duri_node_separation_plan.md` - 노드 분리 계획
- `restart_instructions.md` - 이 파일

## 🚨 **문제 해결**

### **포트 충돌 시**
```bash
# 포트 8000 정리
sudo lsof -ti:8000 | xargs kill -9

# 또는 다른 포트 사용
# 포트 8002, 8003 등으로 변경
```

### **서버 응답 없을 때**
```bash
# 프로세스 강제 종료
sudo pkill -9 -f "uvicorn"

# 서버 재시작
cd ~/DuRiWorkspace/duri_core
PYTHONPATH=/home/duri/DuRiWorkspace DB_HOST=localhost DB_PASSWORD=duri123 DB_USER=duri DB_NAME=duri_db python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

---

**마지막 업데이트**: 2025-08-01
**상태**: 서버 정상 작동 중, 노드 분리 준비 완료
