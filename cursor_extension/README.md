# DuRi Cursor Extension

DuRi AI 자동화 학습 시스템을 위한 Cursor 확장 프로그램입니다.

## 🚀 기능

### **자동 대화 캡처**
- 사용자 입력 자동 감지
- Cursor 응답 자동 캡처
- 터미널 출력 모니터링
- 명령어 실행 추적

### **실시간 학습**
- DuRi API와 실시간 통신
- 대화 자동 전송
- 학습 결과 실시간 피드백

### **명령어 지원**
- `DuRi: 자동 학습 시작` - 자동 학습 활성화
- `DuRi: 자동 학습 중지` - 자동 학습 비활성화
- `DuRi: 대화 전송` - 수동으로 대화 전송

## 📦 설치

### **1. 의존성 설치**
```bash
cd cursor_extension
npm install
```

### **2. 컴파일**
```bash
npm run compile
```

### **3. Cursor에서 확장 프로그램 로드**
1. Cursor에서 `Ctrl+Shift+P` (또는 `Cmd+Shift+P`)
2. "Extensions: Install from VSIX..." 선택
3. 컴파일된 `.vsix` 파일 선택

## ⚙️ 설정

### **API 서버 URL 설정**
```json
{
  "duri.apiUrl": "http://localhost:8000"
}
```

### **자동 캡처 설정**
```json
{
  "duri.autoCapture": true
}
```

## 🔧 사용법

### **자동 학습 시작**
1. `Ctrl+Shift+P` (또는 `Cmd+Shift+P`)
2. "DuRi: 자동 학습 시작" 선택
3. 자동으로 대화가 캡처되고 DuRi에게 전송됩니다

### **수동 대화 전송**
1. `Ctrl+Shift+P` (또는 `Cmd+Shift+P`)
2. "DuRi: 대화 전송" 선택
3. 전송할 메시지 입력

### **학습 중지**
1. `Ctrl+Shift+P` (또는 `Cmd+Shift+P`)
2. "DuRi: 자동 학습 중지" 선택

## 🎯 캡처되는 내용

### **사용자 입력**
- 코드 작성
- 주석 작성
- 문서 작성
- 명령어 입력

### **Cursor 응답**
- 코드 생성
- 설명 제공
- 오류 수정
- 리팩토링 제안

### **시스템 이벤트**
- 명령어 실행
- 터미널 출력
- 파일 변경

## 🔍 필터링

### **입력 필터링**
- 10자 미만 입력 제외
- 주석 제외
- 중복 입력 제외

### **응답 필터링**
- 20자 미만 응답 제외
- 에러 메시지 제외
- 중복 응답 제외

## 📊 학습 결과

DuRi는 캡처된 대화를 분석하여:
- **학습 패키지** 생성
- **요약** 제공
- **학습가치** 평가
- **메모리** 저장

## 🛠️ 개발

### **빌드**
```bash
npm run compile
```

### **개발 모드**
```bash
npm run watch
```

### **테스트**
```bash
npm test
```

## 📝 로그

확장 프로그램의 로그는 Cursor의 개발자 도구에서 확인할 수 있습니다:
1. `Ctrl+Shift+I` (또는 `Cmd+Option+I`)
2. Console 탭에서 로그 확인

## 🔗 DuRi API 연동

이 확장 프로그램은 다음 DuRi API 엔드포인트와 연동됩니다:

- `GET /health/` - 서버 상태 확인
- `POST /automated-learning/process` - 대화 전송
- `GET /memory/` - 메모리 상태 확인

## 🚨 문제 해결

### **API 서버 연결 실패**
1. DuRi API 서버가 실행 중인지 확인
2. `http://localhost:8000`에서 서버 응답 확인
3. 방화벽 설정 확인

### **캡처가 작동하지 않음**
1. 자동 캡처 설정 확인
2. 학습이 활성화되어 있는지 확인
3. 로그에서 오류 메시지 확인

## 📄 라이선스

MIT License

## 🤝 기여

이슈나 기능 요청은 GitHub에서 제출해주세요. 