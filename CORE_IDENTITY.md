# CORE_IDENTITY.md

## 🧠 DuRi 시스템 설계 철학

- DuRi는 분산형 AI 시스템이며, 각 노드는 명확한 역할과 책임을 가진다.
- GUI는 기본적으로 **duri-head만 허용**하며, **나머지는 CLI-only Server 환경**으로 유지한다.
- 각 모듈은 다음과 같은 책임 구조를 따른다:
  - **duri-core**: 시스템의 심장. 통합 제어, 스냅샷/복원, 통신 브로커
  - **duri-brain**: 추론/판단 엔진. 입력 해석 및 의사결정 API
  - **duri-evolution**: 학습/적응/변화 감지. 지속적인 피드백 구조
  - **duri-control**: 예외적으로 GUI 및 개발 허용. 현장 대응 + 보조 개발 터미널
- 공통 모듈 및 중복된 로직은 `duri-core/common/`으로 통합하고, 각 노드는 이를 import하는 구조로 통일한다.

---

## 🛑 절대 잊지 말 것

- 중복 파일은 반드시 모듈화. 복붙 구조는 장기적으로 제거한다.
- `duri-core`는 전체 흐름의 **심장(heart)**.
  → 통신, 데이터 흐름, 백업 모두 이곳을 중심으로 통제되어야 한다.
- **Emotion vector**는 이 시스템의 공통 언어다.
  → 모든 모듈은 감정 벡터 기반으로 소통한다.

---

## 🔐 운영 정책

- `duri-core`, `duri-brain`, `duri-evolution`은 반드시 **CLI-only Server 환경 유지**
  - GUI, Xorg, Gnome, Snap 패키지 모두 제거
  - 설치 직후 `sudo systemctl set-default multi-user.target` 실행 필수
- `duri-head`만 VSCode, Cursor, WSL, GUI 개발 환경을 사용
- 모든 Git 관리, 병합, 배포, 전략 설계는 `duri-head`에서만 수행
- 모든 백업, 스냅샷 저장소는 `duri-core`에서 중앙 관리

---

## 🖥️ duri-control (현장 대응 + 보조 개발 노드)

- **Ubuntu Desktop 기반 GUI 허용 노드**
- 주요 목적:
  - 시스템 상태 모니터링, 현장 시연, 긴급 제어
  - 필요 시 직접 코드 수정 및 실행 가능
- **예외적으로 개발 허용됨 (duri-head 외 유일한 GUI 코딩 가능 노드)**
  - `cursor` 사용 가능
  - Git clone 후 `main → dev` 브랜치 분기하여 작업 가능
  - 테스트 및 시연 목적의 dev 기능 구현 가능
- 금지 사항:
  - 시스템 설계 구조 변경
  - 병합, 릴리스 브랜치 관리
- 개발 권한: ✅ 있음 (단, **상황 대응 목적, 보조 작업 범위**로 한정)

---

## 🧠 시스템 핵심 요약

| 노드명         | 역할                      | GUI | 개발 허용 여부 | 비고 |
|----------------|---------------------------|-----|----------------|------|
| duri-core      | 백업, 통제, 통신 허브          | ❌  | ❌              | CLI-only |
| duri-brain     | 판단/추론 API               | ❌  | ❌              | CLI-only |
| duri-evolution | 학습/변화 감지                | ❌  | ❌              | CLI-only |
| duri-head      | **주 개발 GUI 터미널**         | ✅  | ✅              | VSCode, Cursor 허용 |
| duri-control   | **보조 개발 + 현장 대응 터미널** | ✅  | ✅ (예외 허용)   | Cursor 개발 가능 |
