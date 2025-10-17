from flask import Flask, request, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from time import time
import os

app = Flask(__name__)

TASK_SUCCESS = Counter("task_success_total", "Count of successful tasks")
HALLUCINATIONS = Counter("hallucinations_total", "Count of hallucinated answers")
GROUNDED = Counter("grounded_answers_total", "Count of answers with citations")
TOOL_CALLS = Counter("tool_calls_total", "Count of tool/function invocations")
COST_USD_TOTAL = Counter("cost_usd_total", "Total API cost in USD")
COST_USD_LAST = Gauge("cost_usd_last", "Last request cost in USD")

REQ_LAT = Histogram(
    "agent_request_latency_seconds",
    "End-to-end request latency",
    buckets=[0.1,0.2,0.5,1,2,5,10]
)

TOKEN = os.getenv("EXPORTER_TOKEN","")
def _ok(req): return (not TOKEN) or req.headers.get("X-Exporter-Token")==TOKEN

# Rate limiting
BUCKET = {"ts":0, "cnt":0}
def _ratelimit(max_per_min=60):
    now=int(time()//60)
    if BUCKET["ts"]!=now: BUCKET.update(ts=now, cnt=0)
    BUCKET["cnt"]+=1
    return BUCKET["cnt"]<=max_per_min

@app.get("/inc/<name>")
def inc(name):
    if not _ok(request): return {"ok": False}, 401
    m = {
        "task_success_total": TASK_SUCCESS,
        "hallucinations_total": HALLUCINATIONS,
        "grounded_answers_total": GROUNDED,
        "tool_calls_total": TOOL_CALLS,
    }.get(name)
    if m: m.inc()
    return {"ok": True}

@app.post("/observe")
def observe():
    if not _ok(request): return {"ok": False}, 401
    if not _ratelimit(60): return {"ok": False, "err":"rate limit"}, 429
    lat = float(request.args.get("latency", "0"))
    add = float(request.args.get("cost_add", "0"))
    if lat > 0: REQ_LAT.observe(lat)
    if add != 0:
        COST_USD_TOTAL.inc(add)
        COST_USD_LAST.set(add)
    return {"ok": True}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.get("/health")
def health():
    return {"status": "ok", "service": "ai_metrics_exporter"}

if __name__ == "__main__":
    port = int(os.getenv("AI_METRICS_PORT", "19100"))
    app.run(host="127.0.0.1", port=port)
