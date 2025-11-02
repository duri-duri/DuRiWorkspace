#!/usr/bin/env bash
# Gate Check: gates.yml과 doctor.sh 출력을 합쳐 pass/fail 판정
set -euo pipefail

cd "$(dirname "$0")/.."

# doctor.sh 실행
DOCTOR_OUTPUT=$(bash scripts/doctor.sh 2>&1)
DOCTOR_EXIT=$?

echo "$DOCTOR_OUTPUT"
echo ""
echo "=== Gate Check ==="

# gates.yml 파싱 (간단한 yaml 파서)
GATES_YML="${GATES_YML:-gates.yml}"

# EV velocity 체크
EV_VEL=$(echo "$DOCTOR_OUTPUT" | grep "EV_velocity(h):" | awk '{print $2}' || echo "0")
EV_WARN=$(grep -A 5 "ev_velocity_per_hour:" "$GATES_YML" 2>/dev/null | grep "warn:" | awk '{print $2}' || echo "2.5")
EV_PASS=$(grep -A 5 "ev_velocity_per_hour:" "$GATES_YML" 2>/dev/null | grep "pass:" | awk '{print $2}' || echo "4.0")

if (( $(echo "$EV_VEL < $EV_PASS" | bc -l 2>/dev/null || echo "1") )); then
  if (( $(echo "$EV_VEL < $EV_WARN" | bc -l 2>/dev/null || echo "1") )); then
    echo "[FAIL] EV velocity: $EV_VEL < $EV_WARN (warning threshold)"
    GATE_FAIL=1
  else
    echo "[WARN] EV velocity: $EV_VEL < $EV_PASS (pass threshold)"
  fi
else
  echo "[PASS] EV velocity: $EV_VEL ≥ $EV_PASS"
fi

# AB p-value 분산 체크
AB_SAMPLES=$(echo "$DOCTOR_OUTPUT" | grep "AB_p_samples:" | awk '{print $2}' | cut -d, -f1 || echo "0")
AB_UNIQUE=$(echo "$DOCTOR_OUTPUT" | grep "AB_p_samples:" | awk '{print $4}' || echo "0")

if [ "${AB_SAMPLES:-0}" -lt 10 ]; then
  echo "[FAIL] AB samples: $AB_SAMPLES < 10 (min_samples)"
  GATE_FAIL=1
elif [ "${AB_UNIQUE:-0}" -le 1 ]; then
  echo "[FAIL] AB p-value variance: unique=$AB_UNIQUE (require_variance=true)"
  GATE_FAIL=1
else
  echo "[PASS] AB p-value variance: samples=$AB_SAMPLES, unique=$AB_UNIQUE"
fi

# Shadow epoch 체크
EPOCH_P95=$(echo "$DOCTOR_OUTPUT" | grep "p95:" | awk '{print $2}' | sed 's/s$//' || echo "9999")
EPOCH_P95_THRESHOLD=$(grep -A 3 "shadow_epoch_seconds:" "$GATES_YML" 2>/dev/null | grep "p95:" | awk '{print $2}' || echo "720")

if [ "${EPOCH_P95:-9999}" -gt "$EPOCH_P95_THRESHOLD" ]; then
  echo "[WARN] Shadow epoch p95: ${EPOCH_P95}s > ${EPOCH_P95_THRESHOLD}s"
else
  echo "[PASS] Shadow epoch p95: ${EPOCH_P95}s ≤ ${EPOCH_P95_THRESHOLD}s"
fi

# DB 일관성 체크
if echo "$DOCTOR_OUTPUT" | grep -q "\[OK\] DB:"; then
  echo "[PASS] DB consistency"
else
  echo "[FAIL] DB consistency"
  GATE_FAIL=1
fi

# 메트릭 엔드포인트 체크
if echo "$DOCTOR_OUTPUT" | grep -q "\[OK\] 메트릭 엔드포인트"; then
  echo "[PASS] Metrics endpoint"
else
  echo "[WARN] Metrics endpoint"
fi

# 파일럿 프로세스 체크
if echo "$DOCTOR_OUTPUT" | grep -q "\[OK\] 파일럿/워커 프로세스"; then
  echo "[PASS] Pilot process"
else
  echo "[WARN] Pilot process"
fi

# 최근 EV 생성 시간 체크
LAST_EV_AGE=$(echo "$DOCTOR_OUTPUT" | grep "생성 시간:" | awk '{print $3}' | sed 's/s$//' || echo "9999")
LAST_EV_WARN=$(grep -A 3 "last_ev_age:" "$GATES_YML" 2>/dev/null | grep "warn_seconds:" | awk '{print $2}' || echo "3600")
LAST_EV_FAIL=$(grep -A 3 "last_ev_age:" "$GATES_YML" 2>/dev/null | grep "fail_seconds:" | awk '{print $2}' || echo "7200")

if [ "${LAST_EV_AGE:-9999}" -gt "$LAST_EV_FAIL" ]; then
  echo "[FAIL] Last EV age: ${LAST_EV_AGE}s > ${LAST_EV_FAIL}s"
  GATE_FAIL=1
elif [ "${LAST_EV_AGE:-9999}" -gt "$LAST_EV_WARN" ]; then
  echo "[WARN] Last EV age: ${LAST_EV_AGE}s > ${LAST_EV_WARN}s"
else
  echo "[PASS] Last EV age: ${LAST_EV_AGE}s ≤ ${LAST_EV_WARN}s"
fi

echo ""
if [ "${GATE_FAIL:-0}" -eq 1 ]; then
  echo "=== Gate Check: FAIL ==="
  echo "[ACTION] Fix instructions printed above. See cursor-tasks.md for task suggestions."
  exit 1
else
  echo "=== Gate Check: PASS ==="
  exit 0
fi

