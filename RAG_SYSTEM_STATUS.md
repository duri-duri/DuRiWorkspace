# RAG 시스템 운영 가이드

## 현재 상태 ✅

- **RAG 검증**: 경고 0개 달성
- **검색 도구**: 정상 동작 (다중 필터 지원)
- **pre-push 훅**: 태그 푸시 무음 통과, 브랜치 푸시 정상 처리
- **유령 에러**: `origin/origin/...` 패턴 완전 박멸

## 훅 동작 원칙

- **태그 푸시**: 무조건 통과 (exit 0)
- **브랜치 푸시**: 업스트림 존재할 때만 freeze-guard 조건부 실행
- **업스트림 해석**: `@{u}` 우선, 없으면 `origin/$(current-branch)` 추정

## 멀티라인 JSON 재발 방지

- `.gitattributes`에서 `*.jsonl -text`로 고정
- JSONL 형식: 1줄=1레코드 강제 보장
- CI에 단일행 검사 포함

## RAG 품질 검증 명령어

### ID 중복 확인
```bash
find rag -name '*.jsonl' -exec jq -r '.id' {} + \
| sort | uniq -d | sed -n '1p' || echo "OK: duplicated id none"
```

### 허용 카테고리만 사용
```bash
ALLOWED='^(intake|education|exercise|orders|schedule|policy|diagnosis)$'
find rag -name '*.jsonl' -exec jq -r '.id + "\t" + .category' {} + \
| awk -F'\t' -v A="$ALLOWED" 'BEGIN{ok=1} !($2 ~ A){print "WARN unknown category:",$0; ok=0} END{if(ok)print "OK: categories clean"}'
```

### 배열 타입 검증
```bash
# bullets 배열 검증
find rag -name '*.jsonl' -exec jq -e '
  select(has("bullets")) | .bullets | type=="array" and all(.[]; type=="string")
' {} + >/dev/null && echo "OK: bullets array<string>"

# tags 배열 검증
find rag -name '*.jsonl' -exec jq -e '
  select(has("tags")) | .tags | type=="array" and all(.[]; type=="string")
' {} + >/dev/null && echo "OK: tags array<string>"
```

### 필수 키 누락 확인
```bash
find rag -name '*.jsonl' -exec jq -r '
  select( (has("id")|not) or (has("title")|not) or (has("category")|not) or (has("body")|not) )
  | "MISSING\t\(.id//"-")\t\(.title//"-")"
' {} + | sed -n '1p' || echo "OK: required fields present"
```

## 일반 사용 명령어

### 검색
```bash
bash scripts/rag_search.sh "<검색어>" [카테고리] [환자용:true|false]
```

### 자동 보강 (짧은 본문 확장)
```bash
bash scripts/rag_autofill.sh
```

### 전체 검증
```bash
bash scripts/rag_verify.sh
```

### 훅 복구 (필요시)
```bash
bash scripts/fix_pre_push.sh
```

## 운영 팁

- **검색 프리뷰**: 160자로 확장하여 임상문서 잘림 최소화
- **카테고리별 권장 길이**: orders/policy(120자), schedule(140자), exercise(180자), intake/diagnosis(200자), education(220자)
- **자동화**: 모든 변경사항은 pre-commit → CI → 검증으로 자동 연동
- **재발 방지**: 훅 복구 스크립트까지 최신 템플릿으로 동기화 완료

## 상태 확인 (명령어 수정 금지)

### 최종 스모크 테스트
```bash
# 태그 푸시 시뮬레이션 (무음이어야 정상)
printf "0000000 0000000 refs/tags/smoke 0000000\n" | .git/hooks/pre-push origin dummy-url

# 브랜치 푸시 스킵 경로 확인 (업데이트 없음 → 무음)
printf "" | .git/hooks/pre-push origin dummy-url
```

### 훅 리그레션 방지 체크리스트
- [ ] `scripts/fix_pre_push.sh`가 단일 소스로 유지됨
- [ ] 실행 비트 보장됨 (`chmod +x`)
- [ ] macOS 멀티머신 엔티몰 시 `bash 3.x` 호환성 고려

## 현재 결과 (자동 생성됨)

```
✅ 훅 스모크 테스트 완벽 통과
✅ ID 중복 없음
✅ 전체 카테고리 허용 규칙 준수
✅ bullets 배열<string> 타입 정상
✅ tags 배열<string> 타입 정상
✅ 필수 키 누락 없음
```

**RAG 시스템 운영 준비 완료** 🎉
