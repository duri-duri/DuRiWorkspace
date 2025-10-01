# Day35 Pack — Multi-Objective (J) Setup

## Files
- `configs/objective_params.yaml` — 목적함수, 변환, 가중치 프리셋, 하드 제약
- `tools/evaluate_objective.py` — (metrics JSON) → (J, utilities) 계산
- `tools/pareto.py` — 여러 후보의 유틸리티 공간에서 파레토 프론티어 산출
- `tools/ab_test_runner.py` — (Day36 용) A/B J 비교 Welch t-test 스캐폴드
- `example_metrics.json` — 샘플 메트릭

## Quick Start
```bash
# 1) 예제 계산
python tools/evaluate_objective.py --metrics example_metrics.json --config configs/objective_params.yaml --weight_preset balanced

# 2) 모드별 비교
for m in balanced speed quality safety_first; do
  python tools/evaluate_objective.py --metrics example_metrics.json --config configs/objective_params.yaml --weight_preset $m > out_$m.json
done

# 3) 파레토 프론티어
python tools/pareto.py --inputs out_*.json
```

## Metrics Schema (JSON)
```json
{
  "latency_ms": 1350,
  "accuracy": 0.91,          // or 91 (auto-normalized)
  "explainability": 0.78,     // or 78 (auto-normalized)
  "failure_rate": 0.012
}
```

## Calibration
- Day31~34 로그의 p95 지연/정확/설명/실패율 분포에서 **target/k** 및 **min/max**를 재추정하세요.
- 하드 제약(`acceptance_criteria`)는 실패 방지용 **컷오프**입니다. 위반 시 `constraints_ok=false`로 표시됩니다.

## Next (Day36)
- 동일 조건에서 A/B(가중치 프리셋 또는 시스템 파라미터)로 여러 샘플을 수집 → `evaluate_objective.py`로 J 산출 → `ab_test_runner.py`로 차이 검정.
```
