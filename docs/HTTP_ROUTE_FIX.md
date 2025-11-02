# HTTP 404 라우트 배선 (패치 #3, 옵션)

## 개요
`generate_min_samples.sh`가 사용하는 엔드포인트를 배선합니다.
파일 주입(QF)이 이미 있으므로, 이는 여유 있을 때 구현하는 옵션입니다.

## FastAPI 구현 예시

```python
from fastapi import FastAPI
from datetime import datetime
import json

app = FastAPI()

@app.post("/api/evolution/probe")
def probe(variant: str, value: float):
    """샘플 프로브 엔드포인트"""
    # EV ID는 서버가 생성하거나, 요청이 제공한 cycle_id를 사용
    ev_id = f"EV-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
    
    rec = {
        "schema_version": "1",
        "ts": datetime.utcnow().isoformat() + "Z",
        "cycle_id": ev_id,
        "variant": variant,  # "A" | "B"
        "metric": {"name": "loss", "value": float(value)},
        "n": 1
    }
    
    # jsonl append
    with open("var/events/evolution.jsonl", "a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    
    return {"ok": True, "ev_id": ev_id}
```

## 연결 확인

```bash
curl -s -X POST localhost:8081/api/evolution/probe \
  -H "Content-Type: application/json" \
  -d '{"variant":"A","value":0.31}' | jq .
```

## 주의사항
- 파일 주입 경로(QF)가 이미 작동하므로 우선순위 낮음
- 프로듀서 스키마 고정(패치 #2)이 더 중요

