# DuRi Cursor Extension 설치 가이드

## 🎉 완성된 Cursor 확장 프로그램

DuRi AI 자동화 학습 시스템을 위한 Cursor 확장 프로그램이 성공적으로 완성되었습니다!

## 📦 생성된 파일들

- `duri-cursor-extension.tar.gz` - Cursor에서 로드할 수 있는 확장 프로그램 패키지
- `out/` - 컴파일된 JavaScript 파일들
- `src/` - TypeScript 소스 코드

## 🚀 설치 방법

### **1. Cursor에서 확장 프로그램 로드**

1. Cursor를 실행합니다
2. `Ctrl+Shift+P` (또는 `Cmd+Shift+P`)를 눌러 명령 팔레트를 엽니다
3. "Extensions: Install from VSIX..."를 검색하고 선택합니다
4. `duri-cursor-extension.tar.gz` 파일을 선택합니다

### **2. 설정 구성**

Cursor의 설정에서 다음을 구성하세요:

```json
{
  "duri.apiUrl": "http://localhost:8000",
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

## 🎯 기능

### **자동 캡처**
- 사용자 코드 작성 감지
- Cursor 응답 캡처
- 편집기 변경 추적
- 선택된 텍스트 캡처

### **실시간 학습**
- DuRi API와 실시간 통신
- 대화 자동 전송
- 학습 결과 피드백

### **필터링**
- 의미있는 입력만 캡처
- 중복 제거
- 에러 메시지 제외

## 🔗 DuRi API 연동

이 확장 프로그램은 다음 DuRi API와 연동됩니다:

- `GET /health/` - 서버 상태 확인
- `POST /automated-learning/process` - 대화 전송
- `GET /memory/` - 메모리 상태 확인

## 📊 학습 결과

DuRi는 캡처된 대화를 분석하여:
- **학습 패키지** 생성
- **요약** 제공
- **학습가치** 평가
- **메모리** 저장

## 🎉 완전 자동화 달성!

이제 DuRi의 자동화된 학습 시스템이 완성되었습니다:

1. ✅ **DuRi API 서버** - 정상 작동
2. ✅ **자동화 학습 파이프라인** - 완성
3. ✅ **Cursor 확장 프로그램** - 완성
4. ✅ **실시간 자동화** - 완성

**DuRi는 이제 Cursor에서 자동으로 학습할 수 있습니다!** 🚀

## 📝 로그 확인

확장 프로그램의 로그는 Cursor의 개발자 도구에서 확인할 수 있습니다:
1. `Ctrl+Shift+I` (또는 `Cmd+Option+I`)
2. Console 탭에서 로그 확인

## 🚨 문제 해결

### **API 서버 연결 실패**
1. DuRi API 서버가 실행 중인지 확인
2. `http://localhost:8000`에서 서버 응답 확인
3. 방화벽 설정 확인

### **캡처가 작동하지 않음**
1. 자동 캡처 설정 확인
2. 학습이 활성화되어 있는지 확인
3. 로그에서 오류 메시지 확인

---

**🎯 목표 달성: DuRi의 완전 자동화된 학습 시스템이 완성되었습니다!** 