#!/usr/bin/env bash
# scripts/day21_risk_loop.sh
# 벤치(실제) → 설정 반영 → 회귀 → risk_checks → runner → (선택) 모델카드
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

fail(){ echo "[ERR]" "$*" >&2; exit 1; }
info(){ echo "[INFO]" "$*"; }
ok(){ echo "[OK]" "$*"; }

# 필수 도구
command -v jq >/dev/null || fail "jq 필요"
command -v python3 >/dev/null || fail "python3 필요"
[[ -x "tools/run_trace_bench.sh" ]] || fail "tools/run_trace_bench.sh 실행권한 필요"
[[ -x "tools/apply_trace_config.sh" ]] || fail "tools/apply_trace_config.sh 실행권한 필요"
[[ -f "configs/trace_v2_selected.json" ]] || fail "configs/trace_v2_selected.json 없음"

# 0) 실벤치 검증(더미 금지)
if [[ -x "ci/ensure_real_bench.sh" ]]; then
  bash ci/ensure_real_bench.sh || fail "실벤치 CI 가드 실패"
else
  info "CI 가드 없음: run_trace_bench.sh의 자체 검증 로직에 의존"
fi

# 1) 선택 구성 로드
sampling="$(jq -r '.sampling_rate' configs/trace_v2_selected.json)"
ser="$(jq -r '.serialization' configs/trace_v2_selected.json)"
comp="$(jq -r '.compression' configs/trace_v2_selected.json)"
info "선택 구성: sampling=$sampling, ser=$ser, comp=$comp"

# 2) 스모크 벤치 (실벤치)
SMOKE_OUT="auto_code_loop_beta/logs/trace_smoke.json"
mkdir -p "auto_code_loop_beta/logs"
bash tools/run_trace_bench.sh --sampling "$sampling" --ser "$ser" --comp "$comp" --out "$SMOKE_OUT"
ok "스모크 결과: $SMOKE_OUT"
jq . "$SMOKE_OUT" || true

# 3) SLO 검증 (eval/metrics.yaml → weight/제약, slo_sla_dashboard_v1/metrics.json → baseline)
#    yq가 없을 수 있어 파이썬으로 YAML 파싱
PYCONF="$(cat <<'PY'
import json, sys, yaml, pathlib
root = pathlib.Path(".")
eval_yaml = root/"eval/metrics.yaml"
slo_json = root/"slo_sla_dashboard_v1/metrics.json"

# 기본값
weights = {"overhead":0.6,"error":0.3,"size":0.1}
max_over=5.0
max_err=0.5
base_p95=750.0
base_size=100.0

try:
    y = yaml.safe_load(eval_yaml.read_text(encoding="utf-8"))
    t = (((y or {}).get("trace_v2") or {}).get("tuning") or {})
    w = t.get("weight") or {}
    weights["overhead"] = float(w.get("overhead", weights["overhead"]))
    weights["error"]    = float(w.get("error",    weights["error"]))
    weights["size"]     = float(w.get("size",     weights["size"]))
    max_over = float(t.get("max_overhead_pct", max_over))
    max_err  = float(t.get("max_error_rate", max_err)) * 100  # 0.005 -> 0.5%
except Exception as e:
    pass

try:
    s = json.loads(slo_json.read_text(encoding="utf-8"))
    base_p95 = float(s.get("baseline_p95_ms", s.get("p95_ms", base_p95)))
    base_size = float(s.get("baseline_size_kb", 100.0))
except Exception:
    pass

print(json.dumps({"weights":weights,"max_overhead_pct":max_over,"max_error_rate_pct":max_err,
                  "baseline_p95_ms":base_p95,"baseline_size_kb":base_size}))
PY
)"
CONF_JSON="$(python3 -c "$PYCONF")"
echo "$CONF_JSON" | jq . >&2

BASE_P95="$(echo "$CONF_JSON" | jq -r '.baseline_p95_ms')"
MAX_OVER="$(echo "$CONF_JSON" | jq -r '.max_overhead_pct')"
MAX_ERR="$(echo "$CONF_JSON" | jq -r '.max_error_rate_pct')"

# 스모크 검증
over_pct="$(jq --argjson B "$BASE_P95" '((.p95_ms - $B)/$B)*100' "$SMOKE_OUT")"
err_pct="$(jq '.error_rate*100' "$SMOKE_OUT")"
awk "BEGIN{ exit !($over_pct <= $MAX_OVER) }" || fail "SLO 실패: overhead ${over_pct}% > ${MAX_OVER}%"
awk "BEGIN{ exit !($err_pct  <= $MAX_ERR) }"   || fail "SLO 실패: error ${err_pct}% > ${MAX_ERR}%"
ok "스모크 SLO 통과: overhead=${over_pct}%, error=${err_pct}% (한계: ${MAX_OVER}%, ${MAX_ERR}%)"

# 4) 설정 적용(서비스 설정/런타임 반영)
tools/apply_trace_config.sh
ok "설정 반영 완료"

# 5) 회귀 테스트 → 리스크 평가 → 승격 판단
pushd auto_code_loop_beta >/dev/null
  bash gates/run_regression_tests.sh
  python3 gates/risk_checks.py --in logs/test_result.json --out logs/risk.json
  RUN_OUT="$(python3 runner.py)"
popd >/dev/null

echo "$RUN_OUT" | jq . || true
PROMOTE="$(echo "$RUN_OUT" | jq -r '.promote // false')"
if [[ "$PROMOTE" == "true" ]]; then
  ok "승격 조건 충족. pass_rate=$(echo "$RUN_OUT" | jq -r '.pass_rate // .tests.pass_rate // "N/A"')"
else
  info "승격 보류: $(echo "$RUN_OUT" | jq -r '.reason // "unknown"')"
  exit 2
fi

# 6) (선택) 모델카드 자동 갱신
if [[ -f "model_card_autofill.py" && -f "model_card_template.md" ]]; then
  python3 model_card_autofill.py --template model_card_template.md --out model_card_v1.autofilled.md --strict || true
  ok "모델카드 갱신 시도 완료 (strict)"
else
  info "모델카드 템플릿/스크립트 미존재: 갱신 생략"
fi

# --- domain hooks (optional, default: off) ---
if [[ "${POU_REHAB_HOOK:-0}" = "1" && -f auto_code_loop_beta/gates/rehab_objective_eval.py ]]; then
  auto_code_loop_beta/gates/rehab_objective_eval.py \
    --objective configs/objective_rehab.yaml \
    --rules auto_code_loop_beta/gates/risk_checks_rehab_protocol.yaml \
    --infile cases/rehab/examples.jsonl \
    --out auto_code_loop_beta/logs/rehab_objective_report.json || true
fi

ok "Day 21 risk loop 완료"
