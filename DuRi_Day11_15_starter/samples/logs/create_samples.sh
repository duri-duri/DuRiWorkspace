# Day36 PoU 지표 수집 자동화 시스템 샘플 로그

# 의료 도메인 샘플 (JSONL)
cat > samples/logs/medical_sample.jsonl <<'JSONL'
{"timestamp": "2025-01-16T09:00:00Z", "p95_latency_ms": 1420, "accuracy": 0.92, "explainability": 0.81, "status": "success", "domain": "medical"}
{"timestamp": "2025-01-16T09:01:00Z", "p95_latency_ms": 1380, "accuracy": 0.90, "explainability": 0.79, "status": "success", "domain": "medical"}
{"timestamp": "2025-01-16T09:02:00Z", "p95_latency_ms": 1510, "accuracy": 0.88, "explainability": 0.80, "status": "ok", "domain": "medical"}
{"timestamp": "2025-01-16T09:03:00Z", "p95_latency_ms": 1450, "accuracy": 0.91, "explainability": 0.82, "status": "success", "domain": "medical"}
{"timestamp": "2025-01-16T09:04:00Z", "p95_latency_ms": 1390, "accuracy": 0.89, "explainability": 0.78, "status": "success", "domain": "medical"}
JSONL

# 재활 도메인 샘플 (CSV)
cat > samples/logs/rehab_sample.csv <<'CSV'
timestamp,latency_ms,acc,exp_score,success,domain
2025-01-16T09:00:00Z,1350,0.91,0.78,success,rehab
2025-01-16T09:01:00Z,1320,0.92,0.80,success,rehab
2025-01-16T09:02:00Z,1400,0.90,0.77,ok,rehab
2025-01-16T09:03:00Z,1370,0.93,0.81,success,rehab
2025-01-16T09:04:00Z,1330,0.89,0.79,success,rehab
CSV

# 코딩 도메인 샘플 (TXT 키=값)
cat > samples/logs/coding_sample.txt <<'TXT'
timestamp=2025-01-16T09:00:00Z latency=1480 accuracy=92 rubric=81 status=success domain=coding
timestamp=2025-01-16T09:01:00Z latency=1520 accuracy=90 rubric=80 status=success domain=coding
timestamp=2025-01-16T09:02:00Z latency=1490 accuracy=93 rubric=82 status=ok domain=coding
timestamp=2025-01-16T09:03:00Z latency=1510 accuracy=91 rubric=79 status=success domain=coding
timestamp=2025-01-16T09:04:00Z latency=1470 accuracy=94 rubric=83 status=success domain=coding
TXT

# 통합 샘플 (JSON)
cat > samples/logs/integrated_sample.json <<'JSON'
[
  {"timestamp": "2025-01-16T09:00:00Z", "latency_ms": 1400, "accuracy": 0.91, "explainability": 0.80, "failure_rate": 0.001, "domain": "medical"},
  {"timestamp": "2025-01-16T09:01:00Z", "latency_ms": 1350, "accuracy": 0.92, "explainability": 0.81, "failure_rate": 0.000, "domain": "rehab"},
  {"timestamp": "2025-01-16T09:02:00Z", "latency_ms": 1500, "accuracy": 0.90, "explainability": 0.79, "failure_rate": 0.002, "domain": "coding"},
  {"timestamp": "2025-01-16T09:03:00Z", "latency_ms": 1380, "accuracy": 0.93, "explainability": 0.82, "failure_rate": 0.000, "domain": "medical"},
  {"timestamp": "2025-01-16T09:04:00Z", "latency_ms": 1420, "accuracy": 0.89, "explainability": 0.78, "failure_rate": 0.001, "domain": "rehab"}
]
JSON
