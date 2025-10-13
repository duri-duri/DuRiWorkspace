#!/usr/bin/env bash
# Smoke test for rag_gate.sh precedence order
# Tests: env > .gate > defaults

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
GT_FILE="$PROJECT_DIR/.reports/day62/ground_truth_clean.tsv"

echo "=== Testing rag_gate.sh precedence order ==="

# Test 1: .gate only (should use .gate values)
echo "Test 1: .gate only"
output1="$(bash "$PROJECT_DIR/scripts/rag_gate.sh" "$GT_FILE" 2>&1 | head -1 || true)"
echo "Output: $output1"
if echo "$output1" | grep -q "THRESH_P=0.30"; then
  echo "✅ PASS: .gate THRESH_P=0.30 applied"
else
  echo "❌ FAIL: Expected THRESH_P=0.30"
  exit 1
fi

# Test 2: ENV overrides .gate
echo -e "\nTest 2: ENV overrides .gate"
output2="$(THRESH_P=0.60 bash "$PROJECT_DIR/scripts/rag_gate.sh" "$GT_FILE" 2>&1 | head -1 || true)"
echo "Output: $output2"
if echo "$output2" | grep -q "THRESH_P=0.60"; then
  echo "✅ PASS: ENV THRESH_P=0.60 overrode .gate"
else
  echo "❌ FAIL: Expected THRESH_P=0.60"
  exit 1
fi

# Test 3: K override
echo -e "\nTest 3: K override"
output3="$(K=5 THRESH_P=0.45 bash "$PROJECT_DIR/scripts/rag_gate.sh" "$GT_FILE" 2>&1 | head -1 || true)"
echo "Output: $output3"
if echo "$output3" | grep -q "K=5.*THRESH_P=0.45"; then
  echo "✅ PASS: Both K=5 and THRESH_P=0.45 applied"
else
  echo "❌ FAIL: Expected K=5 THRESH_P=0.45"
  exit 1
fi

echo -e "\n🎉 All precedence tests passed!"
echo "Precedence order: ENV > .gate > defaults ✅"
