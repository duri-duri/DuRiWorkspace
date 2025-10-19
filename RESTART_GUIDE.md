**📋 Cursor 재시작 후 작업 이어가기 가이드**

## 🎯 현재 진행 상황

### ✅ 완료된 작업:
- Shadow Guard Redis 표준화 (rps_limit, log_sample, ingest_enabled)
- 데이터 오염 방지 격리 스키마 (shadow_guard.emotion_events)
- duri_core/duri_evolution Docker 시스템 복구
- 모든 Docker 서비스 정상 실행 (9개 서비스 healthy)

### 🔄 현재 상태:
- **Shadow 훈련장 활용도**: 80% (트래픽 수신은 되지만 DB 기록 안됨)
- **문제**: track 제약조건에서 'shadow' 제외됨
- **해결 필요**: feedback_events에 shadow 트래픽 기록
## 🚀 재시작 후 즉시 실행할 명령어들

### 1. Docker 서비스 상태 확인:
```bash
cd /home/duri/DuRiWorkspace
docker compose -p duriworkspace ps
```

### 2. Shadow 훈련장 상태 확인:
```bash
docker compose -p duriworkspace exec duri-redis redis-cli MGET shadow:enabled canary:enabled canary:ratio
```

### 3. Shadow 트래픽 테스트:
```bash
curl -X POST http://localhost:8083/emotion -H "Content-Type: application/json" -H "X-DuRi-Shadow: 1" -d '{"emotion": "happy", "context": "shadow_test"}'
```
## 📝 남은 작업 목록

### 🎯 우선순위 높음:
1. **Shadow 트래픽 DB 기록 문제 해결**
   - track 제약조건에 'shadow' 추가
   - 또는 duri_control에서 'cand'로 기록하도록 수정

2. **Shadow 훈련장 100% 활용도 달성**
   - 현재 80% → 목표 100%

### 🔧 추가 작업:
3. 로그 노이즈 억제 (샘플링·레벨·보존)
4. 컨트롤러 보호 (서킷 브레이커·재시도·백프레셔)
5. 모니터링/알림 (Prometheus 룰 및 대시보드)
6. 배포 스크립트 3종 생성
