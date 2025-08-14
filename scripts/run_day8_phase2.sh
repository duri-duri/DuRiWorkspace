#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$(pwd)}"
cd "$ROOT"

echo "==[Day8 Phase2 | SLO Gate + Prom Export + Alert]=="

# 0) 환경 가드(테스트 오염 방지)
export PYTHONWARNINGS=ignore
export DURI_ENV="ci-day8-slo"
export DURI_TEST_ISOLATION=1
export DURI_DISABLE_NOISY_PRINTS=1

# 1) SLO Gate 단독 실행 (junit xml 저장)
mkdir -p var/reports var/metrics var/logs
pytest -q tests/test_day8_slo_gate.py \
  --disable-warnings \
  --maxfail=1 \
  --junitxml=var/reports/junit_day8_slo.xml

echo "[OK] pytest: test_day8_slo_gate PASSED"

# 2) Prometheus 텍스트 파일 존재/기본 메트릭 검증
PROM="var/metrics/prometheus.txt"
test -f "$PROM" || { echo "[ERR] prometheus.txt 미생성"; exit 2; }

echo "[OK] prometheus.txt 생성 확인 → $PROM"

# 2-1) 핵심 메트릭 키 최소셋 점검 (이름은 귀하 환경에 맞춰 3개 패턴 중 하나라도 잡히게 구성)
REQ_LAT=$(grep -E '(_p95|request_latency_p95|latency_ms_p95)' "$PROM" || true)
SUCC_RT=$(grep -E '(success_rate|availability|req_success_ratio|pass_rate)' "$PROM" || true)
MEMORY=$(grep -E '(memory_mb|rss_mb|heap_used_mb)' "$PROM" || true)

[[ -n "$REQ_LAT" ]] || { echo "[ERR] p95 지연 메트릭 패턴 미검출"; exit 3; }
[[ -n "$SUCC_RT" ]] || { echo "[ERR] 성공률/가용성 메트릭 패턴 미검출"; exit 3; }
[[ -n "$MEMORY" ]] || { echo "[ERR] 메모리 메트릭 패턴 미검출"; exit 3; }

echo "[OK] 핵심 메트릭 키 검출 완료"

# 3) SLO 임계값 평가 (파일 내 값 파싱; 기본 패턴 두 가지 지원)
python3 - <<'PY'
import re, sys, json
path = "var/metrics/prometheus.txt"
txt = open(path, "r", encoding="utf-8").read()

def find_num(patterns):
    for p in patterns:
        m = re.search(p, txt, re.M)
        if m: 
            try: return float(m.group(1))
            except: pass
    return None

# 환경별로 이름 상이할 수 있어 패턴 다중 지원
p95 = find_num([
    r"latency_ms_p95\{.*\}\s+([0-9.]+)",
    r"request_latency_p95\s+([0-9.]+)",
    r"_p95\{.*\}\s+([0-9.]+)",
    r"latency_ms_p95\s+([0-9.]+)",
])

succ = find_num([
    r"success_rate\{.*\}\s+([0-9.]+)",
    r"availability\{.*\}\s+([0-9.]+)",
    r"req_success_ratio\{.*\}\s+([0-9.]+)",
    r"pass_rate\s+([0-9.]+)",
])

mem = find_num([
    r"memory_mb\{.*\}\s+([0-9.]+)",
    r"rss_mb\{.*\}\s+([0-9.]+)",
    r"heap_used_mb\{.*\}\s+([0-9.]+)",
    r"memory_mb_p95\s+([0-9.]+)",
])

# 기본 임계(귀하가 Day7에서 정한 값과 일치/보수적으로 세팅)
# sys.argv 안전 처리
P95_MAX   = 120.0     # ms (Day8 설정 기준)
SUCC_MIN  = 0.95      # ratio (0~1)
MEM_MAX   = 200.0     # MB (Day8 설정 기준)

vals = {"p95_ms": p95, "success_rate": succ, "memory_mb": mem}
if None in vals.values():
    print("[ERR] SLO 평가에 필요한 값 중 None 존재:", vals); sys.exit(4)

viol = []
if p95 > P95_MAX:   viol.append(f"p95 {p95:.2f}ms > {P95_MAX}ms")
if succ < SUCC_MIN: viol.append(f"success {succ:.3f} < {SUCC_MIN}")
if mem  > MEM_MAX:  viol.append(f"mem {mem:.1f}MB > {MEM_MAX}MB")

print(json.dumps({"metrics": vals, "thresholds": {"p95_ms_max": P95_MAX, "success_min": SUCC_MIN, "mem_mb_max": MEM_MAX}, "violations": viol}, ensure_ascii=False))

if viol:
    print("[SLO-FAIL]", "; ".join(viol)); sys.exit(5)
else:
    print("[SLO-PASS] 모든 임계 충족")
PY

echo "[OK] SLO 임계 통과 평가 완료"

# 4) 알림 연계 (실환경/모의 모두 지원)
# 우선순위: scripts/notify_slo_ok.sh → scripts/notify_on_slo_violation.sh → WEBHOOK_URL 직접 호출 → 모의 로그
if [[ -x scripts/notify_slo_ok.sh ]]; then
  scripts/notify_slo_ok.sh "Day8 Phase2 SLO PASS"
  echo "[OK] notify_slo_ok.sh 호출"
elif [[ -x scripts/notify_on_slo_violation.sh ]]; then
  scripts/notify_on_slo_violation.sh --close "Day8 Phase2 SLO PASS (해제)"
  echo "[OK] notify_on_slo_violation.sh 해제호출"
elif [[ -n "${WEBHOOK_URL:-}" ]]; then
  curl -fsS -X POST "$WEBHOOK_URL" -H 'Content-Type: application/json' \
    -d '{"text":"Day8 Phase2 SLO PASS: 임계 충족 및 prometheus.txt 검증 완료"}' >/dev/null && echo "[OK] WEBHOOK 전송"
else
  echo "[MOCK] 알림 훅 없음 → var/logs/alerts.log에 기록"
  echo "$(date +'%F %T') SLO PASS Day8-Phase2" >> var/logs/alerts.log
fi

# 5) 아티팩트 요약
echo "==[Artifacts]=="
echo "  - var/reports/junit_day8_slo.xml"
echo "  - var/metrics/prometheus.txt"
echo "  - var/logs/alerts.log (모의일 때만)"

echo "==[DONE] Day8 Phase2 완료"
