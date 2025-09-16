#!/usr/bin/env bash
# Day36 A/B 테스트용 올바른 JSON 샘플 데이터 생성

# 의료 도메인 샘플 (A군: safety_first용)
for i in {1..15}; do
  cat > samples/logs/medical_A_${i}.jsonl <<JSONL
{"timestamp": "2025-01-16T09:$(printf "%02d" $((i-1))):00Z", "p95_latency_ms": $((1400 + RANDOM % 200)), "accuracy": 0.$(printf "%02d" $((85 + RANDOM % 15))), "explainability": 0.$(printf "%02d" $((75 + RANDOM % 20))), "status": "success", "domain": "medical"}
{"timestamp": "2025-01-16T09:$(printf "%02d" $((i-1))):30Z", "p95_latency_ms": $((1350 + RANDOM % 150)), "accuracy": 0.$(printf "%02d" $((88 + RANDOM % 12))), "explainability": 0.$(printf "%02d" $((78 + RANDOM % 17))), "status": "success", "domain": "medical"}
{"timestamp": "2025-01-16T09:$(printf "%02d" $((i-1))):45Z", "p95_latency_ms": $((1450 + RANDOM % 100)), "accuracy": 0.$(printf "%02d" $((90 + RANDOM % 10))), "explainability": 0.$(printf "%02d" $((80 + RANDOM % 15))), "status": "ok", "domain": "medical"}
JSONL
done

# 의료 도메인 샘플 (B군: balanced용)
for i in {1..15}; do
  cat > samples/logs/medical_B_${i}.jsonl <<JSONL
{"timestamp": "2025-01-16T10:$(printf "%02d" $((i-1))):00Z", "p95_latency_ms": $((1400 + RANDOM % 200)), "accuracy": 0.$(printf "%02d" $((85 + RANDOM % 15))), "explainability": 0.$(printf "%02d" $((75 + RANDOM % 20))), "status": "success", "domain": "medical"}
{"timestamp": "2025-01-16T10:$(printf "%02d" $((i-1))):30Z", "p95_latency_ms": $((1350 + RANDOM % 150)), "accuracy": 0.$(printf "%02d" $((88 + RANDOM % 12))), "explainability": 0.$(printf "%02d" $((78 + RANDOM % 17))), "status": "success", "domain": "medical"}
{"timestamp": "2025-01-16T10:$(printf "%02d" $((i-1))):45Z", "p95_latency_ms": $((1450 + RANDOM % 100)), "accuracy": 0.$(printf "%02d" $((90 + RANDOM % 10))), "explainability": 0.$(printf "%02d" $((80 + RANDOM % 15))), "status": "ok", "domain": "medical"}
JSONL
done

# 재활 도메인 샘플 (A군: safety_first용)
for i in {1..15}; do
  cat > samples/logs/rehab_A_${i}.jsonl <<JSONL
{"timestamp": "2025-01-16T11:$(printf "%02d" $((i-1))):00Z", "p95_latency_ms": $((1300 + RANDOM % 150)), "accuracy": 0.$(printf "%02d" $((88 + RANDOM % 12))), "explainability": 0.$(printf "%02d" $((76 + RANDOM % 19))), "status": "success", "domain": "rehab"}
{"timestamp": "2025-01-16T11:$(printf "%02d" $((i-1))):30Z", "p95_latency_ms": $((1250 + RANDOM % 100)), "accuracy": 0.$(printf "%02d" $((91 + RANDOM % 9))), "explainability": 0.$(printf "%02d" $((79 + RANDOM % 16))), "status": "success", "domain": "rehab"}
{"timestamp": "2025-01-16T11:$(printf "%02d" $((i-1))):45Z", "p95_latency_ms": $((1350 + RANDOM % 80)), "accuracy": 0.$(printf "%02d" $((89 + RANDOM % 11))), "explainability": 0.$(printf "%02d" $((81 + RANDOM % 14))), "status": "ok", "domain": "rehab"}
JSONL
done

# 재활 도메인 샘플 (B군: balanced용)
for i in {1..15}; do
  cat > samples/logs/rehab_B_${i}.jsonl <<JSONL
{"timestamp": "2025-01-16T12:$(printf "%02d" $((i-1))):00Z", "p95_latency_ms": $((1300 + RANDOM % 150)), "accuracy": 0.$(printf "%02d" $((88 + RANDOM % 12))), "explainability": 0.$(printf "%02d" $((76 + RANDOM % 19))), "status": "success", "domain": "rehab"}
{"timestamp": "2025-01-16T12:$(printf "%02d" $((i-1))):30Z", "p95_latency_ms": $((1250 + RANDOM % 100)), "accuracy": 0.$(printf "%02d" $((91 + RANDOM % 9))), "explainability": 0.$(printf "%02d" $((79 + RANDOM % 16))), "status": "success", "domain": "rehab"}
{"timestamp": "2025-01-16T12:$(printf "%02d" $((i-1))):45Z", "p95_latency_ms": $((1350 + RANDOM % 80)), "accuracy": 0.$(printf "%02d" $((89 + RANDOM % 11))), "explainability": 0.$(printf "%02d" $((81 + RANDOM % 14))), "status": "ok", "domain": "rehab"}
JSONL
done

# 코딩 도메인 샘플 (A군: safety_first용)
for i in {1..15}; do
  cat > samples/logs/coding_A_${i}.jsonl <<JSONL
{"timestamp": "2025-01-16T13:$(printf "%02d" $((i-1))):00Z", "p95_latency_ms": $((1450 + RANDOM % 200)), "accuracy": 0.$(printf "%02d" $((90 + RANDOM % 10))), "explainability": 0.$(printf "%02d" $((78 + RANDOM % 17))), "status": "success", "domain": "coding"}
{"timestamp": "2025-01-16T13:$(printf "%02d" $((i-1))):30Z", "p95_latency_ms": $((1500 + RANDOM % 150)), "accuracy": 0.$(printf "%02d" $((92 + RANDOM % 8))), "explainability": 0.$(printf "%02d" $((80 + RANDOM % 15))), "status": "success", "domain": "coding"}
{"timestamp": "2025-01-16T13:$(printf "%02d" $((i-1))):45Z", "p95_latency_ms": $((1480 + RANDOM % 120)), "accuracy": 0.$(printf "%02d" $((91 + RANDOM % 9))), "explainability": 0.$(printf "%02d" $((82 + RANDOM % 13))), "status": "ok", "domain": "coding"}
JSONL
done

# 코딩 도메인 샘플 (B군: quality용)
for i in {1..15}; do
  cat > samples/logs/coding_B_${i}.jsonl <<JSONL
{"timestamp": "2025-01-16T14:$(printf "%02d" $((i-1))):00Z", "p95_latency_ms": $((1450 + RANDOM % 200)), "accuracy": 0.$(printf "%02d" $((90 + RANDOM % 10))), "explainability": 0.$(printf "%02d" $((78 + RANDOM % 17))), "status": "success", "domain": "coding"}
{"timestamp": "2025-01-16T14:$(printf "%02d" $((i-1))):30Z", "p95_latency_ms": $((1500 + RANDOM % 150)), "accuracy": 0.$(printf "%02d" $((92 + RANDOM % 8))), "explainability": 0.$(printf "%02d" $((80 + RANDOM % 15))), "status": "success", "domain": "coding"}
{"timestamp": "2025-01-16T14:$(printf "%02d" $((i-1))):45Z", "p95_latency_ms": $((1480 + RANDOM % 120)), "accuracy": 0.$(printf "%02d" $((91 + RANDOM % 9))), "explainability": 0.$(printf "%02d" $((82 + RANDOM % 13))), "status": "ok", "domain": "coding"}
JSONL
done

echo "Day36 A/B 테스트용 올바른 JSON 샘플 데이터 생성 완료 (n=15/군)"
