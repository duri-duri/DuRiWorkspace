# Insight Engine (β) — Spec (v0.1)

## 목적
입력(prompt)과 후보 응답(candidates)에 대해 **신규성/응집성/간결성**을 정량화하고, 가중합 점수로 상위안을 고르는 미니 엔진.
외부 의존성 없이 표준 라이브러리로 동작.

## 지표
- **Novelty**: 고유 토큰 비율(유형/전체), n-gram 반복 패널티 포함
- **Coherence**: 문장 간 연결(접속사·대명사 anchor 비율) + 급격한 주제 전환(키워드 Jaccard drop) 패널티
- **Brevity**: 길이 prior(적정 길이 µ=120±σ=60 토큰에 가우시안 prior)
- **Composite**: `S = w_n*Novelty + w_c*Coherence + w_b*Brevity`, 기본 가중치 (0.45, 0.4, 0.15)

## API
- `score_candidate(prompt, text) -> dict`  // 각 서브스코어와 S 반환
- `rank(prompt, candidates, weights=None, k=1) -> list[(idx, score, breakdown)]`
- CLI: `python -m insight.cli --prompt p --c file_or_text --topk 3`

## 테스트 기준
- 단위테스트 5개 이상 (스코어 범위, 길이 민감도, 반복 패널티, 순위 안정성, 빈 후보 예외)

## 사용 예
```bash
./scripts/run_insight.sh --prompt "invent a new rehab drill" \
  --c "text A" --c "text B" --c-file samples/ideas.txt --topk 2
```

## 확장 포인트
- 한국어 형태소 tokenizer 연결(선택)
- 도메인 키워드 prior(의료·재활)
