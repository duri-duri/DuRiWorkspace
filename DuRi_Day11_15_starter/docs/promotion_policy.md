# Promotion Gate Policy

## 승격 기준

이 정책은 A/B 테스트 결과의 승격(promotion) 여부를 결정하는 규칙을 정의합니다.

### 기본 규칙

- **delta**: `> 0` - 개선이 있어야 함 (양수)
- **p_value**: `<= 0.05` - 통계적 유의성 통과 (5% 유의수준)

### 경계값 처리

- `p_value = 0.05`는 **PASS**로 처리 (경계 포함)
- `delta = 0`은 **FAIL**로 처리 (개선 없음)

### 선택적 게이트 (필요시 주석 해제)

- **mes**: 최소 실질 효과 크기
- **ci_width**: 95% 신뢰구간 폭 상한
- **n_A, n_B**: 최소 샘플 크기

### 사용법

```bash
# CLI 사용
python scripts/promotion_gate.py results.json policies/promotion.yaml

# Python 모듈 사용
from scripts.promotion_gate import evaluate, load_policy
policy = load_policy(Path("policies/promotion.yaml"))
ok, reasons = evaluate(results, policy)
```

### 실패 사유

게이트 실패 시 `gate_reasons`에 구체적인 실패 원인이 기록됩니다:
- `delta fail: -0.075127 !gt 0` - 개선이 없음
- `p_value fail: 0.06 !le 0.05` - 유의성 부족
