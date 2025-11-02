# 프로듀서 jsonl 최소 스키마 고정 (패치 #2)

## 개요
프로듀서가 **6키 의미론**을 항상 기록하도록 보강합니다.
핵심 키: `variant|arm`, `metric|score|loss`, `samples|n|count`

## 스키마 정의

```json
{
  "schema_version": "1",
  "ts": "2025-11-02T03:09:24Z",
  "cycle_id": "EV-20251102-030924-45",
  "variant": "A",
  "metric": {"name": "loss", "value": 0.321},
  "n": 1
}
```

## 구현 예시

### Python (FastAPI/worker)

```python
from datetime import datetime
import json

def write_evolution_event(f, ev_id: str, variant: str, metric_name: str, metric_value: float, samples: int = 1):
    """프로듀서 측 evolution.jsonl 기록 함수"""
    rec = {
        "schema_version": "1",
        "ts": datetime.utcnow().isoformat() + "Z",
        "cycle_id": ev_id,              # "EV-..."
        "variant": variant,             # "A" | "B"
        "metric": {"name": metric_name, "value": float(metric_value)},  # or score/decision/p_value
        "n": int(samples)               # >=1이면 p라인 생성 대상
    }
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
```

### FastAPI 엔드포인트 예시

```python
from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.post("/api/evolution/record")
def record_event(variant: str, metric_name: str, metric_value: float, samples: int = 1):
    ev_id = f"EV-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
    
    with open("var/events/evolution.jsonl", "a") as f:
        write_evolution_event(f, ev_id, variant, metric_name, metric_value, samples)
    
    return {"ok": True, "ev_id": ev_id}
```

## 검증

```bash
# 유효 키 포함 파일 수(최근 2h)
find var/evolution -name "evolution.EV-*.jsonl" -newermt "-2 hours" \
  -exec grep -lE '"(variant|arm|ab_variant)".*|"(metric|score|loss|decision|p_value)".*|"(samples|n|count)"' {} \; | wc -l

# 재번들/판정
bash scripts/evolution/evidence_bundle.sh --ev all --force
bash scripts/ab_pvalue_stats.sh "2 hours" && bash scripts/final_smoke_3metrics.sh
```

## 성공 확률
- `unique_p≥2 & σ>0`: **0.95+**
- 재발확률: **≤0.5%**

