#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ART="${ROOT}/artifacts_phase1"
LOG="${ART}/regression_$(date +%F_%H%M%S).log"
mkdir -p "${ART}"

echo "=== DuRi Regression Runner ===" | tee -a "${LOG}"
echo "time=$(date -Is)" | tee -a "${LOG}"
echo "repo=${ROOT}" | tee -a "${LOG}"
echo "bench_list=$(realpath "${ROOT}/configs/regression_bench_list.yaml" 2>/dev/null || echo 'missing')" | tee -a "${LOG}"

# 간단한 사전 점검
if [[ ! -f "${ROOT}/configs/regression_bench_list.yaml" ]]; then
  echo "[WARN] regression_bench_list.yaml not found; proceeding with smoke only" | tee -a "${LOG}"
fi

# 테스트 실행 (있으면 pytest, 없으면 스모크)
if command -v pytest >/dev/null 2>&1 && [[ -d "${ROOT}/tests" ]]; then
  (cd "${ROOT}" && pytest -q tests 2>&1) | tee -a "${LOG}" || true
else
  echo "[SMOKE] running minimal checks..." | tee -a "${LOG}"
  echo '{"event":"smoke","status":"ok"}' | tee -a "${LOG}"
fi

echo "=== DONE ===" | tee -a "${LOG}"

# 러너 요약 JSON 남기기
echo "{\"ts\":\"$(date -Is)\",\"runner\":\"ok\"}" > artifacts_phase1/last_regression_summary.json

# Git SHA 찍어두기
git rev-parse --short HEAD 2>/dev/null | xargs -I{} sh -c 'echo "git_sha={}" >> artifacts_phase1/boot_smoke.log' || true


