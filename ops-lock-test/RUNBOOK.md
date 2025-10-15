# DuRi 운영 런북

## 증상: 헬스 5xx / 스크레이프 실패

### 1단계: 로그 확인
```bash
make logs
```

### 2단계: 스모크 테스트 재확인
```bash
make smoke
```

### 3단계: 의존 서비스 상태 확인
```bash
docker compose ps
```

### 4단계: 컨테이너 재시작
```bash
make restart
```

### 5단계: 실패 시 이전 태그로 롤백
```bash
git checkout v1.0.0-lock && docker compose up -d --build
```

## 안정 태그로 즉시 롤백
```bash
git checkout v1.0.1-opslock && docker compose up -d --build
make smoke
```

## 빠른 명령어
- `make up` - 서비스 기동
- `make down` - 서비스 중지
- `make restart` - 서비스 재시작
- `make smoke` - 스모크 테스트
- `make logs` - 로그 확인
