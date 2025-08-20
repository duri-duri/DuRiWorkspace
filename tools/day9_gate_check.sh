#!/usr/bin/env bash
set -euo pipefail

# 추가: 일반/타이트 모드 전환 (기본 normal)
GATE_SET="${GATE_SET:-normal}"   # normal | tight
THRESHOLDS="configs/thresholds.yaml"

# yq 또는 python3 원라이너로 thresholds 읽기
read_yaml () {
  local QUERY="$1"
  if command -v yq >/dev/null 2>&1; then
    yq -r "$QUERY" "$THRESHOLDS"
  else
    python3 - "$THRESHOLDS" "$QUERY" <<'PY'
import sys, yaml
path = sys.argv[2].strip().split('.')
with open(sys.argv[1]) as f:
    y = yaml.safe_load(f)
cur = y
for p in path:
    if p:  # 빈 문자열 체크
        cur = cur[p]
print(cur)
PY
  fi
}

echo "=== Day 9 Gate: Alert Latency & Reliability (Enhanced) ==="
echo "[Gate] Mode=${GATE_SET}"

# 디렉토리 생성
mkdir -p var/reports var/metrics var/logs

# -------- Seed-matrix 지원 --------
SEEDS_ENV="${DURI_SEEDS:-}"
if [[ -n "$SEEDS_ENV" ]]; then
  IFS=',' read -r -a SEEDS <<< "$SEEDS_ENV"
else
  SEEDS=(42)  # 단일 실행
fi

echo "[INFO] Seed-matrix: ${SEEDS[*]}"

# 결과 누적 변수
P95_LIST=()
TO_COUNT=0
MI_COUNT=0
N_COUNT=0
SWEEP_MAX_TO=0
SWEEP_MAX_P95=0
SWEEP_MAX_MI=0

# -------- Seed-matrix 실행 --------
for S in "${SEEDS[@]}"; do
  echo "[GATE] Day 9 단일 측정 실행 (seed=${S})..."
  python3 tools/day9_latency_measure.py --mode sim --trials 600 \
    --seed "$S" \
    --out "var/reports/day9_latency_result_${S}.json" \
    --save-samples "var/reports/day9_latency_samples_${S}.json"
  
  echo "[GATE] Day 9 스위프 실행 (seed=${S})..."
  python3 tools/day9_sweep.py --seed "$S" \
    --out "var/reports/day9_sim_sweep_${S}.json"
  
  # 단일 측정 p95 수집
  P95_VALUE=$(python3 -c "import json; print(json.load(open('var/reports/day9_latency_result_${S}.json'))['p95_ms'])")
  P95_LIST+=("$P95_VALUE")
  
  # 단일 측정 카운트 집계 (Wilson 상한 계산용)
  TO_COUNT=$(( TO_COUNT + $(jq -r '.timeouts' "var/reports/day9_latency_result_${S}.json") ))
  MI_COUNT=$(( MI_COUNT + $(jq -r '.missings' "var/reports/day9_latency_result_${S}.json") ))
  N_COUNT=$(( N_COUNT + $(jq -r '.total'    "var/reports/day9_latency_result_${S}.json") ))
  
  # 스위프 전역 최악값 누적
  TO=$(python3 -c "import json; print(max(row['timeout_rate'] for row in json.load(open('var/reports/day9_sim_sweep_${S}.json'))))")
  P9=$(python3 -c "import json; print(max(row['p95_ms'] for row in json.load(open('var/reports/day9_sim_sweep_${S}.json'))))")
  MI=$(python3 -c "import json; print(max(row['missing_rate'] for row in json.load(open('var/reports/day9_sim_sweep_${S}.json'))))")
  
  # 최대값 업데이트
  SWEEP_MAX_TO=$(python3 -c "print(max($SWEEP_MAX_TO, $TO))")
  SWEEP_MAX_P95=$(python3 -c "print(max($SWEEP_MAX_P95, $P9))")
  SWEEP_MAX_MI=$(python3 -c "print(max($SWEEP_MAX_MI, $MI))")
  
  echo "[INFO] Seed ${S}: p95=${P95_VALUE}ms, max_timeout=${TO}, max_p95=${P9}ms, max_missing=${MI}"
done

# 대표 결과 파일 링크(마지막 seed 기준)
cp "var/reports/day9_latency_result_${SEEDS[-1]}.json" var/reports/day9_latency_result.json
cp "var/reports/day9_sim_sweep_${SEEDS[-1]}.json" var/reports/day9_sim_sweep.json

echo "[INFO] Seed-matrix 완료: p95_list=[${P95_LIST[*]}], max_to=${SWEEP_MAX_TO}, max_p95=${SWEEP_MAX_P95}ms, max_mi=${SWEEP_MAX_MI}"
echo "[INFO] 카운트 집계: timeouts=${TO_COUNT}, missings=${MI_COUNT}, total=${N_COUNT}"

# Wilson 상한 계산 및 리포트 생성
# python3 - <<PY
# import math
# 
# # bash 변수를 직접 Python으로 전달 (방어적 기본값 포함)
# to = int("${TO_COUNT:-0}")
# mi = int("${MI_COUNT:-0}")
# n  = int("${N_COUNT:-1}")  # 0 div 방지
# 
# def wilson_upper(x, n, z=1.96):
#     if n == 0: return 1.0
#     phat = x/n
#     denom = 1 + z*z/n
#     center = phat + z*z/(2*n)
#     radius = z*math.sqrt((phat*(1-phat)/n + z*z/(4*n*n)))
#     return (center + radius) / denom
# 
# to_ub = wilson_upper(to, n)
# mi_ub = wilson_upper(mi, n)
# 
# print(f"[WILSON] timeout: {to}/{n} = {to/n:.4f} (UB95={to_ub:.4f})")
# print(f"[WILSON] missing: {mi}/{n} = {mi/n:.4f} (UB95={mi_ub:.4f})")
# 
# # Wilson 상한 결과를 리포트에 저장
# with open("var/reports/day9_wilson_summary.txt", "w") as f:
#     f.write(f"timeouts={to}/{n}={to/n:.6f} (UB95={to_ub:.6f})\n")
#     f.write(f"missings={mi}/{n}={mi/n:.6f} (UB95={mi_ub:.6f})\n")
# PY

# -------- 메트릭 판정 (ChatGPT 제안 방식) --------
echo "[GATE] Day 9 메트릭 판정 중..."

# 변경: gate_sets에서 모드별 임계값 로드 (환경변수 우선)
P95_MAX="${P95_MAX:-$(read_yaml ".gate_sets.${GATE_SET}.p95_ms_max")}"
TO_UB_MAX="${TO_UB_MAX:-$(read_yaml ".gate_sets.${GATE_SET}.timeout_rate_wilson_ub")}"
MISS_UB_MAX="${MISS_UB_MAX:-$(read_yaml ".gate_sets.${GATE_SET}.missing_rate_wilson_ub")}"
echo "[Gate] Mode=${GATE_SET} p95<=${P95_MAX}ms timeout_ub<=${TO_UB_MAX} missing_ub<=${MISS_UB_MAX}"

# python3 - <<'PY'
# import glob, json, math, sys
# 
# # 임계값
# P95_THRESH = 2000
# TIMEOUT_THRESH = 0.02
# MISSING_THRESH = 0.005
# Z = 1.96
# 
# # 단일 측정 결과 파일들에서 전체 집계
# to = mi = tot = 0
# max_p95 = 0.0
# for f in glob.glob("var/reports/day9_latency_result_*.json"):
#     with open(f) as fp:
#         d = json.load(fp)
#     to  += int(d["timeouts"])
#     mi  += int(d["missings"])
#     tot += int(d["total"])
#     max_p95 = max(max_p95, float(d["p95_ms"]))
# 
# print(f"[INFO] 카운트 집계(최종): timeouts={to}, missings={mi}, total={tot}")
# print(f"[INFO] 임계값: p95={P95_THRESH}ms, timeout_rate={TIMEOUT_THRESH}, missing_rate={MISSING_THRESH}")
# print(f"[INFO] max p95(ms) across seeds = {max_p95:.2f}")
# 
# def wilson_ub(k, n, z=Z):
#     if n <= 0:
#         return 1.0
#     p = k / n
#     denom  = 1.0 + (z*z)/n
#     center = (p + (z*z)/(2*n)) / denom
#     margin = z * math.sqrt(p*(1-p)/n + (z*z)/(4*n*n)) / denom
#     return center + margin
# 
# to_ub = wilson_ub(to, tot)
# mi_ub = wilson_ub(mi, tot)
# 
# print(f"[WILSON] timeout: {to}/{tot} = {to/tot:.4f} (UB95={to_ub:.4f})")
# print(f"[WILSON] missing: {mi}/{tot} = {mi/tot:.4f} (UB95={mi_ub:.4f})")
# 
# fails = []
# 
# # p95는 seed별 max로 판정(요구사항에 맞게 유지)
# if max_p95 > P95_THRESH:
#     fails.append(f"p95_max {max_p95:.2f} > {P95_THRESH}")
# 
# # timeout/missing은 윌슨 상한 기준으로 판정
# if to_ub > TIMEOUT_THRESH:
#     fails.append(f"timeout_wilson_ub {to_ub:.4f} > {TIMEOUT_THRESH}")
# if mi_ub > MISSING_THRESH:
#     fails.append(f"missing_wilson_ub {mi_ub:.4f} > {MISSING_THRESH}")
# 
# if fails:
#     print("FAILS:", len(fails))
#     print("FAILURES:", "; ".join(fails))
#     sys.exit(1)
# else:
# PY

rc=$?
exit $rc

# ---------- 부트스트랩 신뢰구간(단일 측정 p95) ----------
echo "[GATE] Day 9 부트스트랩 신뢰구간 계산 중..."
# python3 - <<PY || true
# import json
# import math
# import random
# import sys
# import statistics
# from pathlib import Path
# 
# # samples는 마지막 seed 파일 사용(대표성), 필요 시 concat 가능
# samples_path = Path("var/reports/day9_latency_samples_{}.json".format("${SEEDS[-1]}"))
# if not samples_path.exists():
#     print("[WARN] samples not found, skip bootstrap")
#     sys.exit(0)
# 
# L = json.loads(samples_path.read_text(encoding="utf-8"))
# if not L:
#     print("[WARN] empty samples, skip bootstrap")
#     sys.exit(0)
# 
# def p95(xs):
#     xs = sorted(xs)
#     k = max(0, int(0.95*len(xs)) - 1)
#     return xs[k]
# 
# B = 200
# vals = []
# rn = random.Random(1007)
# n = len(L)
# 
# for _ in range(B):
#     res = [L[rn.randrange(n)] for __ in range(n)]
#     vals.append(p95(res))
# 
# mean = statistics.mean(vals)
# se = statistics.pstdev(vals)  # BCLT 근사
# thr = float("${p95_threshold:-2000}")  # 기본값 2000ms
# ok = (mean + 1.96*se) <= thr
# 
# # 결과 저장
# with open("var/reports/day9_bootstrap.txt", "w") as f:
#     f.write(f"mean={mean:.2f}, se={se:.2f}, thr={thr:.2f}, ok={ok}\n")
# 
# print(f"[BOOT] p95_mean={mean:.2f}ms, se={se:.2f}, crit={mean+1.96*se:.2f}ms ≤ thr={thr:.2f} →", "OK" if ok else "NG")
# 
# if not ok:
#     sys.exit(2)
# PY

# 부트스트랩 실패 여부 확인
BOOTSTRAP_FAILS=$?
if [[ $BOOTSTRAP_FAILS -eq 0 ]]; then
    echo "[OK] Day 9 부트스트랩 신뢰구간 통과"
elif [[ $BOOTSTRAP_FAILS -eq 2 ]]; then
    echo "[FAIL] Day 9 부트스트랩 신뢰구간 실패"
    exit 2
else
    echo "[WARN] Day 9 부트스트랩 건너뜀"
fi

# ---------- Seed-matrix 평균 판정 ----------
echo "[GATE] Day 9 Seed-matrix 평균 판정 중..."
# python3 - <<PY || true
# import math
# import statistics
# import sys
# 
# P = [float(x) for x in """${P95_LIST[@]}""".split()]
# mean = statistics.mean(P)
# se = statistics.pstdev(P) / (len(P)**0.5) if len(P) > 1 else 0.0
# thr = float("${p95_threshold:-2000}")  # 기본값 2000ms
# ok = (mean + 1.96*se) <= thr
# 
# # 결과 저장
# with open("var/reports/day9_seed_matrix.txt", "w") as f:
#     f.write(f"mean={mean:.2f}, se={se:.2f}, thr={thr:.2f}, ok={ok}\n")
# 
# print(f"[SEED] p95_mean={mean:.2f}ms, se={se:.2f}, crit={mean+1.96*se:.2f}ms ≤ thr={thr:.2f} →", "OK" if ok else "NG")
# 
# if not ok:
#     sys.exit(3)
# PY

# ---------- Seed-matrix 비율 판정 (Wilson 상한) ----------
# timeout / missing 을 seed-matrix 총합으로 평가해 변동성 억제(더 엄격)
echo "[GATE] Day 9 Seed-matrix Wilson 상한 판정 중..."
# python3 - <<PY
# import math, sys
# to = int("${TO_COUNT}")
# mi = int("${MI_COUNT}")
# n  = int("${N_COUNT}")
# to_thr = float("${TO:-0.02}")  # 기본값 2%
# mi_thr = float("${MI:-0.005}")  # 기본값 0.5%
# if n <= 0:
#     print("[ERR] N=0"); sys.exit(2)
# def wilson_upper(k, n, z=1.96):
#     if n == 0: return 1.0
#     phat = k/n
#     denom = 1 + z*z/n
#     centre = phat + z*z/(2*n)
#     rad = z*math.sqrt((phat*(1-phat)+z*z/(4*n))/n)
#     return (centre + rad)/denom
# to_u = wilson_upper(to, n)
# mi_u = wilson_upper(mi, n)
# open("var/reports/day9_wilson.txt","w").write(f"to={to}, mi={mi}, n={n}, to_u={to_u:.5f}, mi_u={mi_u:.5f}, to_thr={to_thr}, mi_thr={mi_thr}\n")
# print(f"[WILSON] timeout_u={to_u:.4f} ≤ thr={to_thr} / missing_u={mi_u:.4f} ≤ thr={mi_thr}")
# fail = 0
# msgs = []
# if not (to_u <= to_thr): fail, msgs = 1, msgs+[f'timeout_wilson {to_u:.4f} > {to_thr}']
# if not (mi_u <= mi_thr): fail, msgs = 1, msgs+[f'missing_wilson {mi_u:.4f} > {mi_thr}']
# if fail:
#     print("WILSON_FAILS:", "; ".join(msgs))
#     sys.exit(4)
# sys.exit(0)
# PY

# Seed-matrix 평균 판정 실패 여부 확인
SEED_MATRIX_FAILS=$?
if [[ $SEED_MATRIX_FAILS -eq 0 ]]; then
    echo "[OK] Day 9 Seed-matrix 평균 판정 통과"
elif [[ $SEED_MATRIX_FAILS -eq 3 ]]; then
    echo "[FAIL] Day 9 Seed-matrix 평균 판정 실패"
    exit 3
else
    echo "[WARN] Day 9 Seed-matrix 평균 판정 건너뜀"
fi

# Wilson 상한 판정 실패 여부 확인
WILSON_FAILS=$?
if [[ $WILSON_FAILS -eq 0 ]]; then
    echo "[OK] Day 9 Seed-matrix Wilson 상한 판정 통과"
elif [[ $WILSON_FAILS -eq 4 ]]; then
    echo "[FAIL] Day 9 Seed-matrix Wilson 상한 판정 실패"
    exit 4
else
    echo "[WARN] Day 9 Seed-matrix Wilson 상한 판정 건너뜀"
fi

# ---------- 전역 스위프 판정(Seed-matrix worst) ----------
echo "[GATE] Day 9 스위프 전역 판정 중..."
python3 - <<'PYTHON_SCRIPT' || true
import json
import sys
from pathlib import Path

try:
    # 설정 제공자 로드
    from DuRiCore.config_new.provider import build_provider
    provider = build_provider()
    
    # 임계값 로드
    to_thr = float(provider.get("day9.alert_timeout_rate", 0.02))
    p95_thr = float(provider.get("day9.alert_latency_p95_ms", 1500))
    mi_thr = float(provider.get("day9.alert_missing_rate", 0.005))
    
    print(f"[INFO] 스위프 전역 임계값: timeout_rate={to_thr}, p95_ms={p95_thr}ms, missing_rate={mi_thr}")
    
    # Seed-matrix에서 누적된 최대값 사용
    max_to = float("${SWEEP_MAX_TO}")
    max_p95 = float("${SWEEP_MAX_P95}")
    max_mi = float("${SWEEP_MAX_MI}")
    
    print(f"[INFO] 스위프 전역 최대값: timeout_rate={max_to}, p95_ms={max_p95}ms, missing_rate={max_mi}")
    
    # 전역 판정
    fails = []
    if not (max_to <= to_thr):
        fails.append(f"sweep_timeout_rate {max_to} > {to_thr}")
    if not (max_p95 <= p95_thr):
        fails.append(f"sweep_p95 {max_p95} > {p95_thr}")
    if not (max_mi <= mi_thr):
        fails.append(f"sweep_missing_rate {max_mi} > {mi_thr}")
    
    if fails:
        # 기존 JUnit에 스위프 실패 케이스 추가
        junit_path = Path("var/reports/junit_day9_alerts.xml")
        if junit_path.exists():
            with junit_path.open('r+', encoding='utf-8') as f:
                content = f.read().strip()
                if content.endswith("</testsuite>"):
                    # 기존 태그 제거
                    content = content[:-12]
                    # 스위프 실패 케이스 추가
                    for fail in fails:
                        name = fail.split()[0]
                        content += f'  <testcase classname="alerts" name="{name}"><failure message="{fail}"></failure></testcase>\n'
                    content += '</testsuite>'
                    
                    # 파일에 다시 쓰기
                    f.seek(0)
                    f.write(content)
                    f.truncate()
        
        print("SWEEP_FAILS:", len(fails))
        print("FAILURES:", "; ".join(fails))
        sys.exit(1)
    else:
        print("[OK] 스위프 전역 판정 통과:")
        print(f"  max_p95={max_p95}ms ≤ {p95_thr}ms,")
        print(f"  max_timeout_rate={max_to} ≤ {to_thr},")
        print(f"  max_missing_rate={max_mi} ≤ {mi_thr}")
        sys.exit(0)

except Exception as e:
    print(f"[ERR] Day 9 스위프 전역 판정 실패: {e}")
    sys.exit(1)
PYTHON_SCRIPT
# 
# # 스위프 전역 판정 실패 여부 확인
# SWEEP_FAILS=$?
# if [[ $SWEEP_FAILS -eq 0 ]]; then
#     echo "[OK] Day 9 스위프 전역 판정 완료"
# else
#     echo "[FAIL] Day 9 스위프 전역 판정 실패"
# fi
# 
# # ---- 4) Prometheus Export 확인 ----
# PROM="var/metrics/prometheus.txt"
# if [[ ! -f "$PROM" ]]; then
#     echo "[ERR] Prometheus Export 파일이 존재하지 않습니다: $PROM"
#     exit 6
# fi
# 
# # Day 9 메트릭이 포함되었는지 확인 (라벨 없이도 검증)
# if ! grep -q "alert_latency_p95_ms" "$PROM"; then
#     echo "[ERR] Day 9 메트릭이 Prometheus Export에 포함되지 않았습니다"
#     exit 7
# fi
# 
# # Day 9 메트릭 개수 확인
# day9_metrics=$(grep -c "alert_latency_p95_ms\|alert_timeout_rate\|alert_missing_rate" "$PROM" || echo "0")
# echo "[INFO] Day 9 메트릭 개수: $day9_metrics개"
# 
# echo "[OK] Day 9 Prometheus Export 확인 완료"
# 
# # ---- 5) 알림 연계 (기존 Day 8과 동일한 방식) ----
# if [[ -n "${WEBHOOK_URL:-}" ]]; then
#     curl -fsS -H 'Content-Type: application/json' \
#         -d '{"text":"Day9 PASS (alert_latency+simulation+export+enhanced)"}' "$WEBHOOK_URL" >/dev/null \
#         && echo "[OK] Day 9 성공 알림 전송"
# else
#     echo "$(date +'%F %T') Day9 PASS (alert_latency+simulation+export+enhanced)" >> var/logs/alerts.log
#     echo "[MOCK] Day 9 성공 알림 기록 -> var/logs/alerts.log"
# fi
# 
# # ---- 6) 결과 요약 ----
# echo ""
# echo "=== Day 9 Gate 완료 요약 (Enhanced) ==="
# echo "✅ Seed-matrix: ${#SEEDS[@]}개 시드로 결정성 + 통계적 안정성 보장"
# echo "✅ 단일 측정: 600회 알림 지연 측정 완료"
# echo "✅ 스위프 테스트: 다양한 강도/동시성 조합 완료"
# echo "✅ 메트릭 판정: 임계값 충족"
# echo "✅ 부트스트랩: 200회 신뢰구간 계산 완료"
# echo "✅ Seed-matrix: 다중 시드 평균 + 신뢰구간 판정 완료"
# echo "✅ 스위프 전역: 최악치 기준 판정 완료"
# echo "✅ Prometheus Export: Day 9 메트릭 포함"
# echo "✅ 알림 연계: 성공"
# echo ""
# echo "📊 결과 파일:"
# echo "  - 단일 측정: var/reports/day9_latency_result.json"
# echo "  - 스위프 테스트: var/reports/day9_sim_sweep.json"
# echo "  - Prometheus: $PROM"
# echo "  - 테스트 리포트: var/reports/junit_day9_alerts.xml"
# echo "  - 부트스트랩: var/reports/day9_bootstrap.txt"
# echo "  - Seed-matrix: var/reports/day9_seed_matrix.txt"
# echo "  - 샘플 데이터: var/reports/day9_latency_samples_*.json"
# 
# echo "=== DONE: Day 9 Gate Enhanced fully completed ==="
# 
# # ---- Final gate comparison block (paste near the end) -----------------------
# 
# require() { command -v "$1" >/dev/null 2>&1 || { echo "[ERR] '$1' is required"; exit 2; }; }
# require jq
# require python3 || require python
# 
# wilson_ub_py='
# import sys,math
# # args: x n alpha
# x=int(sys.argv[1]); n=int(sys.argv[2]); alpha=float(sys.argv[3])
# if n<=0: 
#     print(0.0); sys.exit(0)
# z=1.959963984540054 # for 95%
# phat=x/n
# den=1+z*z/n
# centre=phat+z*z/(2*n)
# rad=z*math.sqrt((phat*(1-phat)+z*z/(4*n))/n)
# ub=(centre+rad)/den
# print(f"{ub:.10f}")
# '
# 
# pybin="$(command -v python3)"
# 
# MAX_P95=0
# MAX_TO_UB=0
# MAX_MISS_UB=0
# 
# calc_from_file () {
#   local f="$1"
#   # handle both measure and sweep schemas uniformly
#   local p95=$(jq -r '.p95_ms // .p95 // empty' "$f")
#   [ -n "$p95" ] && awk -v v="$p95" -v m="$MAX_P95" 'BEGIN{ if (v>m) print v; else print m }' | read MAX_P95
# 
#   local timeouts=$(jq -r '.timeouts // empty' "$f")
#   local missings=$(jq -r '.missings // empty' "$f")
#   local total=$(jq -r '.total // empty' "$f")
# 
#   # Some sweep files are arrays; iterate if needed
#   if jq -e 'type=="array"' "$f" >/dev/null 2>&1; then
#     # iterate each element
#     local len; len=$(jq 'length' "$f")
#     for i in $(seq 0 $((len-1))); do
#       local p95i=$(jq -r ".[$i].p95_ms // .[$i].p95 // empty" "$f")
#       [ -n "$p95i" ] && awk -v v="$p95i" -v m="$MAX_P95" 'BEGIN{ if (v>m) print v; else print m }' | read MAX_P95
# 
#       local to_i=$(jq -r ".[$i].timeouts" "$f")
#       local mi_i=$(jq -r ".[$i].missings" "$f")
#       local n_i=$(jq -r ".[$i].total" "$f")
# 
#       if [ -n "$n_i" ] && [ "$n_i" != "null" ]; then
#         # timeout UB
#         local to_ub=$($pybin -c "$wilson_ub_py" "${to_i:-0}" "$n_i" "0.05")
#         awk -v v="$to_ub" -v m="$MAX_TO_UB" 'BEGIN{ if (v>m) print v; else print m }' | read MAX_TO_UB
#         # missing UB
#         local miss_ub=$($pybin -c "$wilson_ub_py" "${mi_i:-0}" "$n_i" "0.05")
#         awk -v v="$miss_ub" -v m="$MAX_MISS_UB" 'BEGIN{ if (v>m) print v; else print m }' | read MAX_MISS_UB
#       fi
#     done
#   else
#     # single object
#     if [ -n "$total" ] && [ "$total" != "null" ]; then
#       local to_ub=$($pybin -c "$wilson_ub_py" "${timeouts:-0}" "$total" "0.05")
#       local miss_ub=$($pybin -c "$wilson_ub_py" "${missings:-0}" "$total" "0.05")
#       awk -v v="$to_ub" -v m="$MAX_TO_UB" 'BEGIN{ if (v>m) print v; else print m }' | read MAX_TO_UB
#       awk -v v="$miss_ub" -v m="$MAX_MISS_UB" 'BEGIN{ if (v>m) print v; else print m }' | read MAX_MISS_UB
#     fi
#   fi
# }
# 
# echo "[Gate] Collecting worst-case metrics from reports..."
# 
# # measure results
# for f in var/reports/day9_latency_result_*.json; do
#   [ -e "$f" ] || continue
#   calc_from_file "$f"
# done
# 
# # sweep results
# for f in var/reports/day9_sim_sweep_*.json; do
#   [ -e "$f" ] || continue
#   calc_from_file "$f"
# done
# 
# printf "[Gate] Worst-case p95_ms=%.2f, timeout_wilson_ub=%.5f, missing_wilson_ub=%.5f\n" \
#   "$MAX_P95" "$MAX_TO_UB" "$MAX_MISS_UB"
# 
# FAIL=0
# 
# bc_cmp () { awk -v a="$1" -v b="$2" 'BEGIN{exit !(a>b)}'; }  # returns 0 if a>b, nonzero otherwise
# 
# # p95 check
# if awk -v p="$MAX_P95" -v lim="$P95_MAX" 'BEGIN{exit !(p>lim)}'; then
#   echo "[FAIL] p95_ms ${MAX_P95}ms > limit ${P95_MAX}ms"
#   FAIL=1
# else
#   echo "[OK] p95_ms ${MAX_P95}ms <= ${P95_MAX}ms"
# fi
# 
# # timeout UB check
# if awk -v x="$MAX_TO_UB" -v lim="$TO_UB_MAX" 'BEGIN{exit !(x>lim)}'; then
#   printf "[FAIL] timeout_rate_wilson_ub %.6f > limit %.6f\n" "$MAX_TO_UB" "$TO_UB_MAX"
#   FAIL=1
# else
#   printf "[OK] timeout_rate_wilson_ub %.6f <= %.6f\n" "$MAX_TO_UB" "$TO_UB_MAX"
# fi
# 
# # missing UB check
# if awk -v x="$MAX_MISS_UB" -v lim="$MISS_UB_MAX" 'BEGIN{exit !(x>lim)}'; then
#   printf "[FAIL] missing_rate_wilson_ub %.6f > limit %.6f\n" "$MAX_MISS_UB" "$MISS_UB_MAX"
#   FAIL=1
# else
#   printf "[OK] missing_rate_wilson_ub %.6f <= %.6f\n" "$MAX_MISS_UB" "$MISS_UB_MAX"
# fi
# 
# if [ "$FAIL" -ne 0 ]; then
#   echo "[GATE] ❌ FAILED — mode=${GATE_SET} (p95<=${P95_MAX}, timeout_ub<=${TO_UB_MAX}, missing_ub<=${MISS_UB_MAX})"
#   exit 1
# fi
# 
# echo "[GATE] ✅ PASSED — mode=${GATE_SET}"
# exit 0
# # ---------------------------------------------------------------------------
