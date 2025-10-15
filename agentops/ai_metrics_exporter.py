from flask import Flask, Response
app = Flask(__name__)

# in-memory counters (실서비스에선 Redis/DB/Prom으로 집계 권장)
METRICS = {
  "task_success_total": 0,
  "hallucinations_total": 0,
  "grounded_answers_total": 0,
  "tool_calls_total": 0,
  "cost_usd_total": 0.0,
}

@app.get("/inc/<name>")
def inc(name):
    if name in METRICS: METRICS[name] = METRICS.get(name, 0) + 1
    return {"ok": True, "metrics": METRICS}

@app.get("/metrics")
def metrics():
    lines = []
    lines += [
      "# HELP task_success_total Count of successful tasks",
      "# TYPE task_success_total counter",
      f"task_success_total {METRICS['task_success_total']}",
      "# HELP hallucinations_total Count of hallucinated answers",
      "# TYPE hallucinations_total counter",
      f"hallucinations_total {METRICS['hallucinations_total']}",
      "# HELP grounded_answers_total Count of answers with citations",
      "# TYPE grounded_answers_total counter",
      f"grounded_answers_total {METRICS['grounded_answers_total']}",
      "# HELP tool_calls_total Count of tool/function invocations",
      "# TYPE tool_calls_total counter",
      f"tool_calls_total {METRICS['tool_calls_total']}",
      "# HELP cost_usd_total Total API cost in USD",
      "# TYPE cost_usd_total counter",
      f"cost_usd_total {METRICS['cost_usd_total']}",
    ]
    return Response("\n".join(lines) + "\n", mimetype="text/plain")

@app.get("/health")
def health(): return {"status": "ok", "service": "ai_metrics_exporter"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9100)
