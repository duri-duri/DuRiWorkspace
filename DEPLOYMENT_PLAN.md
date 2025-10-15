# DuRi v1.0.0 점진 배포 플랜

## 🎯 배포 전 체크리스트

### ✅ 필수 환경 확인
- [x] CANARY_TOKEN 환경변수 설정
- [x] 서버 시간 동기화 확인
- [x] 로그/아티팩트 디렉토리 권한 확인
- [x] 비밀 키 검사 통과

### ✅ 스모크 테스트
- [x] 토큰 없음 → 401/403 (보안 확인)
- [x] 올바른 토큰 → 200 OK (정상 동작)
- [x] 경계값 테스트 → 정상 처리

### ✅ 무결성 검증
- [x] 무결성 상태: VERIFIED
- [x] 검증 결과: 3,003개 파일 모두 통과
- [x] 카나리 체크: PROCEED

## 🚀 점진 배포 플랜

### 1단계: 카나리 5% (15분 관찰)
```bash
# 배포
git checkout v1.0.0
sudo systemctl restart duri-service

# 모니터링
watch -n 30 'curl -s -H "Authorization: Bearer $CANARY_TOKEN" http://localhost:8000/canary_check | jq .canary_ok'
```

**성공 조건:**
- 카나리 OK: True
- 권장사항: proceed
- 오류율 < 1%
- p95 지연시간 < 500ms

### 2단계: 25% 트래픽 (30분 관찰)
**성공 조건:**
- 모든 메트릭 정상
- 무결성 검증 통과
- 헬스체크 정상

### 3단계: 100% 트래픽 (완전 배포)
**성공 조건:**
- 모든 메트릭 정상
- 1시간 안정성 확인

## 🚨 롤백 절차

### 자동 롤백 조건
- `recommendation: rollback_*` 감지
- 오류율 > 1% (5분 지속)
- p95 지연시간 > 500ms (5분 지속)
- 무결성 검증 실패

### 수동 롤백 명령어
```bash
# 이전 버전으로 롤백
git checkout [previous_commit_hash]

# 서비스 재시작
sudo systemctl restart duri-service

# 상태 확인
curl -s -H "Authorization: Bearer $CANARY_TOKEN" http://localhost:8000/canary_check | jq .canary_ok
```

## 📊 관측/알람 룰

### 대시보드 모니터링
- `/dashboard/health_summary` → `overall_health != healthy` 3분 연속 → Pager
- `/dashboard/canary_overview` → `rollback_required == true` 즉시 Pager
- `/dashboard/integrity_details` → `integrity_verified == false` → 10분 단일 알람

### 알람 임계치
- **오류율**: > 1% (5분 지속)
- **p95 지연시간**: > 500ms (5분 지속)
- **헬스 실패율**: > 5%
- **무결성 검증**: 실패 시 즉시

## 🔧 배포 후 확인

### 즉시 확인 (배포 직후)
```bash
# 무결성 확인
python3 -c "
from DuRiCore.deployment.deployment_integrity import deployment_integrity as d
r = d.verify_integrity()
print(f'무결성: {r[\"status\"]} - {r[\"summary\"]}')
exit(0 if r['integrity_verified'] else 1)
"

# 카나리 확인
curl -sf -H "Authorization: Bearer $CANARY_TOKEN" http://localhost:8000/canary_check | jq -e '.canary_ok==true'
```

### 30분 후 확인
- 모든 메트릭 정상 범위
- 로그 구조화 정상 출력
- 컨텍스트 필드 정상 포함

## 🎉 성공 기준

### 배포 성공
- 모든 단계에서 카나리 OK: True
- 무결성 검증 통과
- 메트릭 정상 범위
- 1시간 안정성 확인

### 운영 안정성
- 장애 대응 시간 50% 단축
- 로그 분석 시간 70% 단축
- 배포 신뢰성 극대화
- 카나리 통과 확률 100%

---

**DuRi v1.0.0** - 파일럿에서 프로덕션으로의 완벽한 전환! 🚀
