#!/usr/bin/env bash
# Day36 A/B 테스트용 샘플 데이터 생성 (n=15/군)

# 의료 도메인 샘플 (A군: safety_first용)
for i in {1..15}; do
  cat > samples/logs/medical_A_${i}.jsonl <<JSONL
{"timestamp": "2025-01-16T09:$(printf "%02d" $((i-1))):00Z", "p95_latency_ms": $((1400 + RANDOM % 200)), "accuracy": $(echo "scale=2; 0.85 + RANDOM % 15 / 100" | bc), "explainability": $(echo "scale=2; 0.75 + RANDOM % 20 / 100" | bc), "status": "success", "domain": "medical"}
{"timestamp": "2025-01-16T09:$(printf "%02d" $((i-1))):30Z", "p95_latency_ms": $((1350 + RANDOM % 150)), "accuracy": $(echo "scale=2; 0.88 + RANDOM % 12 / 100" | bc), "explainability": $(echo "scale=2; 0.78 + RANDOM % 17 / 100" | bc), "status": "success", "domain": "medical"}
{"timestamp": "2025-01-16T09:$(printf "%02d" $((i-1))):45Z", "p95_latency_ms": $((1450 + RANDOM % 100)), "accuracy": $(echo "scale=2; 0.90 + RANDOM % 10 / 100" | bc), "explainability": $(echo "scale=2; 0.80 + RANDOM % 15 / 100" | bc), "status": "ok", "domain": "medical"}
JSONL
done

# 의료 도메인 샘플 (B군: balanced용)
for i in {1..15}; do
  cat > samples/logs/medical_B_${i}.jsonl <<JSONL
{"timestamp": "2025-01-16T10:$(printf "%02d" $((i-1))):00Z", "p95_latency_ms": $((1400 + RANDOM % 200)), "accuracy": $(echo "scale=2; 0.85 + RANDOM % 15 / 100" | bc), "explainability": $(echo "scale=2; 0.75 + RANDOM % 20 / 100" | bc), "status": "success", "domain": "medical"}
{"timestamp": "2025-01-16T10:$(printf "%02d" $((i-1))):30Z", "p95_latency_ms": $((1350 + RANDOM % 150)), "accuracy": $(echo "scale=2; 0.88 + RANDOM % 12 / 100" | bc), "explainability": $(echo "scale=2; 0.78 + RANDOM % 17 / 100" | bc), "status": "success", "domain": "medical"}
{"timestamp": "2025-01-16T10:$(printf "%02d" $((i-1))):45Z", "p95_latency_ms": $((1450 + RANDOM % 100)), "accuracy": $(echo "scale=2; 0.90 + RANDOM % 10 / 100" | bc), "explainability": $(echo "scale=2; 0.80 + RANDOM % 15 / 100" | bc), "status": "ok", "domain": "medical"}
JSONL
done

# 재활 도메인 샘플 (A군: safety_first용)
for i in {1..15}; do
  cat > samples/logs/rehab_A_${i}.jsonl <<JSONL
{"timestamp": "2025-01-16T11:$(printf "%02d" $((i-1))):00Z", "p95_latency_ms": $((1300 + RANDOM % 150)), "accuracy": $(echo "scale=2; 0.88 + RANDOM % 12 / 100" | bc), "explainability": $(echo "scale=2; 0.76 + RANDOM % 19 / 100" | bc), "status": "success", "domain": "rehab"}
{"timestamp": "2025-01-16T11:$(printf "%02d" $((i-1))):30Z", "p95_latency_ms": $((1250 + RANDOM % 100)), "accuracy": $(echo "scale=2; 0.91 + RANDOM % 9 / 100" | bc), "explainability": $(echo "scale=2; 0.79 + RANDOM % 16 / 100" | bc), "status": "success", "domain": "rehab"}
{"timestamp": "2025-01-16T11:$(printf "%02d" $((i-1))):45Z", "p95_latency_ms": $((1350 + RANDOM % 80)), "accuracy": $(echo "scale=2; 0.89 + RANDOM % 11 / 100" | bc), "explainability": $(echo "scale=2; 0.81 + RANDOM % 14 / 100" | bc), "status": "ok", "domain": "rehab"}
JSONL
done

# 재활 도메인 샘플 (B군: balanced용)
for i in {1..15}; do
  cat > samples/logs/rehab_B_${i}.jsonl <<JSONL
{"timestamp": "2025-01-16T12:$(printf "%02d" $((i-1))):00Z", "p95_latency_ms": $((1300 + RANDOM % 150)), "accuracy": $(echo "scale=2; 0.88 + RANDOM % 12 / 100" | bc), "explainability": $(echo "scale=2; 0.76 + RANDOM % 19 / 100" | bc), "status": "success", "domain": "rehab"}
{"timestamp": "2025-01-16T12:$(printf "%02d" $((i-1))):30Z", "p95_latency_ms": $((1250 + RANDOM % 100)), "accuracy": $(echo "scale=2; 0.91 + RANDOM % 9 / 100" | bc), "explainability": $(echo "scale=2; 0.79 + RANDOM % 16 / 100" | bc), "status": "success", "domain": "rehab"}
{"timestamp": "2025-01-16T12:$(printf "%02d" $((i-1))):45Z", "p95_latency_ms": $((1350 + RANDOM % 80)), "accuracy": $(echo "scale=2; 0.89 + RANDOM % 11 / 100" | bc), "explainability": $(echo "scale=2; 0.81 + RANDOM % 14 / 100" | bc), "status": "ok", "domain": "rehab"}
JSONL
done

# 코딩 도메인 샘플 (A군: safety_first용)
for i in {1..15}; do
  cat > samples/logs/coding_A_${i}.jsonl <<JSONL
{"timestamp": "2025-01-16T13:$(printf "%02d" $((i-1))):00Z", "p95_latency_ms": $((1450 + RANDOM % 200)), "accuracy": $(echo "scale=2; 0.90 + RANDOM % 10 / 100" | bc), "explainability": $(echo "scale=2; 0.78 + RANDOM % 17 / 100" | bc), "status": "success", "domain": "coding"}
{"timestamp": "2025-01-16T13:$(printf "%02d" $((i-1))):30Z", "p95_latency_ms": $((1500 + RANDOM % 150)), "accuracy": $(echo "scale=2; 0.92 + RANDOM % 8 / 100" | bc), "explainability": $(echo "scale=2; 0.80 + RANDOM % 15 / 100" | bc), "status": "success", "domain": "coding"}
{"timestamp": "2025-01-16T13:$(printf "%02d" $((i-1))):45Z", "p95_latency_ms": $((1480 + RANDOM % 120)), "accuracy": $(echo "scale=2; 0.91 + RANDOM % 9 / 100" | bc), "explainability": $(echo "scale=2; 0.82 + RANDOM % 13 / 100" | bc), "status": "ok", "domain": "coding"}
JSONL
done

# 코딩 도메인 샘플 (B군: quality용)
for i in {1..15}; do
  cat > samples/logs/coding_B_${i}.jsonl <<JSONL
{"timestamp": "2025-01-16T14:$(printf "%02d" $((i-1))):00Z", "p95_latency_ms": $((1450 + RANDOM % 200)), "accuracy": $(echo "scale=2; 0.90 + RANDOM % 10 / 100" | bc), "explainability": $(echo "scale=2; 0.78 + RANDOM % 17 / 100" | bc), "status": "success", "domain": "coding"}
{"timestamp": "2025-01-16T14:$(printf "%02d" $((i-1))):30Z", "p95_latency_ms": $((1500 + RANDOM % 150)), "accuracy": $(echo "scale=2; 0.92 + RANDOM % 8 / 100" | bc), "explainability": $(echo "scale=2; 0.80 + RANDOM % 15 / 100" | bc), "status": "success", "domain": "coding"}
{"timestamp": "2025-01-16T14:$(printf "%02d" $((i-1))):45Z", "p95_latency_ms": $((1480 + RANDOM % 120)), "accuracy": $(echo "scale=2; 0.91 + RANDOM % 9 / 100" | bc), "explainability": $(echo "scale=2; 0.82 + RANDOM % 13 / 100" | bc), "status": "ok", "domain": "coding"}
JSONL
done

echo "Day36 A/B 테스트용 샘플 데이터 생성 완료 (n=15/군)"
