#!/usr/bin/env bash
set -euo pipefail

mkdir -p agentops scripts .github/workflows alerting

# 1) AI 지표 Exporter (Flask + /metrics)
cat > agentops/ai_metrics_exporter.py <<'PY'
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
PY

# 2) 간단 평가 러너 (시나리오 N개 → 결과/지표 JSON)
cat > scripts/run_agent_evals.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail
OUT="eval_report.json"

# 실제론 LangGraph/LlamaIndex/Playwright 등으로 시나리오 실행
# 여기서는 구조만: 성공 18/20, 환각 0.02, 근거 0.96, 평균 툴콜 1.3, cost $0.04
cat > "$OUT" <<JSON
{
  "timestamp": "$(date -u +%FT%TZ)",
  "scenarios_total": 20,
  "success_rate": 0.90,
  "hallucination_rate": 0.02,
  "grounded_ratio": 0.96,
  "avg_tool_calls": 1.3,
  "cost_per_task_usd": 0.04
}
JSON

echo "Wrote $OUT"
SH
chmod +x scripts/run_agent_evals.sh

# 3) Nightly Eval 워크플로
cat > .github/workflows/agentops_eval.yml <<'YML'
name: AgentOps Nightly Eval
on:
  schedule:
    - cron: "15 18 * * *"   # 매일 03:15 KST
  workflow_dispatch: {}
jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.10" }
      - name: Install deps
        run: pip install flask
      - name: Run eval suite
        run: bash scripts/run_agent_evals.sh
      - name: Sanity & budget guard
        run: |
          test -s eval_report.json
          jq -e '.success_rate >= 0.85 and .hallucination_rate <= 0.03' eval_report.json
      - name: Upload eval report
        uses: actions/upload-artifact@v4
        with:
          name: eval_report
          path: eval_report.json
YML

# 4) Prometheus 룰(알람 2종: 성공률/환각률)
cat > alerting/ai_rules.yml <<'YML'
groups:
- name: ai-quality
  rules:
  - alert: AgentTaskSuccessLow
    expr: (task_success_total) / max(task_success_total + hallucinations_total, 1) < 0.85
    for: 10m
    labels: { severity: page }
    annotations:
      summary: "Agent task success rate below 85%"

  - alert: AgentHallucinationHigh
    expr: (hallucinations_total) / max(task_success_total + hallucinations_total, 1) > 0.03
    for: 10m
    labels: { severity: page }
    annotations:
      summary: "Agent hallucination rate above 3%"
YML

echo "✅ agentops files created."
