# DuRi Emotion Processing System

DuRi는 감정 기반 의사결정 시스템입니다.

## 시스템 구성

### DuRi Core
감정을 기반으로 판단을 내리는 핵심 의사결정 시스템

### DuRi Brain
감정-판단-반응 루프의 전후 데이터를 연결하여 Core의 통계 기반 판단을 향상시키는 시스템

## 주요 기능

### Core 기능
- 감정 기반 의사결정
- 통계 기반 액션 선택
- 감정별 특별 규칙 적용
- 진화 로그 관리
- **감정 요청/응답 로깅**
  - 요청 내용을 파일과 데이터베이스에 저장
  - 응답 결과를 파일과 데이터베이스에 저장
  - 처리 시간 및 성능 모니터링

### Brain 기능
- 감정 입력 기록 및 추적
- 외부 피드백 수집
- 완전한 루프 관리
- 학습 데이터 생성
- 성능 인사이트 제공

## 빠른 시작

### Brain 시스템 예제 실행
```bash
python examples/brain_example.py
```

### 기본 테스트
```bash
python test_simple.py
```

### 감정 로깅 테스트
```bash
python test_emotion_logging.py
```

### 전체 테스트 (unittest)
```bash
python tests/test_decision_logic.py
```

## 로깅 시스템

### 파일 로깅
- **요청 로그**: `LOG_DIR/YYYY-MM-DD_emotion_requests.json`
- **응답 로그**: `LOG_DIR/YYYY-MM-DD_emotion_responses.json`
- JSON Lines 형식으로 저장되어 분석하기 쉬움
- 날짜별로 자동으로 파일이 생성됨 (예: `2025-06-28_emotion_requests.json`)

### 데이터베이스 로깅
- **요청 테이블**: `core.emotion_requests`
- **응답 테이블**: `core.emotion_responses`
- PostgreSQL을 사용하여 구조화된 데이터 저장

### 로그 내용
- 요청 ID (고유 식별자)
- 감정 데이터
- 클라이언트 정보 (IP, User-Agent)
- 처리 시간
- 응답 상태 (성공/실패)
- 타임스탬프

### 환경변수 설정
```bash
# .env 파일에 추가
LOG_DIR=/app/logs
DATABASE_URL=postgresql://duri:duri@duri-postgres:5432/duri
```

### 로그 관리 도구
로그 파일 관리를 위한 유틸리티 스크립트가 제공됩니다:

```bash
# 특정 날짜의 로그 통계 확인
python scripts/log_manager.py --action stats --date 2025-06-28

# 날짜 범위의 로그 통계 확인
python scripts/log_manager.py --action stats --start-date 2025-06-01 --end-date 2025-06-30

# 오래된 로그 파일 정리 (30일 이상)
python scripts/log_manager.py --action cleanup --days 30

# 로그 데이터 내보내기
python scripts/log_manager.py --action export --start-date 2025-06-01 --end-date 2025-06-30 --output logs_export.json
```

## 패턴 시각화

### 성공률 Heatmap 생성
`experience_stats.json` 파일을 기반으로 감정-행동 조합별 성공률을 시각화합니다:

```bash
# 기본 사용법 (experience_stats.json 파일 사용)
python scripts/visualize_patterns.py

# 특정 통계 파일 사용
python scripts/visualize_patterns.py --stats-file my_stats.json

# 출력 파일 지정
python scripts/visualize_patterns.py --output my_heatmap.pdf
```

### 시각화 결과
- **Heatmap**: 감정(행)과 행동(열) 조합별 성공률을 색상으로 표시
- **통계 요약**: 전체, 감정별, 행동별 성공률 통계
- **최고/최저 성공률**: 가장 효과적인/비효과적인 조합 식별
- **PDF 출력**: 고해상도 PDF 파일로 저장

### 필요한 라이브러리
```bash
pip install matplotlib seaborn pandas numpy
```

## 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Emotion       │    │   DuRi Core     │    │   External      │
│   Input         │───▶│   Decision      │───▶│   Feedback      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DuRi Brain                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ Emotion     │  │ Loop        │  │ Feedback    │            │
│  │ Recorder    │  │ Manager     │  │ Collector   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                Brain Controller                             │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 테스트 내용

### Core 테스트
- 알려진 감정들이 fallback이 아닌 액션을 반환하는지 검증
- 알 수 없는 감정들이 fallback 액션을 적절한 이유와 함께 반환하는지 검증
- 다양한 의사결정 방법 (통계 기반, 규칙 기반, fallback) 검증
- 감정 레벨 검증
- 감정별 규칙 적용 검증

### Brain 테스트
- 감정-판단-반응 루프의 완전한 생명주기 검증
- 외부 피드백 수집 및 처리 검증
- 학습 데이터 생성 및 활용 검증
- 세션 관리 및 통계 수집 검증

### 로깅 테스트
- 감정 요청/응답 로깅 기능 검증
- 파일 및 데이터베이스 저장 검증
- 처리 시간 측정 검증
- 오류 처리 및 로깅 검증

## 문서

- [Brain 시스템 상세 문서](brain/README.md)
- [테스트 가이드](tests/README.md)
- [개발 노트](DEV_NOTES.md)
- [Core 정체성](CORE_IDENTITY.md)
- [Docker 배포 가이드](DOCKER_DEPLOYMENT.md)
