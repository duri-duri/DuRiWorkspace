# DuRi 운영 명세서

## 🎯 리스크 분석기 입력 규격

### 입력 데이터 형식
```python
{
    "cpu_usage": float,    # 0.0 ~ 100.0 (음수/100+ 시 clamp 처리)
    "memory_usage": float  # 0.0 ~ 100.0 (음수/100+ 시 clamp 처리)
}
```

### 극단값 처리 규칙
- **음수 값**: `max(0.0, value)` 로 clamp
- **100 초과 값**: `min(100.0, value)` 로 clamp  
- **NaN 값**: `0.0` 으로 처리
- **None/빈 객체**: 기본값 `LOW` 리스크, `0.5` 신뢰도

### 출력 형식
```python
{
    "risk_level": str,        # "LOW" | "MEDIUM" | "HIGH"
    "confidence": float,      # 0.0 ~ 1.0
    "recommendations": [str], # 권장사항 리스트
    "cpu_risk": str,         # CPU 개별 리스크
    "memory_risk": str,      # 메모리 개별 리스크
    "overall_score": float   # 0.0 ~ 1.0 종합 점수
}
```

## 🔧 자율 학습 시스템 명세

### 사이클 ID 형식
```
CYCLE_{YYYYMMDD}_{HHMMSS}_{MICROSECONDS}_{RANDOM_HEX}
예: CYCLE_20251014_134200_123456_abc123
```

### 상태 파일 스키마
```json
{
    "schema_version": "2.0",
    "created_at": "2025-10-14T13:42:00.000000",
    "last_updated": "2025-10-14T13:42:00.000000",
    "cycles": [
        {
            "cycle_id": "CYCLE_20251014_134200_123456_abc123",
            "start_time": "2025-10-14T13:42:00.000000",
            "end_time": "2025-10-14T13:42:00.500000",
            "total_time": 0.5,
            "success": true
        }
    ]
}
```

## 📁 원자적 파일 관리 명세

### 지원 작업
- `atomic_write(data)`: 원자적 쓰기
- `atomic_append(data)`: 원자적 추가 (배열에 append)
- `atomic_read()`: 원자적 읽기
- `get_file_info()`: 파일 정보 조회

### 오류 처리
- **OSError**: 디스크 풀, 권한 거부, 읽기 전용 파일시스템 → `False` 반환
- **JSONDecodeError**: 잘못된 JSON 형식 → `None` 반환
- **임시파일 정리**: 모든 실패 시 자동 정리

### 성능 지표
- 평균 쓰기 시간: < 10ms
- 평균 읽기 시간: < 5ms
- 실패율: < 0.1%

## 📊 로깅 시스템 명세

### 로그 레벨
- **ERROR**: 시스템 오류, 복구 불가능한 문제
- **WARNING**: 주의 필요, 자동 복구 가능
- **INFO**: 일반 정보, 시스템 상태
- **DEBUG**: 상세 디버깅 정보

### 로그 형식
```
{timestamp} - {logger_name} - {level} - {message}
예: 2025-10-14 13:42:00,123 - duri-core - INFO - 시스템 초기화 완료
```

### 로그 파일 관리
- 파일명: `logs/duri-core.log`
- 최대 크기: 10MB
- 백업 개수: 5개
- 인코딩: UTF-8

## 🚨 헬스체크 명세

### 엔드포인트
- `/health`: 기본 헬스체크
- `/ready`: 준비 상태 확인
- `/live`: 생존 상태 확인

### 응답 형식
```json
{
    "status": "healthy|unhealthy",
    "timestamp": "2025-10-14T13:42:00.000000",
    "version": "1.0.0",
    "git_sha": "abc1234",
    "uptime": 3600,
    "checks": {
        "database": "ok",
        "memory": "ok",
        "disk": "ok"
    }
}
```

### 임계치
- **응답 시간**: < 100ms
- **메모리 사용률**: < 80%
- **디스크 사용률**: < 90%
- **CPU 사용률**: < 70%

## 🔄 배포 명세

### 버전 관리
- **Semantic Versioning**: MAJOR.MINOR.PATCH
- **Git 태그**: `v1.0.0` 형식
- **빌드 ID**: `{git_sha}-{timestamp}`

### 롤백 조건
- 헬스체크 실패율 > 5% (5분 지속)
- 응답 시간 > 500ms (평균)
- 오류율 > 1% (5분 지속)
- 메모리 누수 감지

### 모니터링 지표
- **SLA**: 99.9% 가용성
- **RTO**: 5분 (복구 목표 시간)
- **RPO**: 1분 (복구 목표 지점)
