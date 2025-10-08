# 🔧 디버그 토글 가이드

## RAG 시스템 디버그 옵션

### DEBUG_RAG=1
상세 트레이스 & stderr 표시
```bash
DEBUG_RAG=1 bash scripts/rag_search_fusion_v1.sh "요통"
```

### RAG_QUIET=1
게이트/CI에서 불필요한 경고 억제
```bash
RAG_QUIET=1 bash scripts/rag_search_fusion_v1.sh "요통"
```

## 사용 시나리오

- **개발/디버깅**: `DEBUG_RAG=1`로 상세 로그 확인
- **CI/게이트**: `RAG_QUIET=1`로 깔끔한 출력
- **일반 사용**: 기본값으로 정상 동작

## 게이트 기본 모드

### 기본 모드 (게이트/CI)
```bash
RAG_QUIET=1 bash scripts/rag_search_fusion_v1.sh "요통"
```
- 불필요한 경고 억제
- 깔끔한 출력으로 게이트 통과율 향상

### 디버그 모드 (개발/원인 분석)
```bash
DEBUG_RAG=1 bash scripts/rag_search_fusion_v1.sh "요통"
```
- 상세 트레이스 & stderr 표시
- 문제 원인 분석에 유용

### 일반 실행 (둘 다 비움)
```bash
bash scripts/rag_search_fusion_v1.sh "요통"
```
- 기본 동작으로 정상 실행

## 환경변수 일람

| 변수명 | 기본값 | 설명 | 사용 예시 |
|--------|--------|------|-----------|
| `K` | 3 | 검색 결과 개수 | `K=5 bash scripts/rag_search_fusion_v1.sh "요통"` |
| `PRE_K` | 30 | RRF 전 후보 개수 | `PRE_K=20 bash scripts/rag_search_fusion.sh "요통"` |
| `RRF_K` | 18 | RRF 가중치 분모 | `RRF_K=10 bash scripts/rag_search_fusion.sh "요통"` |
| `WEIGHTS` | tuned=1.0,enhanced=0.7 | RRF 가중치 | `WEIGHTS="tuned=1.0,enhanced=0.8"` |
| `SYNONYMS_TSV` | .reports/day64/synonyms.tsv | 동의어 파일 경로 | `SYNONYMS_TSV="custom.tsv"` |
| `RAG_QUIET` | - | 경고 억제 모드 | `RAG_QUIET=1 bash scripts/rag_search_fusion_v1.sh` |
| `DEBUG_RAG` | - | 상세 디버그 모드 | `DEBUG_RAG=1 bash scripts/rag_search_fusion_v1.sh` |
| `LOG_PATH` | - | 로그 파일 경로 | `LOG_PATH="custom.log"` |
| `THRESH_P` | 0.30 | 게이트 임계값 | `THRESH_P=0.45 bash scripts/rag_gate_day62.sh` |
| `SEARCH` | scripts/rag_search_enhanced.sh | 검색 스크립트 | `SEARCH="scripts/rag_search_fusion_v1.sh"` |

### 새 동료 온보딩 가이드

1. **기본 사용**: 환경변수 없이 실행
2. **성능 튜닝**: `K`, `PRE_K`, `RRF_K`, `WEIGHTS` 조정
3. **디버깅**: `DEBUG_RAG=1`로 상세 로그 확인
4. **CI/게이트**: `RAG_QUIET=1`로 깔끔한 출력

## 선택적 의존성 힌트

### 필수 도구
- `bash`, `awk`, `sed`, `grep`, `sort`, `head`, `mktemp` (기본 설치)

### 선택 설치 추천
- `shellcheck`: 스크립트 품질 검사 (`apt install shellcheck`)
- `jq`: JSON 처리 (`apt install jq`)
- `bc`: 수치 계산 (`apt install bc`)

### 설치 확인
```bash
# 필수 도구 확인
bash scripts/check_deps.sh

# 선택 도구 확인
command -v shellcheck && echo "✅ shellcheck 설치됨"
command -v jq && echo "✅ jq 설치됨"
command -v bc && echo "✅ bc 설치됨"
```

### 온보딩 체크리스트
1. **기본 환경**: `make help`로 사용 가능한 명령어 확인
2. **의존성 확인**: `bash scripts/check_deps.sh` 실행
3. **스모크 테스트**: `make smoke`로 기본 기능 확인
4. **PR 게이트**: `make gate`로 전체 시스템 검증
5. **디버깅**: `DEBUG_RAG=1`로 상세 로그 확인
