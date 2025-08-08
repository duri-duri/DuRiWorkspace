# Tests Directory

이 디렉토리는 DuRi Emotion Processing System의 테스트 파일들을 포함합니다.

## 파일 구조

- `test_decision_logic.py`: 의사결정 로직에 대한 포괄적인 테스트
- `test_emotion_vector.py`: 감정 벡터 처리 테스트
- `__init__.py`: 테스트 패키지 초기화

## 테스트 실행 방법

### 개별 테스트 실행
```bash
python tests/test_decision_logic.py
```

### 모든 테스트 실행
```bash
python -m pytest tests/
```

## 테스트 커버리지

### test_decision_logic.py
- 알려진 감정들이 non-fallback 액션을 반환하는지 검증
- 알 수 없는 감정들이 fallback 액션을 적절한 이유와 함께 반환하는지 검증
- 통계 기반 의사결정 검증
- 규칙 기반 의사결정 검증
- 감정별 특별 규칙 적용 검증
- 감정 레벨 검증
- 다양한 의사결정 방법 검증

### test_emotion_vector.py
- 감정 벡터 처리 및 변환 테스트
- 감정 데이터 유효성 검증
- 벡터 연산 테스트 