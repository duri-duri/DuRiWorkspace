# Emotion Async (202 Fast-Path) 운영 가이드

## 개요

`/emotion` 엔드포인트가 즉시 202 응답을 반환하고, 실제 처리는 백그라운드에서 수행됩니다.

## 환경 변수

- `EMOTION_ASYNC=1`: 비동기 경로 활성화 (기본값, 202 응답)
- `EMOTION_ASYNC=0`: 동기 경로 (롤백용, 200 응답)

## 개발 루프 (빠른 검증)

`docker-compose.override.yml` 사용:

```yaml
services:
  duri-core:
    environment:
      - EMOTION_ASYNC=1
    volumes:
      - ./duri_core:/app/duri_core:ro
```

**장점**: 즉시 반영, 디버깅 빠름  
**리스크**: 이미지 재현성↓, 본판과 차이날 수 있음

## 운영 루프 (재현성/안정)

### 1. 이미지 빌드

```bash
docker compose build duri-core
docker compose up -d duri-core
```

### 2. 환경변수 주입

`docker-compose.yml`에 영구 반영:

```yaml
services:
  duri-core:
    environment:
      - EMOTION_ASYNC=1
```

### 3. 헬스체크

```bash
curl -sS http://localhost:8080/health
curl -sS http://localhost:8080/
```

### 4. 스모크 테스트

```bash
bash scripts/test_emotion_202.sh
```

**기대값**: `[OK] 202 + job_id 확인`

## 롤백 절차

1. `EMOTION_ASYNC=0`로 재기동:

```bash
EMOTION_ASYNC=0 docker compose up -d duri-core
```

2. 클라이언트 타임아웃 임시 상향 (20-25s)

## 모니터링

- HTTP 상태코드 202 비율 ≥ 0.9
- 500 에러 스파이크 알람
- job 처리 시간 (백그라운드)

## 문제 해결

### 다시 500 발생

- `url_for` 네임스페이스 확인 (`api.emotion_status`)
- Flask Blueprint 등록 순서 확인

### 202인데 job_id 없음

- 응답 스키마 validation 추가
- enqueue 실패 시 409/503 분기

### override가 무시됨

```bash
docker compose config | grep -A 20 duri-core
docker inspect duri-core | jq '.[0].Mounts'
```
