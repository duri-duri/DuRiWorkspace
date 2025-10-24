# Cursor 작업 환경 설정 가이드

## 현재 작업 환경 상태 (2024-09-16)

### 🎯 **프로젝트 구조**
```
DuRi_Day11_15_starter/
├── src/                    # 통합 소스 코드
│   ├── ab/                 # A/B 테스트 코어
│   ├── pou/                # PoU 시스템
│   ├── pipeline/           # 실행 파이프라인
│   ├── utils/              # 공통 유틸리티
│   └── legacy/             # 기존 코드 (점진 폐기)
├── tests/                  # 테스트 (12/12 PASSED)
├── configs/                # 설정 파일 (Day36-39)
├── policies/               # 정책 SSOT
├── scripts/                # 스크립트
├── docs/                   # 문서
└── .github/workflows/      # CI/CD
```

### 🚀 **핵심 성과**
- **A/B 테스트 인프라**: Day36~39 통합 실행
- **정책 기반 게이트**: `policies/promotion.yaml` SSOT
- **일반화된 평가 엔진**: 모든 정책 규칙 자동 평가
- **완전한 테스트**: 12/12 PASSED
- **CI/CD 매트릭스**: Python 3.10/3.11 × Day 36-39 × Variant A/B

### 🔧 **사용 가능한 명령어**
```bash
# 기본 실행
make day36  # Day36 A/B 실행
make day37  # Day37 A/B 실행
make day38  # Day38 A/B 실행
make day39  # Day39 A/B 실행

# 게이트 확인
DAY=36 make gate  # Day36 게이트 평가
DAY=37 make gate  # Day37 게이트 평가

# 테스트
make test  # 12/12 PASSED ✅
```

### 📋 **Cursor 설정 권장사항**

#### 1. **워크스페이스 설정**
- **루트 디렉토리**: `DuRi_Day11_15_starter/`
- **Python 인터프리터**: `.venv/bin/python`
- **터미널**: 현재 디렉토리에서 실행

#### 2. **확장 프로그램**
- **Python**: Microsoft Python Extension
- **Git**: GitLens
- **YAML**: YAML Language Support
- **Markdown**: Markdown All in One

#### 3. **설정 파일 (.vscode/settings.json)**
```json
{
  "python.defaultInterpreterPath": "./.venv/bin/python",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests/"],
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "outputs/**": true,
    "artifacts/**": true
  },
  "terminal.integrated.cwd": "${workspaceFolder}",
  "git.ignoreLimitWarning": true
}
```

#### 4. **작업 공간 설정 (.vscode/tasks.json)**
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Run Tests",
      "type": "shell",
      "command": "make test",
      "group": "test"
    },
    {
      "label": "Run Day36",
      "type": "shell",
      "command": "make day36",
      "group": "build"
    },
    {
      "label": "Run Day37",
      "type": "shell",
      "command": "make day37",
      "group": "build"
    }
  ]
}
```

### 🎨 **Cursor 특화 설정**

#### 1. **AI 어시스턴트 설정**
- **컨텍스트**: 현재 프로젝트 구조 이해
- **명령어**: `make` 기반 워크플로우 사용
- **테스트**: pytest 기반 테스트 실행

#### 2. **코드 생성 규칙**
- **기존 코드 최대 활용** 원칙
- **정책 기반 SSOT** 사용
- **테스트 우선** 개발

#### 3. **디버깅 설정**
- **브레이크포인트**: `src/` 디렉토리 중심
- **변수 감시**: `results`, `policy`, `gate_pass` 등
- **로그**: `outputs/` 디렉토리 확인

### 📝 **작업 흐름**

#### 1. **일반적인 개발 사이클**
```bash
# 1. 테스트 실행
make test

# 2. A/B 테스트 실행
make day36

# 3. 게이트 확인
DAY=36 make gate

# 4. 커밋
git add . && git commit -m "feat: ..."
```

#### 2. **새 기능 추가**
1. `src/` 디렉토리에 모듈 추가
2. `tests/` 디렉토리에 테스트 추가
3. `configs/` 디렉토리에 설정 추가
4. `Makefile`에 타겟 추가

#### 3. **정책 변경**
1. `policies/promotion.yaml` 수정
2. `tests/test_promotion_gate.py` 업데이트
3. `make test` 실행
4. 실제 데이터로 검증

### 🔄 **환경 재현 방법**

#### 1. **프로젝트 클론**
```bash
git clone <repository>
cd DuRi_Day11_15_starter
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 2. **Cursor 설정 적용**
1. `.vscode/settings.json` 복사
2. `.vscode/tasks.json` 복사
3. 확장 프로그램 설치
4. Python 인터프리터 설정

#### 3. **환경 검증**
```bash
make test  # 12/12 PASSED 확인
make day36  # A/B 테스트 실행
DAY=36 make gate  # 게이트 평가
```

### 🎯 **현재 상태 요약**

- **브랜치**: `feat/phase4_day35_refactor`
- **커밋**: `76da92aba` (robust promotion gate)
- **테스트**: 12/12 PASSED
- **승격 게이트**: 4개 모두 통과
- **다음 단계**: Day40 착수 준비 완료

### 💡 **추가 팁**

1. **터미널**: 항상 프로젝트 루트에서 실행
2. **Git**: `feat/` 브랜치에서 작업
3. **테스트**: 변경사항마다 `make test` 실행
4. **문서**: `docs/` 디렉토리에 기록 유지

---

**이 설정으로 현재의 생산적인 작업 환경을 재현할 수 있습니다!** 🚀
