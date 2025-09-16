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

## 의사결정 트리 (플로차트)

```
시작
  ↓
delta > 0? ──No──→ FAIL (개선 없음)
  ↓ Yes
p_value ≤ 0.05? ──No──→ FAIL (유의성 부족)
  ↓ Yes
ci_width ≤ τ? ──No──→ FAIL (신뢰구간 너무 넓음)
  ↓ Yes
|delta| ≥ MES? ──No──→ FAIL (효과 크기 부족)
  ↓ Yes
n_A ≥ min & n_B ≥ min? ──No──→ FAIL (샘플 부족)
  ↓ Yes
power ≥ 0.8? ──No──→ FAIL (검정력 부족)
  ↓ Yes
PASS ✅
```

### 확장 규칙 설명

- **ci_width**: 95% 신뢰구간 폭이 너무 넓으면 불확실성이 높음
- **mes (Minimum Effect Size)**: 실질적으로 의미있는 최소 효과 크기
- **n_A, n_B**: 통계적 검정력 확보를 위한 최소 샘플 크기
- **power**: 사전 계산된 검정력 (0.8 이상 권장)

### 정책 버전 관리

- **v1.0**: 기본 규칙 (delta > 0, p_value ≤ 0.05)
- **v1.1**: 확장 규칙 추가 (ci_width, mes, n_min, power)
- 각 실행마다 `run_meta.json`에 `policy_version` 기록
